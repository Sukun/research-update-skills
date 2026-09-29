#!/usr/bin/env python3
"""assemble_figures.py — deterministic figure resolver + minimal storyboard writer.

Part of the 4-mk_quickview skill (share step, explicit-arrangement mode; moved from 5a-ppt-quick-assembly). Does NO rendering: it resolves a
(group x role) figure matrix from a directory and emits a storyboard that
6-ppt-create consumes unchanged.

Usage
-----
  python assemble_figures.py SPEC.json            # dry-run: print the matrix only
  python assemble_figures.py SPEC.json --write    # also write storyboard + index.json

Exit codes: 0 = fully resolved, 2 = missing or ambiguous cells (nothing written).
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # aspect detection degrades gracefully
    Image = None

COLORS = ["steelblue", "darkorange", "teal", "purple", "crimson"]
IMG_EXT = {".png", ".jpg", ".jpeg", ".pdf", ".svg", ".gif", ".tif", ".tiff"}
ASPECT_BREAKEVEN = 2.3          # same threshold as 5-ppt-design / 6-ppt-create
ASPECT_FALLBACK = 1.6
TITLE_MAX = 65


# ----------------------------------------------------------------- utilities

def tokenize(name: str) -> list[str]:
    """Split a file stem into tokens on _ - and whitespace, preserving case."""
    return [t for t in re.split(r"[_\-\s]+", Path(name).stem) if t]


def tokenize_lower(name: str) -> list[str]:
    """Lowercase token view, for matching only — never for rebuilding filenames."""
    return [t.lower() for t in tokenize(name)]


def list_figures(directory: Path) -> list[Path]:
    return sorted(p for p in directory.iterdir()
                  if p.is_file() and p.suffix.lower() in IMG_EXT)


def aspect_of(path: Path) -> float:
    if Image is None:
        return ASPECT_FALLBACK
    try:
        w, h = Image.open(path).size
        return w / h
    except Exception:
        return ASPECT_FALLBACK


def rebuild(tokens: list[str], pos: int, alias: str, stem_sep: str, suffix: str) -> str:
    out = list(tokens)
    out[pos] = alias
    return stem_sep.join(out) + suffix


# --------------------------------------------------------------- resolution

def resolve_by_example(example: str, groups, shared: bool, directory: Path):
    """Substitution mode.

    Take one example filename, find which token position holds a group alias,
    and rebuild the same filename for every other group. The hypothesis that
    resolves the most groups wins; a tie between hypotheses producing different
    file sets is reported as ambiguous.
    """
    ex_path = Path(example)
    ex_name = ex_path.name
    suffix = ex_path.suffix
    toks = tokenize(ex_name)          # original case — used to rebuild filenames
    toks_lc = [t.lower() for t in toks]
    # preserve the original separator style ('_' is overwhelmingly the norm)
    sep = "_" if "_" in Path(ex_name).stem else "-"

    alias_owner = {}
    for gi, g in enumerate(groups):
        for a in g["tokens"]:
            alias_owner.setdefault(a.lower(), gi)

    hypotheses = []
    for pos, t in enumerate(toks_lc):
        if t in alias_owner:
            hypotheses.append(pos)

    if not hypotheses:
        # No group alias in the example. Reusing it for every slide is only safe
        # when the user said so — otherwise this is an example that belongs to a
        # group outside `groups` and must not be silently copied everywhere.
        p = directory / ex_name
        if not p.exists():
            return {g["name"]: {"status": "missing", "candidates": [],
                                "note": f"{ex_name} not found in directory"} for g in groups}
        if shared:
            return {g["name"]: {"status": "ok", "path": str(p.resolve()),
                                "note": "shared figure (role marked \"shared\": true)"}
                    for g in groups}
        return {g["name"]: {"status": "ambiguous", "candidates": [ex_name],
                            "note": "example contains no group token — add \"shared\": true "
                                    "to reuse it on every slide, or give a per-group example"}
                for g in groups}

    scored = []
    for pos in hypotheses:
        res = {}
        hits = 0
        for g in groups:
            found = []
            for alias in g["tokens"]:
                for variant in dict.fromkeys([alias, alias.lower(), alias.upper(),
                                              alias.capitalize()]):
                    cand = directory / rebuild(toks, pos, variant, sep, suffix)
                    if cand.exists() and cand not in found:
                        found.append(cand)
            if len(found) == 1:
                res[g["name"]] = {"status": "ok", "path": str(found[0].resolve())}
                hits += 1
            elif len(found) > 1:
                res[g["name"]] = {"status": "ambiguous",
                                  "candidates": [c.name for c in found]}
            else:
                res[g["name"]] = {"status": "missing", "candidates": [],
                                  "note": f"expected {rebuild(toks, pos, g['tokens'][0], sep, suffix)}"}
        scored.append((hits, pos, res))

    scored.sort(key=lambda x: -x[0])
    best_hits, _, best = scored[0]
    rivals = [s for s in scored[1:] if s[0] == best_hits]
    for _, _, other in rivals:
        if {k: v.get("path") for k, v in other.items()} != {k: v.get("path") for k, v in best.items()}:
            for name in best:
                cands = sorted({best[name].get("path", ""), other[name].get("path", "")} - {""})
                best[name] = {"status": "ambiguous",
                              "candidates": [Path(c).name for c in cands],
                              "note": "example filename matches several group-token positions"}
            break
    return best


def resolve_by_tokens(role, groups, all_files, directory: Path):
    """Filter mode: include/exclude token lists plus the group's own alias."""
    include = [t.lower() for t in role.get("include", [])]
    exclude = [t.lower() for t in role.get("exclude", [])]
    out = {}
    for g in groups:
        aliases = [a.lower() for a in g["tokens"]]
        hits = []
        foreign = {a.lower() for og in groups if og is not g for a in og["tokens"]} - set(aliases)
        for f in all_files:
            toks = set(tokenize_lower(f.name))
            if not all(i in toks for i in include):
                continue
            if any(e in toks for e in exclude):
                continue
            if aliases and not any(a in toks for a in aliases):
                continue
            if foreign & toks:          # belongs to another group's slide
                continue
            hits.append(f)
        if len(hits) == 1:
            out[g["name"]] = {"status": "ok", "path": str(hits[0].resolve())}
        elif not hits:
            out[g["name"]] = {"status": "missing", "candidates": [],
                              "note": f"include={include} exclude={exclude}"}
        else:
            out[g["name"]] = {"status": "ambiguous",
                              "candidates": [h.name for h in hits]}
    return out


def resolve_matrix(spec, directory: Path):
    groups = spec["groups"]
    roles = spec["roles"]
    all_files = list_figures(directory)
    overrides = {k.lower(): v for k, v in spec.get("overrides", {}).items()}

    matrix = {}
    for role in roles:
        rname = role["name"]
        if "example" in role:
            cells = resolve_by_example(role["example"], groups,
                                       bool(role.get("shared", False)), directory)
        else:
            cells = resolve_by_tokens(role, groups, all_files, directory)
        for g in groups:
            key = f"{g['name']}|{rname}".lower()
            if key in overrides:
                p = Path(overrides[key])
                p = p if p.is_absolute() else directory / p
                cells[g["name"]] = ({"status": "ok", "path": str(p.resolve()),
                                     "note": "user override"} if p.exists()
                                    else {"status": "missing", "candidates": [],
                                          "note": f"override {p} does not exist"})
        matrix[rname] = cells
    return matrix


# ------------------------------------------------------------ storyboard IO

def pick_layout(paths, explicit):
    if explicit and explicit != "auto":
        return explicit
    n = len(paths)
    if n == 1:
        return "single"
    if n == 4:
        return "grid-2x2"
    if n == 6:
        return "grid-2x3"
    if n in (2, 3):
        amin = min(aspect_of(Path(p)) for p in paths)
        stack = "vstack" if amin >= ASPECT_BREAKEVEN else "hstack"
        return f"{stack}-{n}"
    raise SystemExit(f"ERROR: {n} figures per slide has no default layout — set \"layout\" explicitly.")


def write_storyboard(spec, matrix, directory: Path, out_path: Path):
    groups = spec["groups"]
    roles = [r["name"] for r in spec["roles"]]
    title = spec.get("title", "").strip()
    fig_height = spec.get("figure_height", "13/14")

    lines = ["---", "---", ""]
    index = {"storyboard": str(out_path.resolve()),
             "pptx": str(out_path.with_suffix(".pptx").resolve()),
             "bullet_placeholders": False,
             "slides": []}

    for i, g in enumerate(groups):
        paths = [matrix[r][g["name"]]["path"] for r in roles]
        layout = pick_layout(paths, spec.get("layout"))
        tag = f"{title} · {g['name']}" if title else g["name"]
        if len(tag) > TITLE_MAX:
            print(f"WARNING: section tag > {TITLE_MAX} chars, truncated: {tag}", file=sys.stderr)
            tag = tag[:TITLE_MAX].rstrip()
        color = COLORS[i % len(COLORS)]

        lines += [f"<!-- Slide {i + 1} -->", f"<!-- layout: {layout} -->"]
        if layout == "hstack-3":
            lines.append("<!-- figures: " + ", ".join(paths) + " -->")
        lines += [f"<!-- figure-height: {fig_height} -->",
                  f'<!-- section-tag: "{tag}" color="{color}" -->',
                  f"## {tag}", ""]
        shown = paths[:1] if layout == "hstack-3" else paths
        lines += [f"![]({p})" for p in shown]
        lines += ["", "---", ""]

        num, den = (fig_height.split("/") + ["1"])[:2] if "/" in str(fig_height) else (fig_height, 1)
        index["slides"].append({
            "idx": i, "name": g["name"], "tag": [tag, color], "layout": layout,
            "figures": paths,
            "aspects": [round(aspect_of(Path(p)), 3) for p in paths],
            "figure_height": round(float(num) / float(den), 4),
        })

    out_path.write_text("\n".join(lines).rstrip() + "\n")
    idx_path = out_path.with_suffix(".index.json")
    idx_path.write_text(json.dumps(index, indent=2) + "\n")
    return idx_path


# ------------------------------------------------------------------- report

def report(matrix, spec):
    groups = [g["name"] for g in spec["groups"]]
    roles = [r["name"] for r in spec["roles"]]
    w = max([len(g) for g in groups] + [8])
    print("RESOLUTION MATRIX  (rows = slides/groups, columns = figure roles)\n")
    print("  " + "".ljust(w) + " | " + " | ".join(r for r in roles))
    bad = []
    for g in groups:
        cells = []
        for r in roles:
            c = matrix[r][g]
            if c["status"] == "ok":
                cells.append(Path(c["path"]).name)
            else:
                cells.append(f"[{c['status'].upper()}]")
                bad.append((g, r, c))
        print("  " + g.ljust(w) + " | " + " | ".join(cells))
    print()
    for g, r, c in bad:
        print(f"  {c['status'].upper()}: {g} x {r}")
        if c.get("note"):
            print(f"      {c['note']}")
        for cand in c.get("candidates", []):
            print(f"      candidate: {cand}")
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec", help="JSON spec file")
    ap.add_argument("--write", action="store_true", help="write storyboard + index.json")
    ap.add_argument("-o", "--output", help="storyboard path (overrides spec)")
    args = ap.parse_args()

    spec = json.loads(Path(args.spec).read_text())
    directory = Path(spec["dir"]).expanduser().resolve()
    if not directory.is_dir():
        raise SystemExit(f"ERROR: figure directory not found: {directory}")

    matrix = resolve_matrix(spec, directory)
    bad = report(matrix, spec)

    if bad:
        print("Unresolved cells — nothing written. Fix the spec (roles/tokens) or add "
              "\"overrides\": {\"Group|Role\": \"filename.png\"} after asking the user.")
        return 2

    if not args.write:
        print("Dry run OK. Re-run with --write to emit the storyboard.")
        return 0

    topic = spec.get("topic", "slides")
    default = Path.cwd() / f"{topic}_{_dt.date.today():%d-%m-%Y}.md"
    out = Path(args.output or spec.get("output") or default).expanduser().resolve()
    idx = write_storyboard(spec, matrix, directory, out)
    print(f"storyboard: {out}")
    print(f"index:      {idx}")
    print(f"slides:     {len(spec['groups'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
