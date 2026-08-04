#!/usr/bin/env python3
"""Validate the structural contract shared by 1-plan-task and 3-conduct-plan."""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


REQUIRED_HEADINGS = (
    "Conclusion",
    "Relevance",
    "Deliverables",
    "Inputs",
    "Non-Goals",
    "Scope Budget",
    "Files Allowed to Change",
    "Execution Plan",
    "Success Criteria",
    "Risks",
    "Stop Conditions",
    "Blocking Questions",
    "Approval Status",
)

COUNT_FIELDS = (
    "Primary experiments",
    "Sanity checks",
    "Parameter variants",
    "Expected figures",
    "Extra reports or presentations",
    "New dependencies",
    "Unrelated refactors",
    "Scientific interpretation",
    "Expected files to modify",
)

BOOLEAN_FIELDS = ("HPC run required", "External data download required")
ALLOWED_STATUSES = {"AWAITING_APPROVAL", "APPROVED", "NEEDS_REVISION", "BLOCKED"}
PLACEHOLDER_RE = re.compile(r"\[[^\]]+\]|\b(?:TBD|TODO|unknown)\b", re.IGNORECASE)


def section(text, heading):
    match = re.search(
        rf"^##\s+{re.escape(heading)}\s*$\n(.*?)(?=^##\s+|\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    return match.group(1).strip() if match else ""


def bullet_value(body, label):
    match = re.search(rf"^-\s+{re.escape(label)}\s*:\s*(.+?)\s*$", body, re.MULTILINE)
    return match.group(1).strip() if match else None


def validate(path, require_approved):
    errors = []
    warnings = []
    if not path.is_file():
        return {"valid": False, "errors": [f"not a file: {path}"], "warnings": []}

    raw = path.read_bytes()
    text = raw.decode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()

    if not re.search(r"^#\s+Task Contract\s*$", text, re.MULTILINE):
        errors.append("missing '# Task Contract' title")

    bodies = {}
    for heading in REQUIRED_HEADINGS:
        bodies[heading] = section(text, heading)
        if not bodies[heading]:
            errors.append(f"missing or empty section: {heading}")

    budget = bodies.get("Scope Budget", "")
    for label in COUNT_FIELDS:
        value = bullet_value(budget, label)
        if value is None:
            errors.append(f"missing Scope Budget field: {label}")
        elif not re.fullmatch(r"\d+", value):
            errors.append(f"Scope Budget field must be a non-negative integer: {label}={value!r}")

    for label in BOOLEAN_FIELDS:
        value = bullet_value(budget, label)
        if value is None:
            errors.append(f"missing Scope Budget field: {label}")
        elif value.lower() not in {"yes", "no"}:
            errors.append(f"Scope Budget field must be yes or no: {label}={value!r}")

    compute_scale = bullet_value(budget, "Compute scale")
    if not compute_scale:
        errors.append("missing Scope Budget field: Compute scale")

    status_body = bodies.get("Approval Status", "")
    status_value = bullet_value(status_body, "Status")
    status = status_value.strip("`") if status_value else None
    if status not in ALLOWED_STATUSES:
        errors.append(f"invalid approval status: {status!r}")
    if require_approved and status != "APPROVED":
        errors.append("contract is not APPROVED")

    allowed_files = bodies.get("Files Allowed to Change", "")
    if allowed_files and PLACEHOLDER_RE.search(allowed_files):
        errors.append("Files Allowed to Change contains a placeholder")

    deliverables = bodies.get("Deliverables", "")
    for record in ("RUN_RECORD.json", "VALIDATION.md"):
        if record not in deliverables:
            errors.append(f"Deliverables must declare workflow record: {record}")

    questions = bodies.get("Blocking Questions", "")
    question_count = len(re.findall(r"^\s*[-*]\s+.+", questions, re.MULTILINE))
    if question_count > 3:
        errors.append(f"Blocking Questions has {question_count} entries; maximum is 3")

    for heading in ("Conclusion", "Deliverables", "Inputs", "Execution Plan", "Success Criteria"):
        if bodies.get(heading) and PLACEHOLDER_RE.search(bodies[heading]):
            warnings.append(f"section contains a placeholder: {heading}")

    return {
        "valid": not errors,
        "path": str(path.resolve()),
        "sha256": digest,
        "status": status,
        "errors": errors,
        "warnings": warnings,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    parser.add_argument("--require-approved", action="store_true")
    args = parser.parse_args()
    result = validate(args.contract, args.require_approved)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
