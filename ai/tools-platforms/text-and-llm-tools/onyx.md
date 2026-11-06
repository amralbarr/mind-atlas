# Onyx (formerly Danswer)

**Type:** Open source (MIT core)

## Category
Self-hostable enterprise RAG platform

## AI Capabilities
- 40+ pre-built connectors (Slack, Confluence, Google Drive, Jira, GitHub, etc.)
- Permission-aware retrieval — inherits access-control lists from the source system, so a user never sees content they couldn't already access there
- Built-in chat UI

## Related AI Solutions
- [RAG — Retrieval-Augmented Generation](../../solutions/documents/document-understanding/rag-retrieval-augmented-generation.md)

## Notes
- Reported as the most-deployed open-source option for workforce-facing (internal) RAG as of 2026, specifically because of the connector + ACL combination most frameworks don't ship out of the box.
- The permission-filter pattern it implements is the same one described in the handbook's [RAG](../../../engineering/concepts/ai/rag/rag.md) note's security section.
