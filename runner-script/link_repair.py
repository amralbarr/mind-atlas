#!/usr/bin/env python3
"""
Repairs EXISTING markdown links whose relative path doesn't resolve, by
locating the real file elsewhere in the vault (matched by basename) and
rewriting the link to the correct relative path from the linking file's
own directory.

This is the counterpart to link_sweep.py, which only ever ADDS a new link
to previously-bare text and never touches an existing link whether it's
correct or broken. This script's whole job is the opposite: fixing links
that already exist but point at the wrong place -- the long-standing
"wrong ../ depth" bug found repeatedly across this handbook (a file
written as if it were one directory level shallower/deeper than it
actually is).

Conservative by design:
- a broken link is only auto-repaired when exactly ONE file in the
  scanned tree matches its basename -- 0 or 2+ candidates are reported,
  never guessed
- only the PATH is rewritten; the link TEXT is left untouched
- an anchor (#section) on the original link is preserved verbatim
- a link whose target is a directory (common in README.md-style folder
  links) is left alone -- only missing FILES are "broken" here
- every repair is re-verified against the real filesystem before the run
  is considered clean, same discipline as link_sweep.py

Usage:
    python3 link_repair.py                # dry run, writes a report only
    python3 link_repair.py --apply        # applies the fixes to disk
    python3 link_repair.py --apply --file <path>   # scope to one file
"""
import argparse
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # .../mind-atlas/

# mind-atlas is multi-domain (engineering/, marketing/, finance/, ...) rather
# than one flat vault, so scanning is repo-wide by directory name rather than
# a fixed content-type list scoped to a single domain.
EXCLUDE_DIR_NAMES = {"runner-script", ".git"}

LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")


def iter_scan_files():
    for p in ROOT.rglob("*.md"):
        if EXCLUDE_DIR_NAMES & set(p.relative_to(ROOT).parts[:-1]):
            continue
        yield p


def build_basename_index():
    index = {}
    for p in iter_scan_files():
        index.setdefault(p.name, []).append(p)
    return index


def is_code_protected(text, start, end):
    for rx in (FENCE_RE, INLINE_CODE_RE):
        for m in rx.finditer(text):
            if start >= m.start() and end <= m.end():
                return True
    return False


def repair_file(path, basename_index):
    text = path.read_text(encoding="utf-8")
    original = text
    changes = []
    unresolved = []

    matches = list(LINK_RE.finditer(text))
    for m in reversed(matches):  # reverse so earlier offsets stay valid as we edit
        link_text, target = m.group(1), m.group(2)
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        if is_code_protected(text, m.start(), m.end()):
            continue

        anchor = ""
        path_part = target
        if "#" in target:
            path_part, anchor = target.split("#", 1)
            anchor = "#" + anchor
        if not path_part:
            continue  # pure same-file anchor link

        resolved = (path.parent / path_part).resolve()
        if resolved.is_file() or resolved.is_dir():
            continue  # already correct (directory links are valid targets here)

        basename = Path(path_part).name
        candidates = basename_index.get(basename, [])
        if len(candidates) == 1:
            new_rel = os.path.relpath(candidates[0], start=path.parent).replace(os.sep, "/")
            new_target = new_rel + anchor
            new_link = f"[{link_text}]({new_target})"
            text = text[: m.start()] + new_link + text[m.end() :]
            changes.append({
                "line": original.count("\n", 0, m.start()) + 1,
                "old": target,
                "new": new_target,
            })
        else:
            unresolved.append({
                "line": original.count("\n", 0, m.start()) + 1,
                "target": target,
                "candidates": len(candidates),
            })

    return text, changes, unresolved


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="Write fixes to disk (default is dry-run).")
    ap.add_argument("--file", action="append", help="Restrict to this file only (repeatable).")
    ap.add_argument("--report", default=str(ROOT / "runner-script" / "link_repair_report.md"))
    args = ap.parse_args()

    basename_index = build_basename_index()

    if args.file:
        files = []
        for f in args.file:
            p = Path(f)
            if not p.is_absolute():
                p = ROOT / f
            if not p.is_file():
                print(f"--file target not found: {f}", file=sys.stderr)
                sys.exit(1)
            files.append(p.resolve())
    else:
        files = sorted(set(iter_scan_files()))

    all_changes = []
    all_unresolved = []
    verify_failures = []

    for path in files:
        new_text, changes, unresolved = repair_file(path, basename_index)
        if changes:
            all_changes.append((path, changes))
            if args.apply:
                path.write_text(new_text, encoding="utf-8")
                for c in changes:
                    target_path = c["new"].split("#")[0]
                    if target_path and not (path.parent / target_path).resolve().is_file():
                        verify_failures.append((path, c))
        if unresolved:
            all_unresolved.append((path, unresolved))

    total_changes = sum(len(c) for _, c in all_changes)
    total_unresolved = sum(len(u) for _, u in all_unresolved)

    lines = [
        "# Link Repair Report",
        "",
        f"Mode: {'APPLY' if args.apply else 'DRY RUN'}",
        f"Scanned files: {len(files)}",
        f"Links {'fixed' if args.apply else 'proposed'}: {total_changes}",
        f"Unresolved (0 or 2+ basename candidates): {total_unresolved}",
        "",
    ]
    if all_changes:
        lines.append("## Fixed")
        for path, changes in all_changes:
            lines.append(f"### {path.relative_to(ROOT)}")
            for c in changes:
                lines.append(f"- line {c['line']}: `{c['old']}` -> `{c['new']}`")
        lines.append("")
    if all_unresolved:
        lines.append("## Unresolved -- needs manual attention")
        for path, unresolved in all_unresolved:
            lines.append(f"### {path.relative_to(ROOT)}")
            for u in unresolved:
                lines.append(f"- line {u['line']}: `{u['target']}` ({u['candidates']} basename candidate(s))")
        lines.append("")
    if verify_failures:
        lines.append("## VERIFICATION FAILURES")
        for path, c in verify_failures:
            lines.append(f"- {path.relative_to(ROOT)}: `{c['new']}` does not resolve")

    Path(args.report).write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote report to {args.report}")
    print(f"{'Fixed' if args.apply else 'Proposed'} {total_changes} link(s). {total_unresolved} unresolved.")
    if verify_failures:
        print(f"WARNING: {len(verify_failures)} verification failure(s)!", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
