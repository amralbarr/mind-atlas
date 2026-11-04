"""Three real chunking strategies compared on the same sample document:
fixed-size, recursive-character (structure-agnostic), and structure-aware
(splits on headings/paragraphs first).

Companion to:
- ../../interview/interview-01/01-rag.md (chunk size/overlap question)
- ../../interview/interview-01/11-rag-deep-dive.md
- ../../overviews/ai/chunking-strategies.md
"""
import re


def fixed_size_chunks(text: str, size: int = 200, overlap: int = 40) -> list[str]:
    """The simplest strategy: cut every `size` characters, overlapping by
    `overlap` characters so a sentence spanning a cut boundary isn't lost
    entirely from both resulting chunks. Blind to sentence/paragraph
    structure — a chunk can start or end mid-sentence."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start = end - overlap
        if start <= 0 or end >= len(text):
            break
    return chunks


def recursive_character_chunks(text: str, size: int = 200, overlap: int = 40) -> list[str]:
    """Tries a sequence of separators, largest unit first ("\\n\\n" for
    paragraphs, then "\\n", then ". ", then " "), splitting on the first
    separator that actually produces pieces within the size budget.
    Structure-agnostic in the sense that it doesn't know what a heading
    or a table is — it just prefers natural text boundaries over an
    arbitrary character cut."""
    separators = ["\n\n", "\n", ". ", " "]

    def split_on(text, seps):
        if not seps:
            return fixed_size_chunks(text, size, overlap)
        sep, rest = seps[0], seps[1:]
        pieces = text.split(sep)
        chunks, current = [], ""
        for piece in pieces:
            candidate = current + sep + piece if current else piece
            if len(candidate) <= size:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                current = piece if len(piece) <= size else None
                if current is None:
                    chunks.extend(split_on(piece, rest))
                    current = ""
        if current:
            chunks.append(current)
        return chunks

    return split_on(text, separators)


def structure_aware_chunks(text: str, max_size: int = 300) -> list[str]:
    """Splits on Markdown headings FIRST — every chunk stays within one
    heading section, never crossing a section boundary, which is what
    recursive-character chunking alone cannot guarantee. Falls back to
    recursive-character chunking only when a single section still
    exceeds max_size."""
    sections = re.split(r"(?=^#{1,6} .+$)", text, flags=re.MULTILINE)
    chunks = []
    for section in sections:
        section = section.strip()
        if not section:
            continue
        if len(section) <= max_size:
            chunks.append(section)
        else:
            chunks.extend(recursive_character_chunks(section, size=max_size, overlap=40))
    return chunks


SAMPLE_DOCUMENT = """# Leave Policy

Employees are entitled to 30 days of paid annual leave per year. Leave requests must be submitted at least 2 weeks in advance through the HR portal.

# Expense Reimbursement

The expense reimbursement process requires manager approval within 5 business days of submission. Receipts must be attached for any expense over $25.

# Remote Work Policy

Remote work is permitted up to 3 days per week with manager sign-off. Employees working remotely must remain reachable during core hours (10am-4pm local time).
"""


if __name__ == "__main__":
    print("=== Fixed-size (200 chars, 40 overlap) ===")
    for i, c in enumerate(fixed_size_chunks(SAMPLE_DOCUMENT, size=200, overlap=40)):
        print(f"  [{i}] {c[:80]!r}...")

    print("\n=== Recursive-character (200 chars) ===")
    for i, c in enumerate(recursive_character_chunks(SAMPLE_DOCUMENT, size=200, overlap=40)):
        print(f"  [{i}] {c[:80]!r}...")

    print("\n=== Structure-aware (splits on headings first) ===")
    for i, c in enumerate(structure_aware_chunks(SAMPLE_DOCUMENT, max_size=300)):
        print(f"  [{i}] {c[:80]!r}...")
