# OpenAI Whisper

**Type:** Open source (MIT)

## Category
Self-hosted speech-to-text model

## AI Capabilities
- Multilingual transcription and translation-to-English
- Robust to accents, background noise, and technical language
- `large-v3` is the highest-accuracy reference model; `large-v3-turbo` (October 2024) runs roughly 5x faster with a small accuracy tradeoff, making it the common default for self-hosted deployments
- Community runtimes — `faster-whisper` (CTranslate2-based) and `whisper.cpp` (C/C++, runs on CPU/edge devices) — provide large speed/memory improvements over the reference PyTorch implementation

## Related AI Solutions
- [AI Transcription (Speech-to-Text)](../../solutions/audio/speech-to-text/ai-transcription.md)

## Notes
- Code and model weights are released under the MIT License — fully permissive, including commercial use, no royalties.
- No official hosted API quality tier beyond OpenAI's own Audio API transcription endpoint; most production self-hosting uses `faster-whisper` or `whisper.cpp` rather than the original repo directly for performance reasons.
