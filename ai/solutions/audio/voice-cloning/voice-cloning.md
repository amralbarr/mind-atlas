# Voice Cloning

## Description
Synthesizes speech in a *specific* person's voice, trained from audio samples of that person rather than drawing from a generic stock-voice library. Ranges from "instant" cloning (seconds of reference audio, lower fidelity) to "professional" cloning (tens of minutes of studio-quality audio, near-indistinguishable results) — see [AI Voice Synthesis](../text-to-speech/ai-voice-synthesis.md) for the generic-voice counterpart. Carries real consent/ethics obligations: reputable vendors require documented consent from the voice owner and increasingly watermark output to deter misuse (impersonation, fraud, deepfakes).

## Input
- Reference audio samples of the target voice (seconds to tens of minutes, depending on clone quality tier)
- Documented consent from the voice owner (required by reputable vendors)
- Text to synthesize in the cloned voice

## Output
- Synthesized speech in the target person's voice, often watermarked for provenance

## Related Capabilities
- [AI Voice Synthesis (Text-to-Speech)](../text-to-speech/ai-voice-synthesis.md) — same underlying tech using a stock voice instead of a cloned one
- [AI Transcription (Speech-to-Text)](../speech-to-text/ai-transcription.md)

## Software & Platforms

**Open source (self-hosted, free):**
- [Coqui TTS](../../../tools-platforms/audio-tools/coqui-tts.md) — bundles the XTTS-v2 cloning model (CPML license — commercial use restricted)
- F5-TTS — code is MIT-licensed, but the official pretrained checkpoints are CC-BY-NC-4.0 (non-commercial); fine-tuning your own weights is required for commercial use

**Paid / managed:**
- [ElevenLabs](../../../tools-platforms/audio-tools/elevenlabs.md) — instant cloning (seconds of audio) and Professional Voice Cloning (studio-quality training data)
- [Resemble AI](../../../tools-platforms/audio-tools/resemble-ai.md) — usage-based Flex pricing, enterprise/IVR focus
- [Respeecher](../../../tools-platforms/audio-tools/respeecher.md) — consent-first, used by film/TV studios for dubbing and ADR

## Applications
- Film/TV dubbing and ADR (automated dialogue replacement) in the original actor's voice
- Personalized audiobook/e-learning narration
- Preserving a voice for someone who has lost the ability to speak (medical use)
- Brand voice consistency across ads/IVR without re-recording a voice actor

## Market note
Both of the most-used open-weight cloning models — XTTS-v2 (Coqui CPML) and F5-TTS (CC-BY-NC-4.0 checkpoints) — restrict commercial use of the official pretrained weights. Verify license terms before shipping either in a commercial product rather than assuming "open source" means unrestricted.
