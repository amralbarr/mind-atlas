# Photogrammetry & Gaussian Splatting (3D Reconstruction)

## Description
Reconstructs a 3D model or scene from real-world photos, video, or LiDAR scans — the inverse of generating a model from a prompt. Classic photogrammetry triangulates camera positions across overlapping photos to build a textured mesh. Newer AI methods — Neural Radiance Fields (NeRF) and, especially since 2023-2024, 3D Gaussian Splatting — instead train a model that can render novel viewpoints of the captured scene in real time, producing a volumetric "splat" representation rather than a traditional mesh. Both approaches are now commonly offered side by side in the same capture apps.

## Input
- A set of overlapping photos or a walkthrough video of an object/scene
- Optional LiDAR depth data (from a phone or dedicated scanner) for faster/more accurate alignment

## Output
- A textured 3D mesh (photogrammetry) and/or a Gaussian-splat scene file, exportable to standard 3D formats or viewable directly as a real-time splat

## Related Capabilities
- [Text-and-Image-to-3D Generation](../3d-modeling-and-generation/text-and-image-to-3d-generation.md) — generating a model from a prompt instead of capturing one from reality
- [3D Scene Understanding & Spatial AI](../spatial-understanding/3d-scene-understanding-and-spatial-ai.md) — point-cloud/SLAM techniques that often share the same camera-pose-estimation step as photogrammetry
- [AI-Accelerated Rendering & Denoising](../3d-rendering/ai-accelerated-rendering-and-denoising.md) — rendering the reconstructed asset back out

## Software & Platforms

**Open source (self-hosted, free):**
- [nerfstudio](../../../tools-platforms/3d-and-cad-software/nerfstudio.md) — Apache 2.0 framework for training and rendering NeRFs and Gaussian Splats (via its `splatfacto`/`gsplat` backend) from your own photo/video captures

**Paid / managed:**
- [Polycam](../../../tools-platforms/3d-and-cad-software/polycam.md) — mobile LiDAR scanning, photogrammetry, and Gaussian Splatting capture with cloud processing
- [Luma AI](../../../tools-platforms/3d-and-cad-software/luma-ai.md) — phone-based NeRF/Gaussian-splat capture app, one of the earliest consumer tools to popularize splatting
- [RealityScan](../../../tools-platforms/3d-and-cad-software/realityscan.md) — Epic Games' desktop/mobile photogrammetry suite (formerly RealityCapture), with AI-powered masking and scan-completeness detection; free for individuals/small studios under the Unreal royalty revenue threshold

## Applications
- Scanning real products/environments for e-commerce, VFX, or game-asset reference
- Digitizing physical sites for virtual production, real-estate walkthroughs, and digital twins
- Cultural heritage and archival capture of physical objects and spaces
- Fast on-set capture of environments for use as real-time Gaussian-splat backgrounds
