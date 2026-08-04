#!/usr/bin/env python3
"""Check a public skill tree for portable metadata and resource links."""
from __future__ import print_function

import os
import re
import sys

FORBIDDEN = ("/home" + "/users/", "/storage" + "/research/", "/.conda" + "/envs/")
REQUIRED = ("name", "description")


def read_text(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def frontmatter(text):
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end < 0:
        return None
    values = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()
    return values


def main(root):
    errors = []
    skills = []
    for name in sorted(os.listdir(root)):
        path = os.path.join(root, name)
        skill_file = os.path.join(path, "SKILL.md")
        if os.path.isdir(path) and os.path.isfile(skill_file):
            skills.append((name, skill_file))

    for name, skill_file in skills:
        text = read_text(skill_file)
        meta = frontmatter(text)
        if meta is None:
            errors.append("{}: missing YAML frontmatter".format(skill_file))
            continue
        if set(meta) != set(REQUIRED):
            errors.append("{}: frontmatter must contain only name and description".format(skill_file))
        if meta.get("name") != name:
            errors.append("{}: name must match directory".format(skill_file))
        if not meta.get("description"):
            errors.append("{}: description is empty".format(skill_file))

    for base, _, files in os.walk(root):
        for filename in files:
            path = os.path.join(base, filename)
            if filename.endswith((".md", ".py", ".mplstyle")):
                text = read_text(path)
                for item in FORBIDDEN:
                    if item in text:
                        errors.append("{}: machine-specific path fragment {}".format(path, item))
                if filename.endswith(".md"):
                    for target in re.findall(r"\]\(([^)#]+)", text):
                        if "://" in target or target.startswith("/") or target.startswith("<"):
                            continue
                        if not target.startswith(("./references/", "./scripts/")):
                            continue
                        if target.lower().endswith((".png", ".jpg", ".jpeg", ".svg", ".pdf")):
                            continue
                        candidate = os.path.normpath(os.path.join(base, target))
                        if not os.path.exists(candidate):
                            errors.append("{}: broken relative link {}".format(path, target))

    print("skills: {}".format(len(skills)))
    for error in errors:
        print("ERROR: {}".format(error))
    return 1 if errors else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: verify_skill_tree.py <skills-root>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
