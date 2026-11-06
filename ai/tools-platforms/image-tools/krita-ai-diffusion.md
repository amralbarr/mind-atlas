# Krita AI Diffusion

**Type:** Open source (GPL-3.0)

## Category
Inpainting/outpainting plugin for the Krita painting app

## AI Capabilities
- In-canvas inpainting, outpainting, live painting with real-time AI feedback, resolution upscaling, and regional prompting
- Guided generation through [ControlNet](controlnet.md) and [IP-Adapter](ip-adapter.md) layers, including segmentation-based control layers
- Uses [ComfyUI](comfyui.md) as its generation backend; supports [Stable Diffusion](stable-diffusion.md) and [FLUX](flux.md) models
- Runs on local GPU (NVIDIA/CUDA, AMD/ROCm, Intel/XPU, Apple/MPS) or falls back to a cloud backend

## Related AI Solutions
- [AI-Powered Image Editing](../../solutions/image/image-editing/ai-image-editing-and-object-removal.md)

## Notes
- Requires Krita 5.2.0 or newer; actively maintained since 2023, with segmentation control layers added in 2026.
- A good fit for an artist who wants AI inpainting/outpainting inside a real painting app rather than a standalone generation UI.
