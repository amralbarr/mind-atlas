#!/usr/bin/env python3
"""
One-off repair for a bug in an earlier version of link_sweep.py: when a file's
own name (e.g. "Azure AI Search") was correctly excluded from self-linking,
a SHORTER unrelated term (e.g. "Azure") was still free to match the first
word of that self-reference, producing "[Azure](azure.md) AI Search" instead
of leaving the plain self-reference alone.

This scans every concept/overview file (the only files that have "own
terms"), and for each own-term, finds any place where the own-term's first
word got wrapped in a link immediately followed by the rest of the own-term
as plain text -- and unwraps it back to plain text.

link_sweep.py itself has already been fixed (own_term_spans) so this bug
cannot be produced again by a future run; this script only cleans up
instances already written to disk by the earlier, buggy run.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from link_sweep import ROOT, build_index  # noqa: E402


def main():
    apply = "--apply" in sys.argv
    term_to_files, file_to_terms = build_index()

    total_found = 0
    for md_path, own_terms in file_to_terms.items():
        text = md_path.read_text(encoding="utf-8")
        original = text
        for term in own_terms:
            if " " not in term:
                continue
            first, rest = term.split(" ", 1)
            pattern = re.compile(r"\[" + re.escape(first) + r"\]\([^)]+\)" + re.escape(" " + rest))
            matches = list(pattern.finditer(text))
            for m in reversed(matches):
                total_found += 1
                print(f"{md_path.relative_to(ROOT)}: '{m.group(0)}' -> '{term}'")
                text = text[:m.start()] + term + text[m.end():]
        if text != original and apply:
            md_path.write_text(text, encoding="utf-8")

    print(f"\n{'Fixed' if apply else 'Found'} {total_found} self-link-bleed instance(s).")


if __name__ == "__main__":
    main()
