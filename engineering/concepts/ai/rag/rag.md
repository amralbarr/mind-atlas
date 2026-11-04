# Retrieval-Augmented Generation (RAG)

## What is it?

RAG (Retrieval-Augmented Generation) is an AI technique that combines two things:
1. **Retrieval:** Finding the most relevant documents/chunks for a question (from a pre-built index)
2. **Generation:** Using an [LLM](../generation/llm.md) (Large Language Model) to write a natural-language answer based on the retrieved content

The result: a user types a question in plain English, and the system returns a direct, accurate answer — sourced from the organization's own internal documents — along with references to which documents were used. Because it answers plain-English questions, RAG is also what powers "natural-language search" over internal document sets.

## Why RAG instead of just using an LLM?

| Without RAG | With RAG |
|---|---|
| [LLM](../generation/llm.md) only knows what it was trained on | [LLM](../generation/llm.md) answers based on YOUR specific documents |
| Cannot access private internal documents | Reads from the internal Nextcloud index |
| May hallucinate (invent facts) | Answer is grounded in retrieved evidence |
| No document references | Returns which documents the answer came from |
| Sending all docs to [LLM](../generation/llm.md) = expensive + slow | Only relevant chunks are sent to the [LLM](../generation/llm.md) |

## The RAG flow

```
User types a question:
"What is the 2026 project budget for Project A?"
         ↓
1. QUERY PROCESSING
   — Convert question to an embedding vector
         ↓
2. RETRIEVAL
   — Search the vector index for chunks with similar embeddings
   — Retrieve top-N most relevant chunks
         ↓
3. PERMISSION FILTER  ← CRITICAL SECURITY STEP
   — Remove any chunks the current user is not authorized to access
   — Only authorized chunks proceed
         ↓
4. PROMPT CONSTRUCTION
   — Build a prompt:
     "Answer based only on the following context: [chunks]
      Question: What is the 2026 project budget for Project A?"
         ↓
5. LLM GENERATION
   — LLM reads the context and generates a natural-language answer
         ↓
6. RESPONSE TO USER
   — Answer + document references (filename, department)
   — "Based on Projects_ProjectA_Plan.txt: The 2026 budget for Project A is..."
```

## The critical security rule

**WRONG approach:**
```
User → Retrieve ALL documents → LLM → Answer
```

**CORRECT approach:**
```
User
 ↓
Authenticate (who are you?)
 ↓
Authorize (what are you allowed to see?)
 ↓
Retrieve ONLY authorized documents
 ↓
LLM generates answer from authorized content only
 ↓
Answer
```

If this rule is violated, a Finance user could ask the AI "What is the HR salary policy?" and receive the answer — even though they have no permission to see HR documents. The AI becomes an [authorization](../../security/authorization/authorization.md) bypass.

## Permission-aware retrieval

Each chunk in the index stores `allowed_groups`. During retrieval:

```python
user_groups = get_user_groups(username)   # e.g., ["Finance", "Projects"]

results = vector_store.search(
    query_embedding=embed(question),
    filter={"allowed_groups": {"$in": user_groups}}  # metadata filter
)
# Only chunks accessible to this user are returned
```

## RAG components

| Component | What it does | Tools used |
|---|---|---|
| **Embedding Model** | Converts text to vectors | sentence-transformers, OpenAI [embeddings](../ingestion/embeddings.md), [Azure](../../cloud/azure/azure.md) OpenAI |
| **Vector Store** | Stores and searches [embeddings](../ingestion/embeddings.md) | [ChromaDB](../retrieval/vector-stores/chromadb.md), [FAISS](../retrieval/vector-stores/faiss.md), [Qdrant](../retrieval/vector-stores/qdrant.md) |
| **Retriever** | Finds top-N relevant chunks for a query | Built on top of the vector store |
| **Permission Filter** | Removes unauthorized chunks from results | Custom code using group metadata |
| **[LLM](../generation/llm.md)** | Generates the final natural-language answer | GPT-4o, [Azure](../../cloud/azure/azure.md) OpenAI, Ollama (local) |
| **Prompt Template** | Structures the context + question for the [LLM](../generation/llm.md) | Custom template |

## Example interaction

```
User (finance_user): "What was the Q3 revenue?"

System:
1. Embeds question
2. Searches index → finds chunks from Finance_Q3_Report_2026.txt
3. Checks: finance_user ∈ Finance group → Finance docs allowed ✓
4. Sends chunks to LLM
5. LLM responds: "Q3 revenue was 2.4M, exceeding the target by 12%."
   Source: Finance_Q3_Report_2026.txt

User (finance_user): "What is the HR salary policy?"

System:
1. Embeds question
2. Searches index → finds chunks from HR_Salary_Policy_2026.txt
3. Checks: finance_user ∉ HR group → HR docs BLOCKED
4. No authorized chunks found
5. LLM responds: "I could not find this information in your authorized documents."
```

## Natural-language search vs keyword search

| Keyword search | Natural-language (semantic) search |
|---|---|
| Looks for exact words | Understands meaning |
| "budget 2026" finds docs with those exact words | "spending plan for next year" also finds budget docs |
| Misses synonyms and paraphrases | Handles different phrasings |
| Fast but dumb | Slightly slower but much smarter |

## How it fits in this project

RAG is owned by Member 1 (Computer Science) with security integration from Member 2 (Cybersecurity). It is the most complex component of the project and is built last — only after Nextcloud is stable, documents are indexed, and the permission model is in place. The final demo centers on this feature.

## Related

- [Embeddings](../ingestion/embeddings.md)
- [Vector Databases](../retrieval/vector-database.md)
- [Large Language Models (LLMs)](../generation/llm.md)
- [Document Indexing Pipeline](../ingestion/document-indexing.md)
- [Access Control & IAM](../../security/authorization/access-control-iam.md)
- [Fine-tuning](../infrastructure/fine-tuning.md) — the alternative approach when behavior, not knowledge, needs to change
- [Context Window](../generation/context-window.md) — the limit RAG's retrieve-only-relevant-chunks approach works around
- [LLM Evaluation](../evaluation/llm-evaluation.md) — how to measure hallucination reduction and answer quality in a RAG pipeline
- [Nextcloud RAG Case Study](../../../guides/cloud/nextcloud-rag-case-study/nextcloud.md)
