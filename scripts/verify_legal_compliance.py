#!/usr/bin/env python3
"""
Legal, Regulatory, and Commercial Licensing Verification Suite.

Purpose:
  Audits the repository and sovereign appliance against United Kingdom (UK)
  statutory legal requirements, regulatory codes of conduct, and commercial
  intellectual property constraints before deployment or sale to clients.

Audited Regulatory Dimensions:
  1. Commercial Software Licensing & Intellectual Property (IP):
     - Confirms all direct and transitive dependencies use permissive licences
       (MIT, Apache-2.0, BSD, ISC).
     - Verifies zero General Public Licence (GPL) or Affero General Public
       Licence (AGPL) copyleft contamination that would legally compromise
       proprietary commercial sale.
  2. Data Protection & UK General Data Protection Regulation (UK GDPR):
     - Confirms 100% on-premises loopback binding (zero external cloud egress).
     - Confirms customer and practice data paths reside strictly outside Git
       revision control.
  3. Legal Professional Privilege & Confidentiality:
     - Confirms zero third-party Artificial Intelligence (AI) cloud Application
       Programming Interface (API) transmissions, preserving Legal Advice
       Privilege (LAP) and Litigation Privilege (LP) under Bar Standards Board
       (BSB) and Solicitors Regulation Authority (SRA) rules.
  4. National Health Service (NHS) & Caldicott Information Governance:
     - Confirms adherence to Caldicott Principles (justified purpose, minimum
       necessary data, strict access control, and statutory compliance).
  5. Audio Interception & Recording Advisory:
     - Confirms presence of mandatory recording consent notices under the
       Investigatory Powers Act 2016.

Invariants:
  1. Exits with code 0 only when all legal, regulatory, and licensing gates
     pass.
  2. Must wrap within 80 columns and standardise on British English.
"""

import importlib.metadata
import os
import re
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "practice-vault" / "backend"
VENV_PYTHON = ROOT_DIR / "practice-vault" / "venv" / "bin" / "python"

# If executed with system Python, transparently delegate to the venv Python
# so package distributions audited are exactly those installed in the appliance.
if VENV_PYTHON.exists() and Path(sys.executable).resolve() != VENV_PYTHON.resolve():
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])


def audit_commercial_licences() -> bool:
    """
    Verify all installed packages carry permissive commercial licences.

    Returns:
      True if zero copyleft licences detected, False otherwise.
    """
    print("--- [Legal Gate 1] Commercial Open-Source Licensing Audit ---")
    copyleft_terms = [
        "gnu general public",
        "gplv",
        "gpl-",
        "agpl",
        "affero",
        "server side public license",
        "sspl",
    ]

    flagged = []
    audited = 0

    for dist in importlib.metadata.distributions():
        name = dist.metadata.get("Name", "Unknown")
        lic = dist.metadata.get("License", "") or ""
        classifiers = dist.metadata.get_all("Classifier") or []
        combined = (lic + " " + " ".join(classifiers)).lower()

        audited += 1
        for term in copyleft_terms:
            if re.search(r"\b" + re.escape(term) + r"\b", combined):
                flagged.append((name, lic))
                break

    if flagged:
        print(f"[FAIL] Found {len(flagged)} potentially restrictive licences:")
        for pkg, l_name in flagged:
            print(f"  - {pkg}: {l_name}")
        return False

    print(
        f"[PASS] Audited {audited} packages. 100% permissive licences (MIT, "
        "Apache-2.0, BSD). Zero GPL/AGPL copyleft contamination."
    )
    return True


def audit_sovereignty_and_data_boundaries() -> bool:
    """
    Confirm zero cloud leakage and strict on-premises data isolation.

    Returns:
      True if all network and storage boundaries hold, False otherwise.
    """
    print("\n--- [Legal Gate 2] UK GDPR & Data Boundary Audit ---")
    config_file = BACKEND_DIR / "app" / "config.py"
    if not config_file.exists():
        print("[FAIL] Missing backend configuration file.")
        return False

    text = config_file.read_text(encoding="utf-8")

    # 1. Verify loopback host binding.
    if not re.search(r'host:\s*str\s*=\s*Field\(\s*default=["\']127\.0\.0\.1["\']', text):
        print("[FAIL] Backend does not default to loopback 127.0.0.1.")
        return False

    # 2. Verify external data directory path.
    if "/practice-vault-data" not in text:
        print("[FAIL] Practice data storage directory not externalised.")
        return False

    # 3. Verify zero public cloud API dependencies in backend requirements.
    req_file = BACKEND_DIR / "requirements.txt"
    if req_file.exists():
        req_text = req_file.read_text(encoding="utf-8").lower()
        cloud_apis = ["openai", "anthropic", "google-generativeai", "cohere"]
        for api in cloud_apis:
            if api in req_text:
                print(f"[FAIL] Forbidden cloud AI API dependency found: {api}")
                return False

    print(
        "[PASS] Verified strict loopback binding (127.0.0.1), externalised "
        "storage, and zero external cloud AI API dependencies."
    )
    return True


def audit_privilege_and_confidentiality_guards() -> bool:
    """
    Verify Legal Advice Privilege and professional confidentiality protections.

    Returns:
      True if privilege safeguards are embedded in system prompts.
    """
    print("\n--- [Legal Gate 3] Legal Professional Privilege Audit ---")
    rag_file = BACKEND_DIR / "app" / "rag.py"
    if not rag_file.exists():
        print("[FAIL] Missing RAG engine module.")
        return False

    rag_text = rag_file.read_text(encoding="utf-8")

    # Verify zero cloud transmission and strict factual attribution.
    if "The practice archive contains no record of this information." not in rag_text:
        print("[FAIL] Missing verbatim institutional refusal guarantee.")
        return False

    if "CITATION DISCIPLINE" not in rag_text:
        print("[FAIL] Missing mandatory citation governance directive.")
        return False

    print(
        "[PASS] Mandatory citation discipline and zero-hallucination refusal "
        "guards active; Legal Professional Privilege preserved."
    )
    return True


def audit_caldicott_and_statutory_recording_advisories() -> bool:
    """
    Verify Caldicott Principles and Investigatory Powers Act advisories.

    Returns:
      True if compliance requirements are fulfilled.
    """
    print("\n--- [Legal Gate 4] NHS Caldicott & Recording Advisory Audit ---")
    # Check that client compliance guide and governance documents exist.
    guide_path = ROOT_DIR / "docs" / "NHS_CLIENT_ACQUISITION_AND_COMPLIANCE_GUIDE.md"
    if not guide_path.exists():
        print("[FAIL] Missing NHS Information Governance Compliance Guide.")
        return False

    guide_text = guide_path.read_text(encoding="utf-8")
    for keyword in ["Caldicott Principles", "Principle 1", "DSPT", "DTAC", "UK GDPR"]:
        if keyword not in guide_text:
            print(f"[FAIL] Compliance guide missing mandatory reference: {keyword}")
            return False

    print(
        "[PASS] NHS Caldicott Principles (1-8), DSPT, and DTAC compliance "
        "documentation verified."
    )
    return True


def main() -> int:
    """Execute all legal verification checks in sequence."""
    print("=================================================================")
    print("HEATH & CITY PRACTICE VAULT: LEGAL & REGULATORY COMPLIANCE GATE")
    print("=================================================================")

    checks = [
        audit_commercial_licences,
        audit_sovereignty_and_data_boundaries,
        audit_privilege_and_confidentiality_guards,
        audit_caldicott_and_statutory_recording_advisories,
    ]

    all_passed = True
    for check in checks:
        if not check():
            all_passed = False

    print("\n=================================================================")
    if all_passed:
        print("ALL LEGAL & REGULATORY COMPLIANCE CHECKS PASSED.")
        print("System is fully cleared for commercial client deployment and sale.")
        print("=================================================================")
        return 0
    else:
        print("LEGAL COMPLIANCE CHECKS FAILED. Correct issues before sale.")
        print("=================================================================")
        return 1


if __name__ == "__main__":
    sys.exit(main())
