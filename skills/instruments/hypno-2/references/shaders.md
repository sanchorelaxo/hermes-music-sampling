# Hypno 2 — Factory Shader Library Reference

The Hypno 2 ships with a foundational factory library. The core 5 shapes and 5 FX shaders from Hypno 1 are all present, plus additional shaders added for Hypno 2. Shaders are loaded per-channel from the file browser. Custom .frag shaders can be added and edited in the built-in shader editor.

## FX Shaders (Main Track / Mixer)

Loaded on the Main track. The default is `fx_feedback.frag`. All FX shaders share the same CC mapping (CC 0–8, see MIDI CC reference).

| Shader File | Name | Description |
|-------------|------|-------------|
| `fx_feedback.frag` | Basic Feedback | Classic camera-pointed-at-screen feedback. Supports zoom, X/Y offset, rotation, and luma keying. |
| `fx_hsv_feedback.frag` | HSV Feedback | Hue-shifts the feedback frame on each iteration. Same offset/zoom/rotate controls. |
| `fx_hyperdigital_feedback.frag` | Hyperdigital Feedback | Feedback path divides back into itself (fractal division). Very sensitive — can cause flashing at high gain. Use low feedback. |
| `fx_invert_feedback.frag` | Invert Feedback | Inverts the feedback frame, creating pastel-like color shifts. Same offset/zoom/rotate controls. |
| `fx_lumakey_feedback.frag` | Luma Key Feedback | Feeds back only the surviving foreground edges after keying. Good for cutout effects on complex sources. |

## Generative Shape Shaders (Track A / Track B)

Loaded on Channels 1 and 2. These are 2D oscillator shapes that generate video from mathematical functions. They follow the CC 0–61 parameter grid.

| Shader File | Name | Description |
|-------------|------|-------------|
| `sin.frag` | Sine Wave Oscillator | Classic sine wave shape with scroll, rotation, polarization, aspect controls |
| `tan.frag` | Tangent Oscillator | Tangent wave shape — sharper transitions |
| `poly.frag` | Polygon | N-sided polygon shape with fractal/self-modulation |
| `circle.frag` | Circle / Oval | Circular oscillator with aspect ratio stretch |
| `noise.frag` | Fractal Noise | Perlin/simplex noise field generator |
| `sampler.frag` | Sampler | Video/image sampler for loaded media. **CCs 0–2 reserved** for loop in, framerate, loop out. Shader params start at CC 3. |

## Custom Shaders

- `.frag` files must be valid GLSL fragment shaders
- Uniform names become parameter labels in the UI (underscores become spaces)
- 5 uniforms maximum (beyond the built-in resolution/time uniforms)
- Example uniforms: `uniform float x_offset;`, `uniform float rotation;`
- Built-in editor: syntax highlighting, live preview, compile error display
- Custom shaders respect the same mod CC offset rule (mod CC = base CC + 66)

> **Shader parameter count rule:** Shaders can expose 0–5 custom uniforms. When fewer than 5 are exposed, unused CCs show `---` in the UI.

> **Shader development skill:** See [shader-dev/SKILL.md](shader-dev/SKILL.md) for comprehensive GLSL techniques, Hypno 2 constraints, and ready-to-run `.frag` templates. Covers noise generators, SDF shapes, domain warping, Voronoi, edge detection, blend modes, time animation, and audio-reactive patterns — all optimized for the Pi 5 GPU.