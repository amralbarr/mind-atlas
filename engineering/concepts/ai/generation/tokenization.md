# Tokenization

## What is it?

Tokenization is the step that turns raw text into the sequence of integers an [LLM](llm.md) actually operates on. A **tokenizer** splits text into **tokens** — sometimes a whole word, sometimes a word fragment, sometimes a single character or byte — and maps each one to an ID in a fixed **vocabulary**. Everything an [LLM](llm.md) does — reading a prompt, generating a response, being billed per API call — happens in units of tokens, not words or characters.

```
Text:   "Tokenization isn't always intuitive."
         ↓ tokenizer
Tokens: ["Token", "ization", " isn", "'t", " always", " intuit", "ive", "."]
         ↓ vocabulary lookup
IDs:    [7369, 1634, 4536, 470, 1855, 51033, 425, 13]
```

A rough rule of thumb for English text: **1 token ≈ 4 characters ≈ ¾ of a word**. Code, non-English languages, and unusual formatting ([JSON](../../programming/fundamentals/json.md), tables, rare Unicode) typically tokenize far less efficiently than plain English prose — the same sentence can cost noticeably more tokens depending on language and structure.

## Why subword tokenization, not whole words

Splitting on whole words seems natural but breaks down fast:
- The vocabulary would need an entry for every word that could ever appear (including typos, made-up words, and every language) — impractically large, and anything missing becomes an unrecoverable "unknown token."
- Splitting on individual characters avoids that problem but produces very long token sequences and forces the model to learn word structure from scratch every time.

**Subword tokenization** is the middle ground almost every modern [LLM](llm.md) uses: common whole words get their own single token (`"the"`, `"and"`), while rarer or unfamiliar words get split into smaller familiar pieces (`"tokenization"` → `"Token"` + `"ization"`). This keeps the vocabulary a manageable size (tens of thousands of entries) while still being able to represent any string, including words the tokenizer has never seen.

## Byte-Pair Encoding (BPE)

**Byte-Pair Encoding (BPE)** is the de facto standard algorithm behind this. It's built once, offline, from a large text corpus:

1. Start with a base vocabulary of individual characters (or, in byte-level BPE, the 256 possible byte values).
2. Find the most frequently occurring adjacent pair of tokens in the training corpus and merge it into a new single token.
3. Repeat step 2 thousands of times, growing the vocabulary one merge at a time, until it reaches a target size (commonly 30,000–100,000+ tokens).

The result is a vocabulary where frequent words and fragments ("the", "-tion", "-ing") are single tokens, and rare or unseen text falls back to smaller, more granular pieces.

**Byte-level BPE** (popularized by GPT-2, and used by the GPT-3/4/5 and Llama 3+ families) uses raw bytes rather than Unicode characters as its base alphabet. This sidesteps the "unknown token" problem entirely — since any string is just a sequence of bytes, any input, including emoji, unusual scripts, or malformed text, can always be tokenized, even if inefficiently.

Different model families ship different tokenizers (OpenAI's `tiktoken`, Google's SentencePiece, Llama's own BPE variant) — a token count from one model's tokenizer doesn't transfer to another, and the same text can produce meaningfully different token counts across models.

## Why token counts matter

Tokens are the unit almost every practical constraint is measured in:

| Concern | How tokens matter |
|---|---|
| **Cost** | API pricing is quoted per token (e.g. per 1M [input/output](../../programming/fundamentals/io.md) tokens) — see [llm.md](llm.md)'s cost estimation section for a worked example |
| **[Context window](context-window.md)** | The model's maximum input+output capacity is a token count, not a word count — see [Context Window](context-window.md) |
| **Latency** | Generation time scales with output token count, since most [LLMs](llm.md) generate one token at a time |
| **Chunking** | Document [chunking strategies](../../../overviews/ai/chunking-strategies.md) (see [Document Indexing](../ingestion/document-indexing.md)) are usually sized in tokens, not characters, so chunks fit predictably within a model's limits |

A prompt that "looks short" in characters can still be token-expensive — dense code, tables, or non-English text often need more tokens per character than plain English prose. Estimating token count before sending a request (via a tokenizer library rather than guessing from character count) is standard practice for cost-sensitive pipelines.

## Practical example (Python)

```python
import tiktoken

encoding = tiktoken.encoding_for_model("gpt-4o")
tokens = encoding.encode("Tokenization isn't always intuitive.")

print(len(tokens))        # e.g. 8
print(tokens)              # [7369, 1634, 4536, 470, 1855, 51033, 425, 13]
print(encoding.decode(tokens))  # "Tokenization isn't always intuitive."
```

Counting tokens locally with the right tokenizer (rather than estimating) is the only reliable way to predict cost or check whether a prompt will fit a model's [context window](context-window.md) before making the API call.

## Related

- [Large Language Models (LLMs)](llm.md) — see its "Token limit" section for how token limits played out for one specific project
- [Context Window](context-window.md) — the architectural concept token limits define
- [Document Indexing Pipeline](../ingestion/document-indexing.md) — [chunking strategies](../../../overviews/ai/chunking-strategies.md) sized in tokens
- [Embeddings](../ingestion/embeddings.md) — embedding API costs are also billed per token
