# Coqui TTS

**Type:** Open source (MPL-2.0)

## Category
Self-hosted text-to-speech / voice-cloning toolkit

## AI Capabilities
- Multiple TTS architectures (VITS, Tacotron, and the XTTS-v2 voice-cloning model)
- Multilingual synthesis
- Runs fully offline/self-hosted — no per-character API cost

## Related AI Solutions
- [AI Voice Synthesis (Text-to-Speech)](../../solutions/audio/text-to-speech/ai-voice-synthesis.md)
- [Voice Cloning](../../solutions/audio/voice-cloning/voice-cloning.md) — via the bundled XTTS-v2 model

## Notes
- Coqui the *company* shut down in early 2024 (Coqui Studio went offline January 2024); the original `coqui-ai/TTS` GitHub repo has had no meaningful activity since.
- The actively maintained successor is the community fork **`idiap/coqui-ai-TTS`** (PyPI package `coqui-tts`), maintained by the Idiap Research Institute — v0.28.0 shipped October 2026. Use this fork, not the archived original repo.
- The core library code is MPL-2.0 (permissive), but the bundled **XTTS-v2** model weights are licensed under Coqui's own CPML (Coqui Public Model License), which restricts commercial use without a separate license — check CPML terms before shipping XTTS-v2 output in a commercial product.
