# AI Sound Effects Generation

## Description
Generates sound effects, ambience, and foley-style audio (footsteps, weather, machinery, crowd noise) from a text description, rather than recording or licensing stock sound libraries. Built on the same generative-audio architectures as [AI Music Generation](../music-generation/ai-music-generation.md), but tuned toward short, non-musical clips.

## Input
- Text prompt describing the desired sound (e.g. "heavy rain on a tin roof," "robotic laser charging up")
- Optional duration/looping parameters

## Output
- A short audio clip (typically a few seconds up to ~30 seconds), often with multiple variations per generation and optional seamless looping

## Related Capabilities
- [AI Music Generation](../music-generation/ai-music-generation.md) — same generative-audio family, applied to composed music instead of effects
- [AI Voice Synthesis (Text-to-Speech)](../text-to-speech/ai-voice-synthesis.md)

## Software & Platforms

**Open source (self-hosted, free):**
- Meta AudioGen (part of [AudioCraft](../../../tools-platforms/audio-tools/meta-audiocraft.md)) — MIT code, CC-BY-NC-4.0 weights (non-commercial)
- [Stable Audio Open](../../../tools-platforms/audio-tools/stable-audio.md) — includes a dedicated "Small SFX" open-weight model

**Paid / managed:**
- [ElevenLabs Sound Effects](../../../tools-platforms/audio-tools/elevenlabs.md) — SFX v3 model (released October 2026); text-to-sound-effect generation billed per minute of output

## Applications
- Game audio (foley, ambience, UI sound cues)
- Video/film post-production sound design
- Podcast and video intro/transition stingers
- Rapid prototyping of sound design before a sound engineer records/licenses final assets

## Market note
As with music generation, licensing terms differ meaningfully by vendor: AudioGen's released weights are non-commercial only, Stable Audio Open's small models are free commercially up to $1M revenue under Stability's Community License, and ElevenLabs is a straightforward paid API with commercial rights included in the subscription/usage fee.
