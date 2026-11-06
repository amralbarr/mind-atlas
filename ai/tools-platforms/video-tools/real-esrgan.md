# Real-ESRGAN

**Type:** Open source (BSD 3-Clause)

## Category
Video/image super-resolution (upscaling)

## AI Capabilities
- GAN-based super-resolution — upscales low-resolution or compressed/degraded video and images
- Trained specifically on real-world degradation (compression artifacts, noise, blur), not just clean downscaling, so it holds up on real footage rather than only lab test images
- Runs self-hosted on a local GPU; no cloud dependency

## Related AI Solutions
- [Video Upscaling, Interpolation & Restoration](../../solutions/video/video-enhancement/video-upscaling-interpolation-and-restoration.md)

## Notes
- Permissive license (BSD 3-Clause) — commercial use allowed.
- The de facto default upscale backend bundled into other actively maintained open-source tools (ComfyUI, AUTOMATIC1111, Upscayl), which is how most people actually run it rather than the bare repo directly.
- For anime-style content specifically, [Real-CUGAN](real-cugan.md) is faster and tuned for that use case.
