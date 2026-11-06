# AI Solutions

A catalog of what AI can actually do, organized by the type of content or medium an AI solution works with (modality), then by specific capability within that modality. Each capability folder holds one note per concrete AI solution/use case as they get added.

Distinct from [tools-platforms/](../tools-platforms/) — that folder catalogs the software/products that *implement* these capabilities (ChatGPT, Midjourney, ElevenLabs, AutoCAD's AI features, ...). A capability folder here should link out to the relevant entries there (and vice versa) rather than duplicating tool details inline.

- **[text/](text/)** — [writing-and-content-generation/](text/writing-and-content-generation/), [summarization/](text/summarization/), [translation/](text/translation/), [text-analysis/](text/text-analysis/), [text-to-structured-data/](text/text-to-structured-data/), [text-to-text/](text/text-to-text/)
- **[image/](image/)** — [image-generation/](image/image-generation/), [image-editing/](image/image-editing/), [image-enhancement/](image/image-enhancement/), [image-recognition/](image/image-recognition/), [image-segmentation/](image/image-segmentation/), [image-to-image/](image/image-to-image/)
- **[video/](video/)** — [video-generation/](video/video-generation/), [video-editing/](video/video-editing/), [video-enhancement/](video/video-enhancement/), [video-understanding/](video/video-understanding/), [video-to-video/](video/video-to-video/), [video-summarization/](video/video-summarization/)
- **[audio/](audio/)** — [text-to-speech/](audio/text-to-speech/), [speech-to-text/](audio/speech-to-text/), [voice-cloning/](audio/voice-cloning/), [music-generation/](audio/music-generation/), [sound-generation/](audio/sound-generation/), [audio-understanding/](audio/audio-understanding/)
- **[3d-and-spatial/](3d-and-spatial/)** — [3d-modeling-and-generation/](3d-and-spatial/3d-modeling-and-generation/), [3d-reconstruction/](3d-and-spatial/3d-reconstruction/), [3d-rendering/](3d-and-spatial/3d-rendering/), [3d-animation/](3d-and-spatial/3d-animation/), [cad-design/](3d-and-spatial/cad-design/), [simulation/](3d-and-spatial/simulation/), [spatial-understanding/](3d-and-spatial/spatial-understanding/)
- **[code/](code/)** — [code-generation/](code/code-generation/), [code-completion/](code/code-completion/), [code-review/](code/code-review/), [debugging/](code/debugging/), [testing/](code/testing/), [software-development-agents/](code/software-development-agents/)
- **[documents/](documents/)** — [document-generation/](documents/document-generation/), [ocr-and-extraction/](documents/ocr-and-extraction/), [document-understanding/](documents/document-understanding/), [document-conversion/](documents/document-conversion/), [document-processing/](documents/document-processing/)
- **[multimodal/](multimodal/)** — [image-and-text/](multimodal/image-and-text/), [video-and-text/](multimodal/video-and-text/), [audio-and-text/](multimodal/audio-and-text/), [audio-and-video/](multimodal/audio-and-video/), [multimodal-understanding/](multimodal/multimodal-understanding/)
- **[physical-and-robotics/](physical-and-robotics/)** — [robot-control/](physical-and-robotics/robot-control/), [navigation/](physical-and-robotics/navigation/), [object-manipulation/](physical-and-robotics/object-manipulation/), [autonomous-systems/](physical-and-robotics/autonomous-systems/), [human-robot-interaction/](physical-and-robotics/human-robot-interaction/)
- **[structured-data/](structured-data/)** — [data-analysis/](structured-data/data-analysis/), [data-extraction/](structured-data/data-extraction/), [prediction-and-forecasting/](structured-data/prediction-and-forecasting/), [classification/](structured-data/classification/), [anomaly-detection/](structured-data/anomaly-detection/), [data-generation/](structured-data/data-generation/)

## Note template for a capability

Each capability folder's README (or an individual solution file within it) should follow this shape:

```md
# <Capability Name>

## Description
What this capability does.

## Input
- ...

## Output
- ...

## Related Capabilities
- [[other-capability]]

## Software & Platforms
- [[tool-name]]  (link into tools-platforms/)

## Applications
- ...
```

## Rule of thumb for what goes where

| What are you documenting?  | Where it belongs                                   |
| --------------------------- | --------------------------------------------------- |
| What AI can do               | here (ai/solutions)                                 |
| Which software does it        | [tools-platforms/](../tools-platforms/)             |
| How the underlying tech works | [engineering/concepts/ai/](../../engineering/concepts/ai/) |
| Where a business applies it   | business/marketing/sales/product/operations/etc.    |
