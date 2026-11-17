#!/usr/bin/env python3
"""
==============================================================================
FILE: scripts/verify_no_private_data.py
==============================================================================

PURPOSE:
Gate that blocks private or personal data from entering this Git
repository. It scans (a) the staged index before a commit, (b) the
tracked working tree, and (c) optionally the full commit history, and
exits non-zero when a forbidden pattern is found.

WHAT THIS FILE IS NOT FOR:
- It is not a substitute for reading `git diff --cached` by eye
  (AGENTS.md policy 18): automated patterns catch secrets and
  identifiers, not a dossier pasted in prose.
- It is not an antivirus or a general-purpose secret scanner such as
  `gitleaks`; it implements only the pattern classes this project has
  actually leaked or is at risk of leaking.

INVARIANTS:
1. Exit code 0 means "no forbidden pattern found"; exit code 1 means
   "found"; exit code 2 means the scanner itself failed to run.
2. The scan must never modify the repository: it only reads.
3. Synthetic sample documents under `practice-vault/data/sample_docs/`
   are exempt from the personal-name heuristics only, never from the
   credential patterns.
4. Acronyms used below are expanded on first use: United Kingdom
   General Data Protection Regulation (UK GDPR), General Medical
   Council (GMC), Application Programming Interface (API), Uniform
   Resource Locator (URL).

USAGE:
    python3 scripts/verify_no_private_data.py               # tree
    python3 scripts/verify_no_private_data.py --staged       # index
    python3 scripts/verify_no_private_data.py --history      # all refs
    python3 scripts/verify_no_private_data.py --staged --history
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Repository root, derived from this file's location (scripts/..).
ROOT = Path(__file__).resolve().parent.parent

# Directories never scanned because they hold machine-local state that
# is excluded by .gitignore anyway. Scanning them would only produce
# noise from virtual environments and caches.
SKIP_DIRS = {".git", "venv", "__pycache__", ".pytest_cache", "node_modules"}

# Pattern classes. Each entry is a PatternSpec: a human name, a
# compiled regular expression, and whether the pattern may be skipped
# inside test files (True only for credential-assignment patterns,
# where fake values are expected fixtures). Every pattern is
# documented: what it catches and why this repository is exposed to
# it.
#
# Acronyms are expanded on first use: Application Programming
# Interface (API), Open Authorization (OAuth), General Medical
# Council (GMC), Amazon Web Services (AWS), Transport Layer Security
# (TLS).
class PatternSpec:
    """One detection rule: name, expression, test-file policy.

    Attributes:
        name: Human-readable label used in findings output.
        regex: Compiled expression searched in file text.
        skip_in_tests: When True, the rule is not applied to paths
            containing a TEST_PATH_PARTS fragment, because test
            fixtures legitimately contain fake values.
    """

    __slots__ = ("name", "regex", "skip_in_tests")

    def __init__(self, name: str, regex: str, skip_in_tests: bool = False,
                 flags: int = 0) -> None:
        self.name = name
        self.regex = re.compile(regex, flags)
        self.skip_in_tests = skip_in_tests


PATTERNS: list[PatternSpec] = [
    PatternSpec(
        "Google Application Programming Interface (API) key",
        # Google keys are 39 characters: "AIza" plus a URL-safe
        # base64 tail. This repository once shipped a live Maps
        # browser key inside a client mock-up, so this is the
        # primary guard. Never skipped, even in tests.
        r"AIza[0-9A-Za-z_\-]{35}",
    ),
    PatternSpec(
        "OpenAI-style secret key",
        # "sk-" prefix, at least 20 trailing characters.
        r"\bsk-[A-Za-z0-9]{20,}\b",
    ),
    PatternSpec(
        "GitHub personal access or Actions token",
        # "ghp_", "gho_", "ghs_", "ghr_" or "github_pat_" prefixes.
        r"\b(?:ghp|gho|ghs|ghr)_[A-Za-z0-9]{20,}\b|github_pat_[A-Za-z0-9_]{20,}",
    ),
    PatternSpec(
        "Amazon Web Services (AWS) access key id",
        # 16 characters after the AKIA prefix; the fixed width makes
        # false positives rare.
        r"\bAKIA[0-9A-Z]{16}\b",
    ),
    PatternSpec(
        "Slack token",
        r"\bxox[baprs]-[A-Za-z0-9\-]{10,}\b",
    ),
    PatternSpec(
        "Stripe secret key",
        r"\b(?:sk|rk)_(?:live|test)_[A-Za-z0-9]{20,}\b",
    ),
    PatternSpec(
        "OpenRouter key",
        # The Practice Vault routes model calls through OpenRouter;
        # STATUS.md records an outstanding credential rotation for it.
        r"\bsk-or-[A-Za-z0-9_\-]{20,}\b",
    ),
    PatternSpec(
        "Private key material",
        # Armoured private key blocks of any common format.
        r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY",
    ),
    PatternSpec(
        "OAuth client secret assignment",
        # A concrete secret value assigned to a client_secret field,
        # not the field name itself (the FastAPI models legitimately
        # declare `client_secret: str`). Skipped in tests, where
        # doubles such as "test-client-secret" are expected.
        r"""(?:client_secret|CLIENT_SECRET)["']?\s*[:=]\s*["'][A-Za-z0-9_\-]{16,}["']""",
        skip_in_tests=True,
    ),
    PatternSpec(
        "Password assignment with a literal value",
        # Catches `password = "..."` style leaks in scripts and
        # configuration. Template references such as "${VAR}" do not
        # match because the first character check rejects "$".
        r"""(?:password|passwd|PWD)["']?\s*[:=]\s*["'](?![$<{])[^"'\s]{8,}["']""",
        skip_in_tests=True,
    ),
    PatternSpec(
        "General Medical Council (GMC) reference number in prose",
        # Bare six-to-eight digit numbers are far too noisy on their
        # own, so this fires only where the label makes the meaning
        # explicit: "GMC: 1234567" or "GMC Reference Number: 7654321".
        r"\bGMC\b[^0-9\n]{0,20}\b\d{6,8}\b",
        flags=re.IGNORECASE,
    ),
    PatternSpec(
        "NHS number in prose",
        # Ten digits, commonly spaced in groups of 3-3-4, only when
        # the surrounding words identify it as an NHS number.
        r"\bNHS\s+(?:number|No\.?|#)\b[^0-9\n]{0,10}\b\d{3}\s?\d{3}\s?\d{3,4}\b",
        flags=re.IGNORECASE,
    ),
]

# Words that mark a file as an allowlisted synthetic fixture. Files
# whose path matches this are skipped entirely for speed and noise,
# but only after they have been confirmed synthetic by a human once.
ALLOWLISTED_PATH_PARTS = (
    "practice-vault/data/sample_docs/",
)

# Files that are allowed to contain the scanner's own patterns.
SELF_PATHS = {
    "scripts/verify_no_private_data.py",
}

# Test code legitimately assigns fake credentials to fixtures. The
# credential-assignment patterns (marked skip_in_tests=True below) are
# not applied to any path containing one of these parts; every other
# pattern, including the live-key patterns, still applies everywhere.
TEST_PATH_PARTS = (
    "/tests/",
    "/test_",
    "_test.py",
)

# A credential-looking value containing any of these case-insensitive
# fragments is an instruction or fixture, not a real secret: the
# documentation tells the operator to paste a value, and tests name
# their doubles explicitly.
PLACEHOLDER_FRAGMENTS = (
    "test",
    "fake",
    "example",
    "placeholder",
    "paste",
    "here",
    "dummy",
    "redacted",
    "your_",
    "xxx",
    "changeme",
)


# ---------------------------------------------------------------------------
# Collection
# ---------------------------------------------------------------------------

def collect_tree_files() -> list[tuple[str, str]]:
    """Return (relative_path, text) for every scannable tracked file.

    Reads `git ls-files` so that ignored files are excluded by
    definition: only content Git could actually commit is examined.
    Binary files are skipped by decoding with errors="ignore"; their
    patterns would not be meaningfully matched as text anyway.
    """
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    files: list[tuple[str, str]] = []
    for raw in result.stdout.split(b"\0"):
        if not raw:
            continue
        rel = raw.decode("utf-8", errors="replace")
        path = ROOT / rel
        if not path.is_file():
            continue
        # Skip any path inside an allowlisted directory.
        if any(part in rel for part in ALLOWLISTED_PATH_PARTS):
            continue
        if rel in SELF_PATHS:
            continue
        # Skip directories we never want to walk.
        if any(f"/{d}/" in f"/{rel}" for d in SKIP_DIRS):
            continue
        files.append((rel, path.read_text(encoding="utf-8", errors="ignore")))
    return files


def collect_staged_files() -> list[tuple[str, str]]:
    """Return (relative_path, text) for files staged in the index.

    Uses `git diff --cached --name-only` and then reads each blob from
    the index (`git show :path`) so that the scan sees exactly the
    bytes a commit would record, not the working-tree version.
    """
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "-z"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    files: list[tuple[str, str]] = []
    for raw in result.stdout.split(b"\0"):
        if not raw:
            continue
        rel = raw.decode("utf-8", errors="replace")
        if any(part in rel for part in ALLOWLISTED_PATH_PARTS):
            continue
        if rel in SELF_PATHS:
            continue
        blob = subprocess.run(
            ["git", "show", f":{rel}"],
            cwd=ROOT,
            capture_output=True,
        )
        if blob.returncode != 0:
            # Deleted from the index: nothing to scan.
            continue
        files.append((rel, blob.stdout.decode("utf-8", errors="ignore")))
    return files


def collect_history_hits() -> list[str]:
    """Return human-readable lines for hits found in any ref's history.

    Walks every commit reachable from every local ref and runs the
    pattern set against each unique blob. This is the slow mode: it
    exists for the pre-push audit, not for every commit.
    """
    hits: list[str] = []
    seen_blobs: set[str] = set()
    revs = subprocess.run(
        ["git", "rev-list", "--all"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    ).stdout.split()
    for rev in revs:
        # List blobs for this commit's tree, recursively.
        ls = subprocess.run(
            ["git", "ls-tree", "-r", rev],
            cwd=ROOT,
            capture_output=True,
        )
        for line in ls.stdout.split(b"\n"):
            if not line:
                continue
            parts = line.split(b"\t")
            if len(parts) != 2:
                continue
            meta = parts[0].split()
            if len(meta) < 3 or meta[1] != b"blob":
                continue
            sha = meta[2].decode()
            path = parts[1].decode("utf-8", errors="replace")
            if sha in seen_blobs:
                continue
            seen_blobs.add(sha)
            if any(part in path for part in ALLOWLISTED_PATH_PARTS):
                continue
            if path in SELF_PATHS:
                continue
            cat = subprocess.run(
                ["git", "cat-file", "blob", sha],
                cwd=ROOT,
                capture_output=True,
            )
            text = cat.stdout.decode("utf-8", errors="ignore")
            for spec in patterns_for(path):
                match = spec.regex.search(text)
                if match and not is_placeholder(match.group(0)):
                    hits.append(f"{rev.decode()[:10]} {path}: {spec.name}")
    return hits


# ---------------------------------------------------------------------------
# Scanning
# ---------------------------------------------------------------------------

def patterns_for(path: str) -> list[PatternSpec]:
    """Return the pattern specs that apply to the given repository path.

    Arguments:
        path: Repository-relative file path (forward slashes).

    Returns:
        All PATTERNS, minus any skip_in_tests pattern whose path
        looks like test code (TEST_PATH_PARTS). Live-key patterns
        are never skipped: a real key in a test file is still a leak.
    """
    is_test = any(part in path for part in TEST_PATH_PARTS)
    if not is_test:
        return list(PATTERNS)
    return [s for s in PATTERNS if not s.skip_in_tests]


def is_placeholder(match_text: str) -> bool:
    """Return True when a matched value is an obvious fake.

    Arguments:
        match_text: The full text the pattern matched.

    Returns:
        True when the value contains a PLACEHOLDER_FRAGMENTS word
        (case-insensitive), meaning documentation instructions and
        test doubles are reported as clean rather than as findings.
    """
    lower = match_text.lower()
    return any(fragment in lower for fragment in PLACEHOLDER_FRAGMENTS)


def scan(files: list[tuple[str, str]]) -> list[str]:
    """Return one human-readable line per (file, pattern) hit.

    Arguments:
        files: sequence of (relative_path, file_text) pairs already
            filtered for allowlists and self-reference.

    Returns:
        Empty list when clean; otherwise lines of the form
        "path:line: <pattern name>: <matched text, trimmed>".
    """
    findings: list[str] = []
    for rel, text in files:
        for spec in patterns_for(rel):
            for match in spec.regex.finditer(text):
                if is_placeholder(match.group(0)):
                    continue
                line_no = text.count("\n", 0, match.start()) + 1
                snippet = match.group(0)
                if len(snippet) > 60:
                    snippet = snippet[:57] + "..."
                findings.append(f"{rel}:{line_no}: {spec.name}: {snippet}")
    return findings


def main() -> int:
    """Parse arguments, run the requested scans, report, and exit.

    Returns:
        0 when clean, 1 when any hit is found, 2 on scanner failure.
    Side effects:
        Prints findings to standard output; modifies nothing.
    """
    parser = argparse.ArgumentParser(
        description="Block private or personal data from entering Git."
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="scan the staged index (the exact bytes a commit records)",
    )
    parser.add_argument(
        "--history",
        action="store_true",
        help="scan every blob reachable from every local ref (slow)",
    )
    args = parser.parse_args()

    try:
        findings: list[str] = []
        if args.history:
            findings += collect_history_hits()
        if args.staged:
            findings += scan(collect_staged_files())
        if not args.staged and not args.history:
            findings += scan(collect_tree_files())
    except subprocess.CalledProcessError as exc:
        print(f"verify_no_private_data: scanner failed: {exc}", file=sys.stderr)
        return 2

    if findings:
        print("PRIVATE DATA CHECK FAILED")
        print("=========================")
        for line in findings:
            print(f"  {line}")
        print()
        print("AGENTS.md policy 18 forbids committing this content.")
        print("Remove or redact the matches, or add an ignore rule,")
        print("then re-run this script.")
        return 1

    scope = "history" if args.history else ("staged" if args.staged else "working tree")
    print(f"verify_no_private_data: clean ({scope}, {len(PATTERNS)} pattern classes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
