# AI Transcription (Speech-to-Text)

## Description
Converts spoken audio into written text. Modern speech-to-text (STT) uses end-to-end neural models (often transformer-based) to handle accents, background noise, and multiple languages, and frequently bundles speaker diarization, punctuation, and timestamping alongside the raw transcript. Ranges from a fully self-hosted open-weight model (Whisper) to managed streaming APIs tuned for real-time voice agents.

## Input
- Audio file (recorded) or live audio stream (microphone/phone call)
- Optional: language hint, custom vocabulary/keyterms, speaker-count hint

## Output
- Transcript text, usually with word-level timestamps and confidence scores
- Optional speaker labels (see [Audio Understanding](../audio-understanding/audio-event-detection-and-diarization.md) for diarization as its own capability)

## Related Capabilities
- [AI Voice Synthesis (Text-to-Speech)](../text-to-speech/ai-voice-synthesis.md) — the inverse direction
- [Audio Understanding](../audio-understanding/audio-event-detection-and-diarization.md) — speaker diarization is often bundled with transcription
- [AI Customer Support Agents](../../text/text-to-text/ai-customer-support-agents.md) — voice agents pipe STT output into an LLM

## Software & Platforms

**Open source (self-hosted, free):**
- [OpenAI Whisper](../../../tools-platforms/audio-tools/openai-whisper.md) — MIT-licensed; `large-v3` and the faster `large-v3-turbo` are the current reference models; `faster-whisper`/`whisper.cpp` are popular optimized community runtimes

**Paid / managed:**
- [Deepgram](../../../tools-platforms/audio-tools/deepgram.md) — Nova-3 model, usage-based per-minute pricing, strong for real-time/streaming
- [AssemblyAI](../../../tools-platforms/audio-tools/assemblyai.md) — Universal-3.5 Pro model, per-hour pricing, bundled diarization/PII redaction
- [Otter.ai](../../../tools-platforms/audio-tools/otter-ai.md) — consumer/business meeting-transcription app built on STT, not a developer API

## Applications
- Meeting notes and action-item capture
- Call-center QA and compliance transcription
- Captioning/subtitling for video
- Voice-agent pipelines (STT → LLM → TTS)
- Medical and legal dictation

## Market note
Whisper's code and weights are MIT-licensed (fully permissive, including commercial use). `large-v3-turbo` (released October 2024) trades a small accuracy loss for roughly 5x faster inference versus `large-v3`, making it the common self-hosted default as of 2026.
