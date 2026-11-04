#!/usr/bin/env python3
"""
Fixes a specific redundant pattern: an acronym and its own parenthetical
expansion BOTH linked separately to the SAME target file, right next to
each other -- e.g. "[HMAC](hmac.md) ([Hash-based Message Authentication
Code](hmac.md))". The second link adds nothing (same destination) and
just looks like a double-click redundancy. Collapses it to one link +
plain parenthetical text: "[HMAC](hmac.md) (Hash-based Message
Authentication Code)".

Matches both orderings: "ACRONYM (Expansion)" and "Expansion (ACRONYM)" --
whichever one is already linked stays linked; the one in parens loses its
link syntax but keeps its text.

Usage:
    python3 collapse_double_links.py                # dry run, report only
    python3 collapse_double_links.py --apply         # applies the fix
"""
import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCAN_DIRS = ["concepts", "overviews", "guides", "interview", "learning", "commands", "installation"]
SCAN_EXTRA_FILES = ["README.md"]

# [TEXT1](TARGET) (SOMETHING)[TEXT2](TARGET2))  -- outer link, then a
# parenthetical that itself contains another link, both resolving to the
# same TARGET (compared after normalization, see same_target()).
PATTERN = re.compile(
    r"\[([^\]]+)\]\(([^)]+)\)"   # first link: text1, target1
    r"\s\("                       # a literal " ("
    r"\[([^\]]+)\]\(([^)]+)\)"   # second link: text2, target2
    r"\)"                         # closing paren
)


def normalize_target(t: str) -> str:
    return t.split("#")[0].rstrip("/")


def same_target(t1: str, t2: str) -> bool:
    return normalize_target(t1) == normalize_target(t2)


def fix_text(text: str) -> tuple[str, int]:
    count = 0

    def repl(m):
        nonlocal count
        text1, target1, text2, target2 = m.group(1), m.group(2), m.group(3), m.group(4)
        if not same_target(target1, target2):
            return m.group(0)
        count += 1
        return f"[{text1}]({target1}) ({text2})"

    new_text = PATTERN.sub(repl, text)
    return new_text, count


def iter_files():
    for d in SCAN_DIRS:
        base = ROOT / d
        if base.exists():
            yield from base.rglob("*.md")
    for f in SCAN_EXTRA_FILES:
        p = ROOT / f
        if p.exists():
            yield p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    total = 0
    touched = 0
    for path in sorted(set(iter_files())):
        text = path.read_text(encoding="utf-8")
        new_text, count = fix_text(text)
        if count:
            total += count
            touched += 1
            print(f"{path.relative_to(ROOT)}: {count} double-link(s) collapsed")
            if args.apply:
                path.write_text(new_text, encoding="utf-8")

    print(f"\n{'Fixed' if args.apply else 'Found'} {total} double-link(s) across {touched} file(s).")


if __name__ == "__main__":
    main()
