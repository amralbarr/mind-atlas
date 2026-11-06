# OpenAI TTS

**Type:** Paid (API, usage-based)

## Category
Text-to-speech API

## AI Capabilities
- Neural TTS via the Audio API, steerable with natural-language instructions on delivery style (not just word content)
- `gpt-4o-mini-tts` is the current flagship TTS model (default snapshot `gpt-4o-mini-tts-2025-12-15`)

## Related AI Solutions
- [AI Voice Synthesis (Text-to-Speech)](../../solutions/audio/text-to-speech/ai-voice-synthesis.md)

## Notes
- As of November 2026, OpenAI has announced `tts-1`, `tts-1-hd`, and `gpt-4o-mini-tts` are **deprecated**, shutting down January 6, 2027. OpenAI is steering new integrations toward `gpt-realtime-2.1-mini` on the Realtime API instead of the `/v1/audio/speech` endpoint — this is a different API workflow (streaming/session-based rather than a single synthesis call). Confirm the current recommended model before building new integrations.
