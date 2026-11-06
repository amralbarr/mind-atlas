# RAG — Retrieval-Augmented Generation (Chat With Your Documents)

## Description
Grounds an LLM's answers in your own documents/data instead of relying on its training data alone: a query retrieves relevant chunks from an indexed knowledge base (vector/hybrid search), and the LLM generates an answer citing those chunks. Powers internal knowledge-base Q&A, docs chatbots, enterprise search, and is the retrieval layer underneath most AI customer-support agents.

## Input
- Documents (PDF, DOCX, HTML, Markdown, Notion/Confluence pages, scanned/OCR'd files)
- A natural-language question

## Output
- A generated answer grounded in retrieved source passages, usually with citations/links back to the source document

## Related Capabilities
- [AI Customer Support Agents](../../text/text-to-text/ai-customer-support-agents.md) — most support agents are RAG over a help center + ticket history
- [Resume Screening & Candidate Matching](resume-screening-and-candidate-matching.md) — same retrieve+generate pattern applied to resumes/job descriptions
- Underlying concepts: [RAG](../../../../engineering/concepts/ai/rag/rag.md), [Hybrid Search](../../../../engineering/concepts/ai/retrieval/hybrid-search.md), [Embeddings](../../../../engineering/concepts/ai/ingestion/embeddings.md), [Vector Database](../../../../engineering/concepts/ai/retrieval/vector-database.md)

## Software & Platforms

**Open source (self-hosted, free):**
- [Haystack](../../../tools-platforms/text-and-llm-tools/haystack.md) — production RAG/agent orchestration framework (deepset)
- [RAGFlow](../../../tools-platforms/text-and-llm-tools/ragflow.md) — RAG engine specialized in messy documents (scanned PDFs, tables)
- [Onyx](../../../tools-platforms/text-and-llm-tools/onyx.md) — self-hostable RAG platform with 40+ enterprise connectors and ACLs (formerly Danswer)
- [Verba](../../../tools-platforms/text-and-llm-tools/verba.md) — Weaviate's reference RAG app ("Golden RAGtriever")
- Frameworks already in the handbook: [LangChain](../../../../engineering/concepts/ai/agents/langchain.md), [LlamaIndex](../../../../engineering/concepts/ai/agents/llamaindex.md)
- Vector stores already in the handbook: [Pinecone](../../../../engineering/concepts/ai/retrieval/vector-stores/pinecone.md), [Weaviate](../../../../engineering/concepts/ai/retrieval/vector-stores/weaviate.md), [ChromaDB](../../../../engineering/concepts/ai/retrieval/vector-stores/chromadb.md), [Qdrant](../../../../engineering/concepts/ai/retrieval/vector-stores/qdrant.md), [FAISS](../../../../engineering/concepts/ai/retrieval/vector-stores/faiss.md)

**Paid / managed:**
- [Vectara](../../../tools-platforms/text-and-llm-tools/vectara.md) — RAG-as-a-service API with built-in hallucination detection
- [Glean](../../../tools-platforms/text-and-llm-tools/glean.md) — enterprise search + RAG across all company SaaS apps
- [Kapa.ai](../../../tools-platforms/text-and-llm-tools/kapa-ai.md) — docs/dev-support chatbot for product documentation
- [AWS Bedrock Knowledge Bases](../../../tools-platforms/text-and-llm-tools/aws-bedrock-knowledge-bases.md)
- [Google Vertex AI Search](../../../tools-platforms/text-and-llm-tools/google-vertex-ai-search.md)
- Already in the handbook: [Azure AI Search](../../../../engineering/concepts/cloud/azure/azure-ai-search.md)

## Applications
- Internal knowledge-base / "ask HR, ask IT" bots
- Developer docs assistants
- Customer support grounded in help-center content
- Enterprise search across Slack/Drive/Confluence/Notion
