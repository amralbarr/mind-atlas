# AI Customer Support Agents

## Description
Conversational AI that autonomously resolves customer support tickets/chats — not just an FAQ bot, but an agent that can look up order/account data, take actions (refunds, cancellations, updates), and hand off to a human when it can't resolve something. Almost always built on [RAG](../../documents/document-understanding/rag-retrieval-augmented-generation.md) over a help center + macros + ticket history, plus tool-calling into backend systems.

## Input
- Customer message (chat, email, or voice transcript)
- Help center / knowledge base / past ticket history
- Access to backend systems (order DB, CRM, billing) via tool calls

## Output
- A resolved ticket (answer given, refund issued, change made) or a clean handoff to a human agent with context

## Related Capabilities
- [RAG](../../documents/document-understanding/rag-retrieval-augmented-generation.md) — the retrieval layer underneath almost every tool here
- [AI-Driven Interviews](../../multimodal/multimodal-understanding/ai-driven-interviews-chat-voice-video.md) — same conversational-agent pattern applied to recruiting instead of support

## Software & Platforms

**Open source (self-hosted):**
- [Chatwoot](../../../tools-platforms/text-and-llm-tools/chatwoot.md) (+ "Captain" AI agent)
- [Botpress](../../../tools-platforms/text-and-llm-tools/botpress.md)
- [Rasa](../../../tools-platforms/text-and-llm-tools/rasa.md)

**Paid (enterprise AI support agents):**
- [Intercom Fin](../../../tools-platforms/text-and-llm-tools/intercom-fin.md) — ~$0.99/resolution; acquired by Salesforce, completed September 2026
- [Zendesk AI](../../../tools-platforms/text-and-llm-tools/zendesk-ai.md) — absorbed Forethought, completed March 2026
- [Decagon](../../../tools-platforms/text-and-llm-tools/decagon.md)
- [Sierra](../../../tools-platforms/text-and-llm-tools/sierra.md)
- [Ada](../../../tools-platforms/text-and-llm-tools/ada.md)

## Applications
- Tier-1 support deflection (order status, returns, password resets)
- Multi-step resolution with backend tool access (refund processing, subscription changes)
- Internal IT/HR helpdesk agents (same pattern, different data source)

## Market note
The 2026 enterprise AI-support market consolidated fast: Intercom rebranded to "Fin" and was acquired by Salesforce for ~$3.6B; Zendesk bought Forethought. This space moves quickly — verify current pricing/ownership before quoting it.
