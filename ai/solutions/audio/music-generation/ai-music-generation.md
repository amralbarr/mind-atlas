# AI Music Generation

## Description
Composes original music — instrumental or full songs with vocals — from a text prompt (genre, mood, lyrics) or a reference audio clip. The leading consumer products (Suno, Udio) generate full songs with AI-sung vocals; enterprise/API-oriented models (Lyria, MusicGen, Stable Audio) tend to focus on instrumental tracks with more deployment flexibility. The space has been reshaped through 2025-2026 by copyright litigation from major record labels, now resolving into licensing deals rather than continued court battles.

## Input
- Text prompt (genre, mood, instrumentation, optional lyrics)
- Optional reference audio clip to extend or restyle

## Output
- Generated music track (instrumental or with AI vocals), typically 30 seconds to several minutes, exportable as audio

## Related Capabilities
- [AI Sound Effects Generation](../sound-generation/ai-sound-effects-generation.md) — same generative-audio family, applied to effects/ambience instead of music
- [AI Voice Synthesis (Text-to-Speech)](../text-to-speech/ai-voice-synthesis.md)

## Software & Platforms

**Open source (self-hosted, free):**
- Meta MusicGen (part of [AudioCraft](../../../tools-platforms/audio-tools/meta-audiocraft.md)) — MIT-licensed code, but weights are CC-BY-NC-4.0 (non-commercial)
- [Stable Audio Open](../../../tools-platforms/audio-tools/stable-audio.md) — Stability AI's open-weight tier (Small SFX/Small/Medium), Stability AI Community License

**Paid / managed:**
- [Suno](../../../tools-platforms/audio-tools/suno.md) — leading consumer full-song generator; now has licensing deals with Warner, BMG, Believe/TuneCore
- [Udio](../../../tools-platforms/audio-tools/udio.md) — settled with Universal (Oct 2025) and Warner (Nov 2025); moving toward a fully licensed platform
- [Google Lyria 2](../../../tools-platforms/audio-tools/google-lyria.md) — enterprise instrumental music generation via Vertex AI
- [Stable Audio](../../../tools-platforms/audio-tools/stable-audio.md) — paid API/self-hosting tier for the larger Stable Audio 3.0 model

## Applications
- Background music for video, podcasts, ads, and games
- Rapid demo/reference-track composition for songwriters
- Royalty-free production-music libraries
- Personalized/novelty songs (birthday songs, jingles)

## Market note
2025-2026 brought a wave of major-label settlements: Universal Music Group settled with Udio (October 2025) to jointly build a licensed AI music platform; Warner Music Group settled with both Suno and Udio (November 2025); BMG signed with Suno (August 2026); Believe/TuneCore signed with Suno (September 2026). Sony's litigation against Udio was still ongoing as of mid-2026. This means commercial safety of output varies by platform and is actively changing — verify a given platform's current licensing status before recommending it for commercial use.
