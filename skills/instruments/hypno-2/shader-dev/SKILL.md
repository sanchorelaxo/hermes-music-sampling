---
name: hypno2-shader-dev
description: "GLSL fragment shader techniques adapted for the Hypno 2 video synthesizer — single-pass generative visuals and video effects optimized for Raspberry Pi 5, 5-uniform limit, CC-mapped parameters"
category: instruments
---

# Hypno 2 Shader Development

Comprehensive GLSL fragment shader techniques for the [Sleepy Circuits Hypno 2](https://sleepycircuits.com/hypno-2) video synthesizer. Adapted from the [MiniMax-AI/shader-dev](https://github.com/MiniMax-AI/skills/tree/main/skills/shader-dev) skill and optimized for embedded hardware constraints.

## Hypno 2 Shader Constraints

Before writing any shader code, understand the environment:

| Constraint | Detail |
|------------|--------|
| **Shader type** | Fragment shaders only (`.frag`), single-pass |
| **Uniform limit** | Max 5 custom uniforms (beyond built-in `vec2 resolution`, `float time`) |
| **Uniform names** | Become UI parameter labels — underscores become spaces (e.g., `x_offset` → "x offset") |
| **Parameter CCs** | Uniforms map to CC 0–61 on the track's MIDI channel |
| **Modulation CCs** | Each parameter gets a mod LFO at CC + 66 (CC 66–127) |
| **Hardware** | Raspberry Pi 5, ~2.4 GHz ARM, VideoCore VII GPU |
| **Output** | 1080p at video frame rates (30–60 fps) |
| **No multipass** | Cannot render to offscreen buffers — everything is single-pass |
| **No iChannel** | No texture inputs from the engine (only `resolution` and `time`) |
| **No iMouse** | No mouse interaction — use CC-mapped uniforms instead |
| **GLSL version** | Standard GLSL ES-compatible (no WebGL2-only features) |

### What Works Well on Pi 5
- 2D noise (value, simplex, hash-based) with moderate octave counts (4–6)
- Domain warping — fantastic results at low cost
- 2D SDF shapes (circles, polygons, lines, fractals)
- Color palettes (cosine, HSV) — nearly free
- Polar/UV coordinate manipulation — kaleidoscope, symmetry
- Voronoi/cellular patterns — moderate cost, great visuals
- Edge detection (Sobel, Laplacian) on simple geometries
- Blended feedback-style accumulation (poor man's feedback in a single pass)

### What to Avoid on Pi 5
- Ray marching with 3D SDF — frame rate killer at 1080p
- Path tracing or global illumination
- Heavy fluid simulation
- Volumetric rendering with many samples
- Dense particle systems (> 100 particles)
- Complex fractals with high iteration counts

## Skill Structure

```
shader-dev/
├── SKILL.md                    # This file — routing table + constraints
├── techniques/                 # Implementation guides
│   ├── noise-generators.md     # Value/simplex noise, FBM variants
│   ├── color-palettes.md       # Cosine palette, HSV/HSL, Lch interpolation
│   ├── domain-warping.md       # Coordinate deformation for organic visuals
│   ├── sdf-2d-shapes.md        # 2D signed distance functions
│   ├── polar-uv-manipulation.md # Kaleidoscope, symmetry, spiral transforms
│   ├── voronoi-patterns.md     # Cellular/Voronoi noise patterns
│   ├── feedback-effects.md     # Single-pass faux-feedback techniques
│   ├── blend-modes.md          # Mix, multiply, screen, overlay, soft light
│   ├── time-animation.md       # Using `time` uniform for motion
│   └── edge-detection.md       # Sobel, Laplacian, gradient-based effects
├── templates/                  # Ready-to-use .frag shader files
│   ├── bare-minimum.frag       # Minimal valid shader (1 uniform)
│   ├── generative-shape.frag   # 2D SDF + noise + palette template
│   ├── video-effect.frag       # Faux-feedback + color processing
│   └── audio-reactive.frag     # CC-mapped parameters for external modulation
└── references/                 # External resources
    └── glsl-quickref.md        # GLSL built-in functions cheat sheet
```

## How to Use

1. **Match the request** to the Technique Routing Table below.
2. **Read the relevant technique file(s)** from `techniques/` — each contains core principles, implementation steps, and Hypno 2-compatible code templates.
3. **Start from a template** in `templates/` — copy and modify for your specific needs.
4. **Test on-device** — load `.frag` via File Browser, use the built-in shader editor for live tweaking.

## Technique Routing Table

| User wants to create... | Primary technique(s) | Combine with |
|---|---|---|
| Organic flowing visuals / lava lamp / gas giant | domain-warping | noise-generators, color-palettes |
| Kaleidoscope / mirror symmetry / mandalas | polar-uv-manipulation | color-palettes |
| Geometric shapes (circles, polygons, stars) | sdf-2d-shapes | edge-detection, blend-modes |
| Cellular / biological patterns | voronoi-patterns | color-palettes, edge-detection |
| Smooth noise field / clouds / terrain | noise-generators | color-palettes |
| Colorful evolving textures | color-palettes | noise-generators |
| Glitch / datamosh / CRT effects | edge-detection | blend-modes |
| Faux video feedback (single-pass) | feedback-effects | noise-generators, blend-modes |
| Audio-reactive parameter animation | time-animation | (any visual technique) |
| Built-in editor template starting point | templates/bare-minimum.frag | — |
| Full generative shape (factory-style replacement) | templates/generative-shape.frag | — |
| Video processing effect (color + distortion) | templates/video-effect.frag | — |
| Externally modulated visual (MIDI/CV/LFO control) | templates/audio-reactive.frag | — |

## Technique Index

### Core Building Blocks
- **noise-generators** — Value noise, simplex noise, FBM, ridged FBM, hash functions. The foundation of all procedural visuals.
- **color-palettes** — Cosine palette, HSV/HSL, Lch interpolation, blackbody. Essential for audio-reactive color.
- **domain-warping** — Feed noise output back as coordinate offset. Creates organic, flowing, liquid-like patterns.
- **time-animation** — Using the built-in `uniform float time` for smooth animation, speed control, and phase offsets.

### Generative Shapes
- **sdf-2d-shapes** — Circles, rectangles, polygons, lines, rounded shapes via signed distance functions. Anti-aliased edges.
- **polar-uv-manipulation** — Convert to polar coordinates, apply symmetry, kaleidoscope, spiral, and zoom effects.
- **voronoi-patterns** — Cellular noise producing honeycomb, stained glass, and biological-looking structures.

### Effects & Processing
- **feedback-effects** — Single-pass techniques that simulate video feedback: accumulation, bleed, ghosting.
- **blend-modes** — Photoshop-style blend operations: mix, multiply, screen, overlay, soft light, difference, dodge, burn.
- **edge-detection** — Sobel, Laplacian, and gradient-based effects for outlines, glow, and glitch aesthetics.

## Writing a Hypno 2 Shader

### Bare Minimum Template

```glsl
// Must have mainImage() entry point
// Built-in uniforms: vec2 resolution, float time
// Custom uniforms (max 5) become UI parameters

uniform vec2 resolution;
uniform float time;

// Custom uniforms — names appear in Hypno 2 UI
uniform float speed;        // CC 0 — animation speed
uniform float intensity;    // CC 1 — effect intensity

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    // Normalize coordinates to 0–1 range
    vec2 uv = fragCoord / resolution.xy;
    
    // Center UVs (optional, for symmetric effects)
    vec2 p = (fragCoord - 0.5 * resolution.xy) / resolution.y;
    
    // Your effect here
    vec3 col = vec3(0.5 + 0.5 * sin(uv.x * 10.0 + time * speed));
    col *= intensity;
    
    fragColor = vec4(col, 1.0);
}
```

### Key Differences from ShaderToy

| ShaderToy | Hypno 2 |
|-----------|---------|
| `iTime` | `time` |
| `iResolution.xy` | `resolution` |
| `iMouse` | Not available — use uniforms |
| `iChannel0-3` | Not available |
| `mainImage(out vec4, in vec2)` | Same entry point |
| Arbitrary uniforms | Max 5 custom uniforms |
| `#define` constants | Use uniforms for anything user-tweakable |
| WebGL browser | Embedded GLES on Raspberry Pi |

### Uniform → Parameter Mapping

```glsl
uniform float x_offset;    // → UI label: "x offset", CC 0
uniform float frequency;   // → UI label: "frequency", CC 1
uniform float rotation;    // → UI label: "rotation", CC 2
uniform float mirror_amt;  // → UI label: "mirror amt", CC 3
uniform float hue_shift;   // → UI label: "hue shift", CC 4
```

- Declare uniforms in the order you want them to appear in the UI
- All 5 positions are optional — declare fewer for simpler shaders
- Use `float` uniforms only (no `int`, `bool`, `vec2`, etc. in custom uniforms)
- The mod CC offset is automatic: CC 0 gets modulation on CC 66, CC 1 on CC 67, etc.

### Performance Guidelines

1. **Prefer hash-based noise over simplex** — simpler, faster on ARM GPU
2. **Limit FBM octaves to 4–6** — each octave doubles the noise evaluations
3. **Use `fwidth()` sparingly** — it's expensive on VideoCore
4. **Avoid `for` loops with variable bounds** — unroll or use constants
5. **Minimize `texture()` calls** — you have no texture inputs anyway
6. **Keep branching flat** — `mix()` and `step()` are cheaper than `if/else`
7. **Use `smoothstep()` for anti-aliased edges** — one call, no extra samples

## Resources

- Hypno 2 instrument skill: [SKILL.md](../SKILL.md)
- GLSL quick reference: `references/glsl-quickref.md`
- Hypno 2 manual PDF: `/home/rjodouin/Downloads/current_music_docs/Hypno 2 Manual (V0.100).pdf`
- Online docs: https://docs.sleepycircuits.com/hypno2
- ShaderToy (reference only — must adapt): https://www.shadertoy.com/
- GLSL ES spec: https://registry.khronos.org/OpenGL-Refpages/es3/
- Inigo Quilez articles: https://iquilezles.org/articles/

## Commit Conventions

When adding or updating shader techniques:
```
git add -A
git commit -m "Add Hypno 2 shader dev skill (<technique>)

Adapted from MiniMax-AI/shader-dev for Hypno 2 constraints:
- Single-pass, Pi 5 performance target, 5-uniform limit"
```
