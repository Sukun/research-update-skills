#!/usr/bin/env python3
"""Verify shared Agent Skills metadata, resource links, and portable paths."""

import argparse
import re
import sys
from pathlib import Path


NAME_RE = re.compile(r"^[a-z0-9-]{1,64}$")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
FORBIDDEN_PATHS = ("~/.claude/skills", "/home/users/tg932198/.claude/skills")


def remove_fenced_blocks(text):
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    return re.sub(r"`[^`]*`", "", text)


def frontmatter(text):
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, flags=re.DOTALL)
    if not match:
        return None, ["missing YAML frontmatter"]
    fields = {}
    errors = []
    for line in match.group(1).splitlines():
        if not line.strip():
            continue
        field = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not field:
            errors.append("unsupported multiline or malformed frontmatter: " + line)
            continue
        fields[field.group(1)] = field.group(2).strip().strip('"\'')
    unexpected = sorted(set(fields) - {"name", "description"})
    if unexpected:
        errors.append("unexpected frontmatter fields: " + ", ".join(unexpected))
    for required in ("name", "description"):
        if not fields.get(required):
            errors.append("missing frontmatter field: " + required)
    return fields, errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--expected-link-target")
    args = parser.parse_args()
    root = args.root.expanduser()
    errors = []
    checked = 0

    if not root.is_dir():
        print("ERROR: skill root is not a directory: {}".format(root))
        return 1

    if args.expected_link_target and root.is_symlink():
        actual = str(root.resolve())
        expected = str(Path(args.expected_link_target).expanduser().resolve())
        if actual != expected:
            errors.append("skill-root symlink resolves to {}, expected {}".format(actual, expected))

    for skill_dir in sorted(root.iterdir()):
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.is_file():
            continue
        checked += 1
        text = skill_file.read_text(encoding="utf-8")
        fields, local_errors = frontmatter(text)
        errors.extend("{}: {}".format(skill_dir.name, item) for item in local_errors)
        if fields:
            name = fields.get("name", "")
            if name != skill_dir.name:
                errors.append("{}: name field is {!r}".format(skill_dir.name, name))
            if not NAME_RE.match(name):
                errors.append("{}: invalid skill name".format(skill_dir.name))
            if len(fields.get("description", "")) > 1024:
                errors.append("{}: description exceeds 1024 characters".format(skill_dir.name))

        prose = remove_fenced_blocks(text)
        for link in LINK_RE.findall(prose):
            clean = link.split("#", 1)[0]
            if not clean or "://" in clean or clean.startswith("mailto:"):
                continue
            target = (skill_dir / clean).resolve()
            if not target.exists():
                errors.append("{}: broken relative resource link {}".format(skill_dir.name, link))

    for path in root.rglob("*"):
        if not path.is_file() or any(part in {".git", "__pycache__"} for part in path.parts):
            continue
        if path.resolve() == Path(__file__).resolve():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for forbidden in FORBIDDEN_PATHS:
            if forbidden in text:
                errors.append("{}: forbidden path {}".format(path.relative_to(root), forbidden))

    print("skills_checked={}".format(checked))
    print("errors={}".format(len(errors)))
    for error in errors:
        print("ERROR: " + error)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
