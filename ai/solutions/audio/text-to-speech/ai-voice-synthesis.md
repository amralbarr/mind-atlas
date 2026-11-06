# AI Voice Synthesis (Text-to-Speech)

## Description
Converts written text into natural-sounding spoken audio. Modern TTS has moved from robotic concatenative synthesis to neural models that produce human-like prosody, emotion, and multilingual output, usually steerable via text instructions (tone, pacing, accent) rather than just raw phoneme input. Distinct from [Voice Cloning](../voice-cloning/voice-cloning.md), which targets a *specific* person's voice — generic TTS instead offers a library of stock voices.

## Input
- Text (plain text, SSML markup for pronunciation/pacing control, or a natural-language style instruction)
- A chosen voice (stock voice ID, or a cloned voice for personalization)

## Output
- Synthesized speech audio (WAV/MP3/PCM), with optional word-level timestamps for captioning/lip-sync

## Related Capabilities
- [Voice Cloning](../voice-cloning/voice-cloning.md) — same underlying tech, applied to a specific person's voice instead of a stock library
- [Speech-to-Text (Transcription)](../speech-to-text/ai-transcription.md) — the inverse direction
- [AI Customer Support Agents](../../text/text-to-text/ai-customer-support-agents.md) — voice agents pair TTS with an LLM and STT

## Software & Platforms

**Open source (self-hosted, free):**
- [Coqui TTS](../../../tools-platforms/audio-tools/coqui-tts.md) — community-maintained fork (Idiap Research Institute) of the original toolkit; MPL-2.0

**Paid / managed:**
- [ElevenLabs](../../../tools-platforms/audio-tools/elevenlabs.md) — highest-quality expressive voices; market leader as of 2026
- [OpenAI TTS](../../../tools-platforms/audio-tools/openai-tts.md) — `gpt-4o-mini-tts` via the Audio API
- [Google Cloud Text-to-Speech](../../../tools-platforms/audio-tools/google-cloud-text-to-speech.md) — Chirp 3 HD and Gemini-TTS models
- [Amazon Polly](../../../tools-platforms/audio-tools/amazon-polly.md) — AWS-native, tiered Standard/Neural/Generative/Long-form engines
- [PlayAI](../../../tools-platforms/audio-tools/playai.md) (formerly Play.ht) — acquired by Meta in July 2025

## Applications
- Audiobook and podcast narration
- IVR / phone-tree and voice-agent prompts
- Accessibility (screen readers, read-aloud for the visually impaired)
- Localizing video/e-learning narration into multiple languages
- In-app notifications and voice assistants

## Market note
PlayAI (formerly Play.ht) was acquired by Meta in July 2025 and folded into Meta's AI org — it's no longer an independently available product. OpenAI deprecated the original `tts-1`/`tts-1-hd`/`gpt-4o-mini-tts` endpoint family (shutting down January 2027) in favor of the Realtime API's `gpt-realtime-2.1-mini` for new integrations — verify current API surface before building against it.
