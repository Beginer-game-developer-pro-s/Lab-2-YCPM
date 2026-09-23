#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
elicitation_toolkit.py
Lab 2 - Requirements Elicitation
Course: Software Requirements (CSE703095) - Phenikaa University
Author / Performed by: Trần Doãn Việt Anh
-----------------------------------------------------------------
Demonstrates the process of turning raw elicitation data (interview
notes, survey results, workshop notes) into a list of candidate
requirements using keyword-tagging and regex pattern matching.
Includes automated conflict detection across stakeholder needs.

Run: python elicitation_toolkit.py
"""
import csv
import os
import re

# Determine raw notes file path (current directory or fallback to datasets)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_RAW = os.path.join(BASE_DIR, "raw_interview_notes.txt")
FALLBACK_RAW = os.path.join(
    BASE_DIR, "..", "..", "..", "datasets", "raw_interview_notes.txt"
)
RAW_PATH = LOCAL_RAW if os.path.exists(LOCAL_RAW) else FALLBACK_RAW

OUT_CSV = os.path.join(BASE_DIR, "candidate_requirements.csv")

# Keyword -> requirement type dictionary
KEYWORD_MAP = {
    r"search.*doctor|by specialty": (
        "Search doctors by specialty",
        "Functional",
    ),
    r"remind|notification": (
        "Appointment reminder notification",
        "Functional",
    ),
    r"confirmation step|confirm.*booking": (
        "Confirm booking before finalizing",
        "Functional",
    ),
    r"warns?.*conflict|allergy": (
        "Drug interaction/allergy warning",
        "Functional - Safety",
    ),
    r"report on|statistics": (
        "Visit statistics report",
        "Functional",
    ),
    r"manage the doctor list|working schedule": (
        "Manage doctor catalog",
        "Functional",
    ),
    r"crash|peak hour": (
        "System stability during peak hours",
        "Non-functional - Performance",
    ),
    r"encrypted|access.*controlled|sensitive information": (
        "Data security & encryption",
        "Non-functional - Security",
    ),
    r"verifying health insurance": (
        "Verify health insurance coverage",
        "Functional",
    ),
    r"nobody answering the phone|call.*many times": (
        "Alternative booking channel to phone",
        "Functional",
    ),
    # Task 2: Extended Regex Patterns
    r"family member|book on behalf": (
        "Book on behalf of a family member",
        "Functional",
    ),
    r"multi-?language|other languages": (
        "Multi-language UI support",
        "Non-functional - Usability",
    ),
    r"two-factor|OTP verification": (
        "OTP-based login verification",
        "Non-functional - Security",
    ),
}

# Task 2: Contradictory stakeholder needs mapping
CONFLICT_PAIRS = [
    {
        "pair": (
            "unlimited reschedules",
            "receptionist reschedule control policy",
        ),
        "stakeholders": ("SH-01 (Patient)", "SH-03 (Receptionist)"),
        "change_request_id": "CR-003",
        "action": "Escalate to Change Control Board (CCB)",
    },
]


def extract_candidates(text):
    """
    Scans raw text against KEYWORD_MAP using case-insensitive regex.
    Returns a list of unique (label, category) tuples.
    """
    found = []
    seen = set()
    for pattern, (label, kind) in KEYWORD_MAP.items():
        if re.search(pattern, text, flags=re.IGNORECASE):
            if label not in seen:
                found.append((label, kind))
                seen.add(label)
    return found


def detect_conflicts(candidates):
    """
    Matches candidate requirements against CONFLICT_PAIRS to identify
    contradictory stakeholder needs.
    Accepts candidate tuples or candidate labels.
    """
    labels = [
        (c[0] if isinstance(c, (tuple, list)) else str(c)).lower()
        for c in candidates
    ]
    detected = []
    for item in CONFLICT_PAIRS:
        req_a, req_b = item["pair"]
        has_a = any(req_a.lower() in l for l in labels)
        has_b = any(req_b.lower() in l for l in labels)
        if has_a and has_b:
            detected.append(item)
    return detected


def main():
    if not os.path.exists(RAW_PATH):
        raise FileNotFoundError(f"Cannot find raw notes file at: {RAW_PATH}")

    with open(RAW_PATH, encoding="utf-8") as f:
        text = f.read()

    candidates = extract_candidates(text)

    # Save extracted candidate requirements to UTF-8 CSV
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["No", "CandidateRequirement", "Category", "Source"])
        for i, (label, kind) in enumerate(candidates, 1):
            w.writerow([i, label, kind, "Interviews + Survey + Workshop"])

    print(f"Extracted {len(candidates)} candidate requirements from raw data:\n")
    for i, (label, kind) in enumerate(candidates, 1):
        print(f"  {i:2d}. [{kind}] {label}")
    print(f"\n[OK] Saved candidate requirements to: {OUT_CSV}")

    # Stakeholder Conflict Detection Demonstration (Task 2)
    print("\n" + "=" * 65)
    print("STAKEHOLDER CONFLICT DETECTION (Task 2)")
    print("=" * 65)

    # 1. Check direct conflicts in current extracted candidates
    direct_conflicts = detect_conflicts(candidates)
    if direct_conflicts:
        print(f"[!] Detected {len(direct_conflicts)} conflict(s) in dataset.")
    else:
        print("[-] No direct conflict detected in current explicit notes.")

    # 2. Test contradictory scenario: Patient (SH-01) vs Receptionist (SH-03)
    simulated_candidates = list(candidates) + [
        ("Allow unlimited reschedules by patient", "Functional"),
        ("Strict receptionist reschedule control policy", "Functional"),
    ]
    simulated_conflicts = detect_conflicts(simulated_candidates)
    print("\n[*] Executing conflict check on simulated stakeholder inputs:")
    for conflict in simulated_conflicts:
        req_a, req_b = conflict["pair"]
        sh_a, sh_b = conflict["stakeholders"]
        c_id = conflict["change_request_id"]
        action = conflict["action"]
        print(f"    - Conflict ID: {c_id}")
        print(f"      * {sh_a}: '{req_a}' (Unrestricted rescheduling desire)")
        print(f"      * {sh_b}: '{req_b}' (Rescheduling control policy)")
        print(f"      * Action: {action} (Escalate to Change Control Board)")

    print("\n>> Next step: Proceed to qualitative analysis & report review.")


if __name__ == "__main__":
    main()
