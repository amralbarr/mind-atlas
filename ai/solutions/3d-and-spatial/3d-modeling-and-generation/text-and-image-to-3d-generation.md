# Text-and-Image-to-3D Generation

## Description
Generates a textured 3D mesh directly from a text prompt or one/few reference images, skipping manual modeling entirely. Pipelines typically generate a coarse shape (diffusion or feed-forward 3D networks), then auto-retopologize to clean, game/engine-ready topology, auto-UV-unwrap, and bake AI-generated PBR textures — producing an asset exportable as FBX/GLB/OBJ/USDZ in minutes rather than hours of manual sculpting and UV work. Several tools now also offer AI auto-rigging as a pipeline step (see [AI-Assisted Character Animation](../3d-animation/ai-assisted-character-animation.md)).

## Input
- A text description ("a worn leather messenger bag, low-poly")
- One or more reference/concept images, or a sketch
- Optional: a target poly-count/topology style (game-ready, sculpt-detail, CAD-like)

## Output
- A textured 3D mesh (OBJ/FBX/GLB/USDZ) with UVs and PBR materials, often with a rigging option for humanoid/creature shapes

## Related Capabilities
- [Photogrammetry & Gaussian Splatting (3D Reconstruction)](../3d-reconstruction/photogrammetry-and-gaussian-splatting.md) — capturing a 3D model from real photos/video instead of generating one from a prompt
- [AI-Assisted Character Animation](../3d-animation/ai-assisted-character-animation.md) — auto-rigging and motion for a generated or modeled character
- [AI-Assisted CAD & Generative Design](../cad-design/ai-assisted-cad-and-generative-design.md) — the equivalent generate-from-intent pattern for engineering-precise geometry rather than visual assets

## Software & Platforms

**Paid / managed (AI-native generation):**
- [Meshy](../../../tools-platforms/3d-and-cad-software/meshy.md) — text/image-to-3D with built-in retopology, PBR texturing, and rigging; free tier plus Pro/Studio/Premium/Ultra plans
- [Tripo](../../../tools-platforms/3d-and-cad-software/tripo.md) — fast text/image-to-3D focused on clean, engine-ready ("Smart Mesh") topology for games
- [Spline AI](../../../tools-platforms/3d-and-cad-software/spline-ai.md) — browser-based 3D design tool with prompt-driven text/image-to-3D generation and AI texturing built into a full scene editor
- [Kaedim](../../../tools-platforms/3d-and-cad-software/kaedim.md) — image-to-3D with a human-in-the-loop artist review pass, aimed at production game/brand pipelines

## Applications
- Rapid game-asset prototyping (props, environment pieces, creature concepts)
- Populating virtual/AR scenes and product-visualization mockups without a 3D artist
- Concept-to-3D previsualization for product design and marketing
- Generating base meshes that a human artist then refines, rather than fully automated final assets

## Market note
Not every entrant survives: Luma AI's "Genie" text-to-3D tool was discontinued on January 1, 2026, and the space continues to consolidate quickly — verify a tool is still active before committing a pipeline to it.
