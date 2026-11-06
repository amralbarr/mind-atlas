# Video Upscaling, Interpolation & Restoration

## Description
Improves the technical quality of existing video rather than generating new content: upscaling raises resolution (e.g. SD/HD footage to 4K), frame interpolation raises frame rate for smoother motion or slow-motion, and denoising/restoration cleans up compression artifacts, noise, and old/degraded footage. Runs as a local processing step (desktop app or self-hosted model) rather than a conversational AI product.

## Input
- A video file at its original resolution/frame rate/quality

## Output
- The same video at a higher resolution, higher frame rate, and/or with noise/artifacts/damage reduced

## Related Capabilities
- [Video Generation](../video-generation/text-to-video-and-image-to-video-generation.md) — enhancement models are increasingly also used to clean up artifacts in AI-generated video itself
- [Image Enhancement](../../image/image-enhancement/README.md) — the same super-resolution/denoising techniques applied to a single frame instead of a video

## Software & Platforms

**Open source (self-hosted, free):**
- [Real-ESRGAN](../../../tools-platforms/video-tools/real-esrgan.md) — general-purpose GAN-based upscaler (BSD 3-Clause), the default backend bundled into most other open-source upscaling tools
- [Real-CUGAN](../../../tools-platforms/video-tools/real-cugan.md) — upscaler tuned specifically for anime/illustration content (MIT)
- [RIFE](../../../tools-platforms/video-tools/rife.md) — frame interpolation for smoother motion/slow-motion (MIT)
- [FlowFrames](../../../tools-platforms/video-tools/flowframes.md) — desktop GUI wrapping RIFE so interpolation doesn't require the command line

**Paid / managed:**
- [Topaz Video AI](../../../tools-platforms/video-tools/topaz-video-ai.md) — the category-leading desktop app and API; upscaling to 8-24K, 120fps interpolation, denoising, stabilization, and models aimed specifically at cleaning up AI-generated video artifacts

## Applications
- Restoring old/archival or low-resolution footage for re-release
- Upscaling user-generated or AI-generated video for broadcast/large-screen delivery
- Converting footage to a higher frame rate for smooth slow-motion
- Cleaning up compression artifacts from heavily re-encoded or downloaded video

## Market note
NVIDIA also ships a consumer version of this as a GPU-driver feature — RTX Video Super Resolution — which upscales video played in supported browsers in real time on RTX-series cards, rather than as a standalone processing app. No major cloud provider (AWS/Google/Azure) currently offers a dedicated, first-party video-upscaling API; the two services that exist are desktop apps like Topaz, or third-party SaaS APIs built on similar models.
