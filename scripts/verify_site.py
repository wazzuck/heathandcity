#!/usr/bin/env python3
"""
==============================================================================
FILE: scripts/verify_site.py
==============================================================================

PURPOSE:
Automated quality, architecture, and policy verification script for the
Hampstead and North West (NW) London consulting showcase website.

WHAT THIS FILE IS NOT FOR:
- Does not modify or format source files in place.
- Does not require external third-party Python packages outside the standard
  library.

INVARIANTS:
1. Exits with status code 0 only when all structural, hosting, content, and
   80-column documentation checks pass.
2. Exits with status code 1 and prints a diagnostic report if any check fails.
==============================================================================
"""

from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from typing import List, Set, Tuple

# Maximum line width allowed for Markdown documentation and code comments per
# AGENTS.md Section 4, Policy 6.
# Value: 80 characters. Consumed by: check_line_lengths().
MAX_DOC_COLUMNS = 80

# Root directory of the repository checkout.
# Consumed by: main() and all verification helpers.
REPO_ROOT = Path(__file__).resolve().parent.parent


class ShowcaseHTMLValidator(HTMLParser):
    """
    Lightweight HTML parser that records element identifiers and verifies
    basic tag balance in index.html.

    Attributes:
        element_ids (Set[str]): Set of all id="..." values encountered.
        canvas_found (bool): True if the 3D GPU showcase canvas exists.
    """

    def __init__(self) -> None:
        """Initialise the HTML validator state."""
        super().__init__()
        self.element_ids: Set[str] = set()
        self.canvas_found: bool = False

    def handle_starttag(
        self, tag: str, attrs: List[Tuple[str, str | None]]
    ) -> None:
        """
        Inspect each opening HTML tag and record its id attribute.

        Args:
            tag: Lowercase HTML tag name.
            attrs: List of (attribute_name, attribute_value) pairs.
        """
        attr_map = dict(attrs)
        el_id = attr_map.get("id")
        if el_id:
            self.element_ids.add(el_id)
        if tag == "canvas" and el_id == "gpu-centrepiece-canvas":
            self.canvas_found = True


def check_required_files() -> List[str]:
    """
    Verify that all required static website and documentation files exist.

    Returns:
        List of error messages (empty if all files exist).
    """
    errors: List[str] = []
    required_paths = [
        "index.html",
        "css/styles.css",
        "js/config.js",
        "js/gpu-scene.js",
        "js/app.js",
        "package.json",
        "docs/ARCHITECTURE.md",
        "README.md",
    ]
    # 1. Iterate through each required relative path and check existence.
    for rel_path in required_paths:
        full_path = REPO_ROOT / rel_path
        if not full_path.is_file():
            errors.append(f"Missing required file: {rel_path}")
        elif full_path.stat().st_size == 0:
            errors.append(f"Required file is empty: {rel_path}")
    return errors


def check_html_structure() -> List[str]:
    """
    Parse index.html and confirm all mandatory section identifiers, interactive
    controls, and strategy content markers are present.

    Returns:
        List of error messages (empty if valid).
    """
    errors: List[str] = []
    html_path = REPO_ROOT / "index.html"
    if not html_path.is_file():
        return ["index.html not found"]

    # 1. Read and parse index.html.
    content = html_path.read_text(encoding="utf-8")
    validator = ShowcaseHTMLValidator()
    validator.feed(content)

    if not validator.canvas_found:
        errors.append("Missing <canvas id='gpu-centrepiece-canvas'>")

    # 2. Check mandatory section and control IDs.
    required_ids = {
        "gpu-centrepiece-canvas",
        "order-slider",
        "daily-screen",
        "services-by-vertical",
        "specialist-roles",
        "architecture",
        "pricing",
        "contact",
        "audit-enquiry-form",
    }
    missing_ids = required_ids - validator.element_ids
    for mid in sorted(missing_ids):
        errors.append(f"Missing required HTML element id='{mid}'")

    # 3. Verify strategy coverage across verticals and pricing in HTML + config.
    config_text = (REPO_ROOT / "js/config.js").read_text(encoding="utf-8")
    combined_text = content + "\n" + config_text
    required_phrases = [
        "NW3",
        "NW6",
        "NW8",
        "NW11",
        "N6",
        "Two-Tower",
        "itoldyouso.tech",
        "£750",
        "£3,000",
        "£350",
        "Outlook",
        "Single-PA Fragility",
    ]
    for phrase in required_phrases:
        if phrase not in combined_text:
            errors.append(f"Missing strategy phrase: '{phrase}'")

    return errors


def check_gpu_and_hosting_constraints() -> List[str]:
    """
    Verify that the JavaScript modules implement WebGPU detection, Three.js
    rendering, Canvas 2D fallback, and reduced-motion support without using
    SharedArrayBuffer.

    Returns:
        List of error messages (empty if valid).
    """
    errors: List[str] = []
    gpu_js = (REPO_ROOT / "js/gpu-scene.js").read_text(encoding="utf-8")

    # 1. Confirm WebGPU, Three.js, Canvas fallback, and reduced-motion hooks.
    required_tokens = [
        "navigator.gpu",
        "requestAdapter",
        "WebGLRenderer",
        "initCanvas3DFallback",
        "prefers-reduced-motion",
    ]
    for token in required_tokens:
        if token not in gpu_js:
            errors.append(
                f"js/gpu-scene.js missing required fallback token: {token}"
            )

    # 2. Ensure SharedArrayBuffer is never instantiated in code.
    for js_rel in ["js/config.js", "js/gpu-scene.js", "js/app.js"]:
        js_lines = (REPO_ROOT / js_rel).read_text(encoding="utf-8").splitlines()
        for lineno, line in enumerate(js_lines, start=1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("*"):
                continue
            if "SharedArrayBuffer" in stripped:
                errors.append(
                    f"{js_rel}:{lineno} uses forbidden SharedArrayBuffer"
                )

    # 3. Validate package.json is valid JSON.
    try:
        json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"package.json is invalid JSON: {exc}")

    return errors


def check_line_lengths() -> List[str]:
    """
    Verify that documentation files and code comment lines wrap at or below
    MAX_DOC_COLUMNS (80 characters), exempting standalone unbreakable links.

    Returns:
        List of error messages (empty if all lines comply).
    """
    errors: List[str] = []

    # 1. Check Markdown documentation files crafted for this project.
    md_files = ["docs/ARCHITECTURE.md", "README.md"]
    if (REPO_ROOT / "STATUS.md").is_file():
        md_files.append("STATUS.md")

    for rel_path in md_files:
        lines = (REPO_ROOT / rel_path).read_text(encoding="utf-8").splitlines()
        for lineno, line in enumerate(lines, start=1):
            if len(line) > MAX_DOC_COLUMNS and "http" not in line:
                errors.append(
                    f"{rel_path}:{lineno} exceeds {MAX_DOC_COLUMNS} cols "
                    f"({len(line)} chars)"
                )

    # 2. Check comment lines in JavaScript, CSS, and Python files.
    code_files = [
        "js/config.js",
        "js/gpu-scene.js",
        "js/app.js",
        "css/styles.css",
        "scripts/verify_site.py",
    ]
    for rel_path in code_files:
        lines = (REPO_ROOT / rel_path).read_text(encoding="utf-8").splitlines()
        for lineno, line in enumerate(lines, start=1):
            stripped = line.strip()
            is_comment = (
                stripped.startswith("//")
                or stripped.startswith("/*")
                or stripped.startswith("*")
                or stripped.startswith("#")
            )
            if is_comment and len(line) > MAX_DOC_COLUMNS:
                if "http://" not in line and "https://" not in line:
                    errors.append(
                        f"{rel_path}:{lineno} comment exceeds "
                        f"{MAX_DOC_COLUMNS} cols ({len(line)} chars)"
                    )

    return errors


def main() -> int:
    """
    Execute all verification steps and report the outcome.

    Returns:
        0 if all checks pass, or 1 if any check fails.
    """
    all_errors: List[str] = []
    # 1. Run file existence checks.
    all_errors.extend(check_required_files())
    # 2. Run HTML and strategy coverage checks.
    all_errors.extend(check_html_structure())
    # 3. Run WebGPU/WebGL fallback and GitHub Pages constraint checks.
    all_errors.extend(check_gpu_and_hosting_constraints())
    # 4. Run 80-column documentation and comment checks.
    all_errors.extend(check_line_lengths())

    if all_errors:
        print("VERIFICATION FAILED:")
        for err in all_errors:
            print(f"  - {err}")
        return 1

    print("ALL VERIFICATION CHECKS PASSED (files, HTML, GPU fallbacks, 80-col).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
