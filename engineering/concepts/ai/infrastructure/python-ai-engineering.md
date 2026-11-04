# Python for AI Engineering

Python is the default language for AI/ML and [LLM](../generation/llm.md) engineering work. This is a map of the areas worth being fluent in, organized from general language fundamentals up to the [LLM](../generation/llm.md)-specific skills that differentiate an AI engineer. A strong grasp of Python fundamentals is the differentiator that lets everything above it (AI/ML libraries, [LLM](../generation/llm.md) tooling) click into place quickly.

## Python fundamentals

Topics:
- [OOP](../../programming/fundamentals/oop.md)
- [Asyncio](../../backend/architecture/asyncio.md)
- Multithreading
- Multiprocessing
- Context managers
- Generators
- Decorators
- Virtual environments

Common questions:
- GIL explained
- Threading vs multiprocessing
- What are generators?
- Decorators use cases
- [Asyncio](../../backend/architecture/asyncio.md) [event loop](../../programming/javascript/event-loop.md)

## AI/ML core

Topics:
- NumPy
- Pandas
- Scikit-learn
- PyTorch basics
- TensorFlow basics
- ONNX
- OpenCV

Common questions:
- Difference between AI/ML/DL
- Overfitting
- Bias vs variance
- Precision vs recall
- CNN basics
- Model inference optimization

## LLM engineering (the highest-leverage area)

This is where an AI engineer's profile becomes differentiated from a general backend or ML engineer — it's the layer directly responsible for products like [RAG](../rag/rag.md) systems.

Topics:
- [Prompt engineering](../generation/prompt-engineering.md)
- [RAG](../rag/rag.md) architecture
- [Embeddings](../ingestion/embeddings.md)
- [Vector databases](../retrieval/vector-database.md)
- Chunking
- Retrieval pipelines
- Agents
- [Tool calling](../agents/tool-calling.md)
- [MCP](../agents/model-context-protocol.md) (Model Context Protocol)
- Memory systems
- [Multi-agent systems](../agents/multi-agent-systems.md)
- [LangChain](../agents/langchain.md) / [LangGraph](../agents/langgraph.md)
- OpenAI APIs
- Streaming AI responses

Common questions:
- Explain [RAG](../rag/rag.md) architecture
- Why use a vector DB?
- [Chunking strategies](../../../overviews/ai/chunking-strategies.md)
- Hallucination reduction
- Embedding models
- Agent orchestration
- Function calling
- [MCP](../agents/model-context-protocol.md) architecture
- AI memory systems

## Related

- [AI Orchestration Frameworks](../../../overviews/ai/orchestration-frameworks.md)
- [Large Language Models (LLMs)](../generation/llm.md)
- [Retrieval-Augmented Generation (RAG)](../rag/rag.md)
- [Embeddings](../ingestion/embeddings.md)
- [Prompt Engineering](../generation/prompt-engineering.md)
- [Function / Tool Calling](../agents/tool-calling.md)
- [Model Context Protocol (MCP)](../agents/model-context-protocol.md)
- [Multi-Agent Systems](../agents/multi-agent-systems.md)
- [System Design](../../backend/architecture/system-design.md)
