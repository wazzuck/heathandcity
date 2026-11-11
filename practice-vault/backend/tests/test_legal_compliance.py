"""
Unit Tests for Legal, Regulatory, and Commercial Licensing Compliance.

Verifies that the codebase and appliance conform to UK GDPR, SRA/BSB privilege,
NHS Caldicott Principles, and commercial permissive licensing standards.
"""

from pathlib import Path
import subprocess
import sys


def test_legal_compliance_script_passes():
    """Verify scripts/verify_legal_compliance.py exits with code 0."""
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    script_path = repo_root / "scripts" / "verify_legal_compliance.py"
    assert script_path.exists(), f"Missing legal check script at {script_path}"

    res = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"Legal check failed:\n{res.stdout}\n{res.stderr}"
    assert "ALL LEGAL & REGULATORY COMPLIANCE CHECKS PASSED" in res.stdout
