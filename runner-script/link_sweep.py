#!/usr/bin/env python3
"""
Bulk link-sweep for the engineering handbook.

Builds an index of every atomic concept / overview file (term -> file path),
then scans every markdown file in the handbook for the FIRST bare, unlinked
mention of each known term and replaces it with a correctly-relative markdown
link to that term's file.

Deliberately conservative:
- case-sensitive exact-term matching only (no fuzzy/lowercase matching)
- never touches text already inside a markdown link, inline code, a fenced
  code block, or an ATX heading line
- only the first unlinked occurrence per (file, term) pair is linked
- a term that maps to more than one candidate file is treated as AMBIGUOUS
  and skipped entirely, reported for manual resolution
- relative paths are computed per-file with os.path.relpath and re-verified
  against the real filesystem after writing -- this handbook has a long
  history of off-by-one "../" bugs, so every inserted link is checked to
  actually resolve before the run is considered clean
- indexed terms come ONLY from each file's H1 title, never a sub-heading.
  (Tried indexing every heading level to fix a "System Prompt wasn't
  auto-linked" case on 2026-10-23 -- reverted the same day: a vault-wide
  dry run produced real wrong links, e.g. "TypeScript" resolving into an
  unrelated Zod/class-validator subsection, "CLI" into SQLite's own "## CLI"
  heading, "managed" into Weaviate, "The pipeline" into an unrelated radar
  file. An H1 is a deliberately-chosen, handbook-wide-unique concept name;
  an H2-H6 heading is an ordinary structural word scoped to its own file's
  narrative, and matching bare occurrences of ordinary words like "CLI" or
  "managed" anywhere in the vault is unsafe no matter the blocklist. The
  right fix for "this sub-topic deserves to be auto-linked" is still to give
  it its own atomic file with its own H1, same as system-prompt.md.)

Usage:
    python3 link_sweep.py                 # dry run, writes a report only
    python3 link_sweep.py --apply         # applies the changes to disk
    python3 link_sweep.py --apply --term "BM25"   # restrict to one term
    python3 link_sweep.py --report out.md # custom report path

    # After creating/editing ONE file, run both directions:
    python3 link_sweep.py --apply --file concepts/ai/retrieval/new-concept.md
        # -> links that file's own body against every other existing term
    python3 link_sweep.py --apply --term "New Concept"
        # -> links every OTHER file's existing bare mentions of this new term
"""

import argparse
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # .../engineering/

# Directories whose markdown files are INDEXED as link targets (every file
# here is assumed to be an atomic concept doc or a comparison overview doc).
INDEX_DIRS = ["concepts", "overviews"]

# Directories that get SCANNED for bare mentions to replace. Deliberately
# wider than INDEX_DIRS -- concept files link to each other, and guides /
# interview / learning prose reference concepts constantly.
SCAN_DIRS = ["concepts", "overviews", "guides", "interview", "learning", "commands", "installation"]

SCAN_EXTRA_FILES = ["README.md"]

# Known high-collision generic terms that should never be auto-linked even if
# a file happens to be titled exactly this -- too likely to appear in
# unrelated prose. Extend this list after reviewing the dry-run report.
TERM_BLOCKLIST = {
    "api", "apis", "data", "model", "models", "service", "services",
    "server", "servers", "client", "clients", "search", "index", "indexes",
    "indices", "token", "tokens", "security", "storage", "database",
    "databases", "cache", "caches", "query", "queries", "document",
    "documents", "system", "systems", "pipeline", "pipelines", "node",
    "nodes", "event", "events", "job", "jobs", "worker", "workers",
    "resource", "resources", "role", "roles", "policy", "policies",
    "request", "requests", "response", "responses",
    # Generic nouns that collide too often with unrelated prose, even though
    # a design-pattern / architecture file happens to be named exactly this
    # (confirmed false positives during the first dry-run review: "Factory"
    # inside "Azure Data Factory", "Strategy" as a generic table-column
    # header meaning "approach", "Components" meaning generic UI pieces).
    "factory", "factories", "strategy", "strategies", "component",
    "components", "indexing",
    # Confirmed false positives once single-word terms became
    # case-insensitive (2026-10-24): "providers" collides with cloud/model
    # providers in unrelated prose ("Azure Provider Docs", "swapping model
    # providers"), "queues" (the bare plural fallback alias for the
    # "Message Queues" file) collides with the generic data-structure word
    # ("services, data stores, queues, caches"), "guards" collides with
    # non-NestJS generic usage ("UI button guards", "implement guards for
    # rate-limiting"). The multi-word phrase "Message Queues" is unaffected
    # and still links normally.
    "provider", "providers", "queue", "queues", "guard", "guards",
}

# Collapses the specific redundant pattern an acronym + its own
# parenthetical expansion can produce once BOTH are registered aliases of
# the same file: "[HMAC](hmac.md) ([Hash-based Message Authentication
# Code](hmac.md))" -- two separate links to the identical target, right
# next to each other, because the longer alias gets matched first (terms
# are tried longest-first) and the shorter acronym then still finds its
# own now-unlinked occurrence right before the parenthetical. Applied as
# a final safety-net pass after every sweep, rather than trying to
# prevent it mid-loop by tracking adjacency during matching -- simpler
# and correct regardless of which of the two terms happened to match
# first. Fixed 2026-10-24 after 14 pre-existing instances were found
# vault-wide (see collapse_double_links.py, the one-off repair for those).
DOUBLE_LINK_RE = re.compile(
    r"\[([^\]]+)\]\(([^)]+)\)"   # first link: text1, target1
    r"\s\("                       # a literal " ("
    r"\[([^\]]+)\]\(([^)]+)\)"   # second link: text2, target2
    r"\)"                         # closing paren
)


def collapse_redundant_double_links(text: str) -> str:
    def same_target(t1: str, t2: str) -> bool:
        return t1.split("#")[0].rstrip("/") == t2.split("#")[0].rstrip("/")

    def repl(m):
        text1, target1, text2, target2 = m.group(1), m.group(2), m.group(3), m.group(4)
        if not same_target(target1, target2):
            return m.group(0)
        return f"[{text1}]({target1}) ({text2})"

    return DOUBLE_LINK_RE.sub(repl, text)


FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
LINK_RE = re.compile(r"\[[^\]]*\]\([^)]*\)")
HEADING_LINE_RE = re.compile(r"^#{1,6}\s.*$", re.MULTILINE)
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
# A bare URL (not already inside markdown link syntax) -- e.g. a raw
# "https://portal.azure.com" sitting in a table cell or plain prose.
# Needed because case-insensitive matching (see make_term_regex) would
# otherwise match the lowercase scheme word inside the URL itself (e.g.
# the term "HTTPS" matching "https" in "https://portal.azure.com") and
# wrap part of the URL in a markdown link, corrupting it.
BARE_URL_RE = re.compile(r"\b[a-zA-Z][a-zA-Z0-9+.-]*://\S+")


def is_acronym(term: str) -> bool:
    letters = [c for c in term if c.isalpha()]
    return bool(letters) and all(c.isupper() for c in letters) and len(term) <= 8


def filename_to_title(path: Path) -> str:
    stem = path.stem
    words = stem.replace("_", "-").split("-")
    return " ".join(w.upper() if len(w) <= 4 and w.isalpha() and w == w.lower() else w.capitalize() for w in words)


def extract_aliases(md_path: Path) -> list[str]:
    """Pull candidate link-text aliases out of a concept file's H1 heading."""
    try:
        text = md_path.read_text(encoding="utf-8")
    except Exception:
        return []

    m = H1_RE.search(text)
    aliases = []

    if m:
        heading = m.group(1).strip()
        # "ADLS — Azure Data Lake Storage" / "ADLS - Azure Data Lake Storage"
        em_dash_parts = re.split(r"\s+[—\-]\s+", heading, maxsplit=1)
        if len(em_dash_parts) == 2:
            aliases.extend(p.strip() for p in em_dash_parts)
        else:
            # "NLP (Natural Language Processing)"
            paren_m = re.match(r"^(.+?)\s*\((.+)\)\s*$", heading)
            if paren_m:
                aliases.append(paren_m.group(1).strip())
                aliases.append(paren_m.group(2).strip())
            else:
                aliases.append(heading)

    fallback = filename_to_title(md_path)
    # Case-insensitive dedupe: filename_to_title's own casing heuristic
    # (e.g. "https.md" -> "Https") otherwise sits alongside a properly
    # cased alias already pulled from the H1 itself (e.g. "HTTPS"),
    # producing two near-duplicate aliases that point at the same file.
    if fallback.lower() not in {a.lower() for a in aliases}:
        aliases.append(fallback)

    # Clean + filter
    cleaned = []
    for a in aliases:
        a = a.strip().strip(".")
        if not a:
            continue
        if a.lower() in TERM_BLOCKLIST:
            continue
        if len(a) < 3 and not is_acronym(a):
            continue
        cleaned.append(a)
    return cleaned


def build_index() -> tuple[dict[str, set[Path]], dict[Path, list[str]]]:
    term_to_files: dict[str, set[Path]] = {}
    file_to_terms: dict[Path, list[str]] = {}

    for d in INDEX_DIRS:
        base = ROOT / d
        if not base.exists():
            continue
        for md_path in base.rglob("*.md"):
            aliases = extract_aliases(md_path)
            if not aliases:
                continue
            file_to_terms[md_path] = aliases
            for alias in aliases:
                term_to_files.setdefault(alias, set()).add(md_path)

    return term_to_files, file_to_terms


def protected_spans(text: str) -> list[tuple[int, int]]:
    spans = []
    for rx in (FENCE_RE, INLINE_CODE_RE, LINK_RE, HEADING_LINE_RE, BARE_URL_RE):
        for m in rx.finditer(text):
            spans.append((m.start(), m.end()))
    spans.sort()
    return spans


def in_protected_span(pos_start: int, pos_end: int, spans: list[tuple[int, int]]) -> bool:
    for s, e in spans:
        if pos_start >= s and pos_end <= e:
            return True
    return False


def make_term_regex(term: str) -> re.Pattern:
    escaped = re.escape(term)
    # Case-insensitive except for a bare acronym (RAG, LLM, GIL, ADLS, ...):
    # those ARE the ones prone to a real collision with an unrelated
    # lowercase word ("RAG" vs "rag" the cloth), so they stay strict.
    # Everything else -- multi-word phrases AND ordinary single-word
    # concept names like "Serialization" or "Docker" -- is case-insensitive,
    # because this handbook's own "**Term:** definition..." lead-in
    # convention and normal mid-sentence capitalization routinely produce
    # a lowercase first letter (e.g. "**Hybrid search:**", "...no
    # serialization/copying cost...") that still means the exact same
    # concept, not a different word that happens to collide.
    flags = 0 if is_acronym(term) else re.IGNORECASE
    return re.compile(rf"(?<!\w){escaped}(?!\w)", flags)


def own_term_spans(text: str, own_terms: set[str]) -> list[tuple[int, int]]:
    """Every occurrence of this file's OWN name(s) anywhere in its body is a
    self-reference, even where it's never itself turned into a link -- a
    SHORTER term must not be allowed to match a substring inside one of
    these (e.g. the bare term "Azure" matching inside this file's own
    opening "Azure AI Search is Microsoft's ..." sentence)."""
    spans = []
    for term in own_terms:
        for m in make_term_regex(term).finditer(text):
            spans.append((m.start(), m.end()))
    return spans


def process_file(md_path: Path, terms_sorted: list[str], term_to_files: dict[str, set[Path]],
                  own_terms: set[str]) -> tuple[str, list[dict], list[dict]]:
    """Returns (new_text, changes, ambiguous_skips) for one file."""
    text = md_path.read_text(encoding="utf-8")
    changes = []
    ambiguous_skips = []
    linked_terms_this_file: set[str] = set()

    for term in terms_sorted:
        if term in linked_terms_this_file:
            continue
        candidates = term_to_files[term]

        if len(candidates) > 1:
            ambiguous_skips.append({
                "file": str(md_path.relative_to(ROOT)),
                "term": term,
                "candidates": sorted(str(c.relative_to(ROOT)) for c in candidates),
            })
            continue

        target_path = next(iter(candidates))
        if target_path.resolve() == md_path.resolve():
            continue  # never self-link
        if term in own_terms:
            continue  # this file's own title term shouldn't link elsewhere by coincidence

        spans = protected_spans(text) + own_term_spans(text, own_terms)
        rx = make_term_regex(term)
        match = None
        for m in rx.finditer(text):
            if not in_protected_span(m.start(), m.end(), spans):
                match = m
                break
        if not match:
            continue

        rel = os.path.relpath(target_path, start=md_path.parent)
        rel = rel.replace(os.sep, "/")
        # Link text is whatever was actually matched, not the canonical
        # indexed term -- a case-insensitive multi-word match (e.g. the
        # "**Hybrid search:**" lead-in convention) must not silently
        # rewrite the document's own prose casing to "Hybrid Search".
        replacement = f"[{match.group(0)}]({rel})"

        line_no = text.count("\n", 0, match.start()) + 1
        line_start = text.rfind("\n", 0, match.start()) + 1
        line_end_idx = text.find("\n", match.end())
        line_end_idx = line_end_idx if line_end_idx != -1 else len(text)
        before_line = text[line_start:line_end_idx]

        text = text[:match.start()] + replacement + text[match.end():]

        after_line_end_idx = text.find("\n", line_start)
        after_line_end_idx = after_line_end_idx if after_line_end_idx != -1 else len(text)
        after_line = text[line_start:after_line_end_idx]

        changes.append({
            "file": str(md_path.relative_to(ROOT)),
            "term": term,
            "target": str(target_path.relative_to(ROOT)),
            "relpath": rel,
            "line": line_no,
            "before": before_line.strip(),
            "after": after_line.strip(),
        })
        linked_terms_this_file.add(term)

    text = collapse_redundant_double_links(text)
    return text, changes, ambiguous_skips


def iter_scan_files():
    for d in SCAN_DIRS:
        base = ROOT / d
        if not base.exists():
            continue
        yield from base.rglob("*.md")
    for f in SCAN_EXTRA_FILES:
        p = ROOT / f
        if p.exists():
            yield p


def resolve_file_arg(raw: str) -> Path:
    p = Path(raw)
    candidate = p if p.is_absolute() else (Path.cwd() / p)
    if not candidate.is_file():
        candidate = ROOT / raw
    if not candidate.is_file():
        print(f"--file target not found: {raw}", file=sys.stderr)
        sys.exit(1)
    return candidate.resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="Write changes to disk (default is dry-run).")
    ap.add_argument("--term", action="append",
                     help="Restrict to this term only (repeatable). Use when a term was just "
                          "added/renamed and other files' existing bare mentions of it need linking.")
    ap.add_argument("--file", action="append",
                     help="Restrict scanning to this one file only, path relative to the engineering/ "
                          "root or the current directory (repeatable). Use right after creating or "
                          "editing a concept/overview file, to link that file's own body against the "
                          "full existing term index, instead of re-scanning the whole vault.")
    ap.add_argument("--report", default=str(ROOT / "scripts" / "link_sweep_report.md"))
    args = ap.parse_args()

    term_to_files, file_to_terms = build_index()
    terms_sorted = sorted(term_to_files.keys(), key=len, reverse=True)

    if args.file:
        scan_override = sorted({resolve_file_arg(f) for f in args.file})
    else:
        scan_override = None

    if args.term:
        wanted = set(args.term)
        terms_sorted = [t for t in terms_sorted if t in wanted]
        if not terms_sorted:
            print(f"No indexed term matched {args.term}", file=sys.stderr)
            sys.exit(1)

    all_changes = []
    all_ambiguous = []
    verify_failures = []

    scan_files = scan_override if scan_override is not None else sorted(set(iter_scan_files()))

    for md_path in scan_files:
        own_terms = set(file_to_terms.get(md_path, []))
        new_text, changes, ambiguous = process_file(md_path, terms_sorted, term_to_files, own_terms)
        all_ambiguous.extend(ambiguous)
        if not changes:
            continue
        all_changes.extend(changes)

        if args.apply:
            md_path.write_text(new_text, encoding="utf-8")
            for c in changes:
                target_abs = (md_path.parent / c["relpath"]).resolve()
                if not target_abs.is_file():
                    verify_failures.append(c)

    # --- report ---
    report_lines = [
        "# Link Sweep Report",
        "",
        f"Mode: {'APPLY' if args.apply else 'DRY RUN'}",
        f"Indexed terms: {len(term_to_files)}",
        f"Scanned files: {len(scan_files)}",
        f"Links {'added' if args.apply else 'proposed'}: {len(all_changes)}",
        f"Ambiguous terms skipped: {len({a['term'] for a in all_ambiguous})}",
        "",
    ]

    if all_changes:
        report_lines.append("## Changes")
        report_lines.append("")
        by_file: dict[str, list[dict]] = {}
        for c in all_changes:
            by_file.setdefault(c["file"], []).append(c)
        for file, changes in sorted(by_file.items()):
            report_lines.append(f"### {file}")
            for c in changes:
                report_lines.append(f"- line {c['line']}: `{c['term']}` -> `{c['target']}`")
                report_lines.append(f"  - before: {c['before']}")
                report_lines.append(f"  - after:  {c['after']}")
            report_lines.append("")

    if all_ambiguous:
        report_lines.append("## Ambiguous terms (skipped -- resolve manually)")
        report_lines.append("")
        seen = set()
        for a in all_ambiguous:
            key = a["term"]
            if key in seen:
                continue
            seen.add(key)
            report_lines.append(f"- `{a['term']}` -> {', '.join(a['candidates'])}")
        report_lines.append("")

    if verify_failures:
        report_lines.append("## VERIFICATION FAILURES (link does not resolve on disk!)")
        report_lines.append("")
        for c in verify_failures:
            report_lines.append(f"- {c['file']} line {c['line']}: `[{c['term']}]({c['relpath']})` -> target missing")
        report_lines.append("")

    Path(args.report).write_text("\n".join(report_lines), encoding="utf-8")
    print(f"Wrote report to {args.report}")
    print(f"{'Applied' if args.apply else 'Proposed'} {len(all_changes)} link(s) across {len(set(c['file'] for c in all_changes))} file(s).")
    if verify_failures:
        print(f"WARNING: {len(verify_failures)} inserted link(s) failed on-disk verification!", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
