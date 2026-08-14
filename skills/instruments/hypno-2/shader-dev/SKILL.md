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

## Factory Shader Architecture (from `fx_feedback.frag` et al.)

The Hypno 2 factory shaders live in `/home/pi/Documents/VIDOS-Resources/Shaders/fx/` and follow a **two-input feedback architecture** that is fundamentally different from generative shaders. Understanding this is critical before writing your own.

### Entry Point: `main()` not `mainImage()`

Factory shaders use the classic GLSL entry point, **not** ShaderToy's `mainImage()`:

```glsl
void main( void ) {
    // ...
    gl_FragColor = vec4(color, 1.0);
}
```

The engine provides **implicit built-in variables** without explicit uniform declaration:
- `vec2 tcoord` — texture coordinate (equivalent to `uv` or `fragCoord/resolution`)
- `float time` — time in seconds
- `float cc1` through `cc8` — MIDI CC values (0.0–1.0 normalized)
- `vec2 resolution_step` — 1.0/resolution (texel size for convolution)
- `float rotation_0` — precomputed rotation matrix element
- `float luma(vec3)` — luminance helper (approx dot(color, vec3(0.299, 0.587, 0.114)))

### The `#include "FeedbackUtil.frag"` System

Every factory shader includes a shared utility header. This provides:

| Function | Purpose |
|----------|---------|
| `UVPage(uv, zoom, rot, y, x)` | Standard UV transform: zoom, rotate, translate feedback coordinates |
| `linear_srgb_from_srgb(c)` | Convert sRGB → linear (for proper blending) |
| `srgb_from_linear_srgb(c)` | Convert linear → sRGB (for output) |
| `rgb2hsv(c)` / `hsv2rgb(c)` | Color space conversion |
| `HueShift(fb, frame, amt)` | Hue rotation driven by frame luminance |
| `KeepForeground(frame, fb, lo, hi)` | Luma-key matte: keeps new frame in foreground, feedback in background |
| `ColorClamp(c)` | Soft-clamp color to prevent blowout |
| `InvertColor(c)` | 1.0 - color |

### Factory Texture Uniforms (Always Present)

```glsl
uniform sampler2D sampled_frame;   // Current input frame (video/camera/shape)
uniform sampler2D feedback_frame;  // Previous output frame (the "loop")
uniform sampler2D shape1;          // Shape generator 1 output
uniform sampler2D shape2;          // Shape generator 2 output
uniform mat2 fb_rotation_matrix_;  // Precomputed rotation matrix
uniform float gain;                // Global gain
uniform float hue_shift;           // Hue shift amount
uniform float fb_x;                // Feedback X offset (also mapped to cc3)
uniform float fb_y;                // Feedback Y offset (also mapped to cc5)
uniform float fb_rotate_;          // Rotation angle (also mapped to cc6)
uniform float zoom_;               // Zoom amount (also mapped to cc4)
```

**Note:** `fb_x`, `fb_y`, `fb_rotate_`, `zoom_` are declared as uniforms but **shadowed** by local variables assigned from `cc3`, `cc5`, `cc6`, `cc4` inside `main()`. The uniform declarations exist for the engine's parameter binding but the CC values take precedence at runtime.

### CC Parameter Mapping (Factory Convention)

| CC | Factory Usage | Typical Range |
|----|---------------|---------------|
| cc1 | `feedback` amount | 0.0–1.0 |
| cc2 | Effect-specific (chroma, strobe, pixelize, contrast, mirror mode) | 0.0–1.0 |
| cc3 | `fb_x` — feedback X offset | 0.0–1.0 (centered ~0.5) |
| cc4 | `fb_zoom` — feedback zoom | 0.0–1.0 |
| cc5 | `fb_y` — feedback Y offset | 0.0–1.0 (centered ~0.5) |
| cc6 | `fb_rotate` — feedback rotation | 0.0–1.0 |
| cc7 | `low_key` / `black_key` — luma key threshold | 0.0–1.0 |
| cc8 | `hi_key` — high luma key threshold | 0.0–1.0 |

### The Standard Factory Feedback Pipeline

Every factory shader follows this exact 8-step pattern:

```glsl
void main( void ) {
    // 1. READ CC PARAMETERS
    float feedback  = cc1;
    float fb_x      = cc3;
    float fb_y      = cc5;
    float fb_zoom   = cc4;
    float fb_rotate = cc6;
    float black_key = cc7;
    // cc2 is effect-specific

    // 2. SAMPLE CURRENT FRAME
    vec3 frame_color = texture2D( sampled_frame, tcoord ).xyz;

    // 3. TRANSFORM FEEDBACK UVs
    vec2 fbPos = UVPage(tcoord, fb_zoom, rotation_0, fb_y, fb_x);

    // 4. SAMPLE FEEDBACK (previous frame)
    vec3 feedback_color = texture2D( feedback_frame, fbPos ).xyz;
    // Optional: convert to linear for math
    // feedback_color = linear_srgb_from_srgb(feedback_color);

    // 5. COLOR PROCESSING (effect-specific)
    // HSV shift, contrast, pixelize, strobe, etc.
    vec3 color_hsv = rgb2hsv(feedback_color);
    color_hsv.x = color_hsv.x - (hue_shift * luma(frame_color) * 5.0);
    if(color_hsv.y > 0.01){ color_hsv.y = 1.0 - color_hsv.y; }
    if(color_hsv.z > 0.01){ color_hsv.z = 1.0 - color_hsv.z; }
    feedback_color = hsv2rgb(color_hsv);

    // 6. APPLY FEEDBACK AMOUNT
    feedback_color *= feedback;

    // 7. LUMA KEY MATTE (keep new frame in foreground)
    feedback_color = KeepForeground(frame_color, feedback_color, black_key * 0.5, 1.0);

    // 8. COMPOSITE & OUTPUT
    frame_color = abs(feedback_color - frame_color);  // or frame_color + feedback_color
    frame_color = srgb_from_linear_srgb(frame_color);
    gl_FragColor = vec4(frame_color, 1.0);
}
```

### Factory Shader Variants Analyzed

| Shader | cc2 Function | Key Technique |
|--------|--------------|---------------|
| `fx_feedback.frag` | (unused) | Basic feedback + hue shift + luma key |
| `fx_feedback_mirror.frag` | Mirror mode (0/0.3/0.6/1.0) | Flips UV.x and/or UV.y before sampling |
| `fx_hsv.frag` | (unused) | HSV inversion (sat & val flip) + difference composite |
| `fx_hsv_chroma.frag` | Chroma aberration strength | Radial RGB channel separation from center |
| `fx_hsv_contrast.frag` | Contrast exponent | `pow(color, vec3(contrast))` S-curve |
| `fx_hsv_pixelize.frag` | Quantization steps | `floor(color * steps) / steps` posterize |
| `fx_hsv_satboost.frag` | Saturation multiplier | `clamp(sat * (1.0 + boost), 0.0, 2.0)` |
| `fx_hsv_spiral.frag` | Zoom blur strength | Spiral twist matrix applied to feedback UVs |
| `fx_hsv_strobe.frag` | Strobe rate | `sin(floor(time * rate) * PI) > 0 ? 1 : 0` gate on feedback |
| `fx_hyperdigital.frag` | (unused) | Division composite: `frame / (feedback * fb)` |
| `fx_lumakey.frag` | (unused) | Edge detect + luma key + hue shift |
| `fx_last.frag` | (unused) | Experimental: convolution + invert + difference |

### Writing Your Own Factory-Style Shader

1. **Copy the structure** from `fx_feedback.frag` — it is the canonical reference.
2. **Keep the 8-step pipeline** — the engine expects feedback to work this way.
3. **Use cc2 for your effect parameter** — it's the only "free" CC.
4. **Don't redeclare `resolution`, `time`, `tcoord`, `cc*` — they are implicit.
5. **Always end with `gl_FragColor = vec4(color, 1.0);`** — not `fragColor`.
6. **Use `texture2D()` not `texture()`** — GLSL ES 1.0 style.

### Performance Notes from Factory Code

- **Branching is used sparingly** — `if(color_hsv.y > 0.01)` is cheap because it's per-pixel uniform.
- **No `for` loops** in factory shaders — everything is unrolled or single-sample.
- **One `texture2D` per frame per input** — no multi-tap convolution in production shaders.
- **`UVPage()` is the only UV transform** — don't add extra coordinate math unless necessary.
- **Linear/sRGB conversions are selective** — only used when color math requires it (feedback accumulation), skipped in pure HSV shaders.

## Generative Shader Architecture (from `fbm.frag`, `circle.frag`, et al.)

Generative shaders (Track A/B shape generators) live in `/home/pi/Documents/VIDOS-Resources/Shaders/` (root, NOT the `fx/` subdir) and use `#include "ShapeUtil.frag"`. They are structurally different from FX shaders.

### Two Shader Families on the Hypno 2

| | FX shaders (`fx/`) | Generative shaders (root) |
|---|---|---|
| Include | `FeedbackUtil.frag` | `ShapeUtil.frag` |
| Purpose | Process/mix frames (feedback) | Generate shapes from scratch |
| Textures | `sampled_frame`, `feedback_frame` | `cross_mod_shape`, `feedback_frame` |
| Output | Final composited color | Bipolar shape signal (see below) |
| Location | `Shaders/fx/fx_*.frag` | `Shaders/*.frag` |
| Prefix | `fx_` REQUIRED | none |

### Generative CC Map (Factory Convention — DIFFERENT from FX!)

Do NOT reuse the FX cc1–cc8 map. Shape generators use:

| CC | Parameter |
|----|-----------|
| cc0 | x_offset |
| cc1 | frequency |
| cc2 | y_offset |
| cc3 | x_crop (or aspect_x in fbm) |
| cc4 | rotation |
| cc5 | y_crop (or aspect_y in fbm) |
| cc6 | aspect_x / octaves (varies per shader) |
| cc7 | octaves (fbm) / polarization (sin, tan) |
| cc8 | aspect_y |
| cc9 | luma_min |
| cc10 | luma_max (circle: `cc10 + 1.`) |
| cc11 | (fbm: luma_max; sin/tan: luma_max) |
| cc12 | mirror_amt |
| cc13 | mirror_rotation |
| cc61 | cross_mod_amt (modulate by other track's shape) |
| cc62 | fb_mod_amt (modulate by feedback frame) |

**Fold-axis pattern (sin.frag, tan.frag):** wave shapes compute independent X and Y components and blend them with a "fold" parameter:
```glsl
float fold_axis  = cc3;   // blends X vs Y wave component
float fold_shape = cc5;   // wave shaping/folding amount
// ...
float colorX = mix(x_component, y_component, fold_axis);
```
sin/tan use cc3/cc5 for fold_axis/fold_shape instead of x_crop/y_crop — per-shader cc3–cc8 assignments vary, so always read the CC block at the top of `main()` before wiring parameters.

**Note:** CC numbering goes above cc8 — generative shaders can use cc0–cc13+ because tracks expose more parameters than the 5-uniform custom-shader limit (that limit applies to *user-written* shaders in the newer mainImage style, not the factory shape format).

### The Standard Generative Pipeline

```glsl
#include "ShapeUtil.frag"

// Standard texture inputs
uniform sampler2D cross_mod_shape;  // other oscillator's output
uniform sampler2D feedback_frame;   // final frame for feedback modulation

void main( void ) {
    // 1. READ CCs
    float x_offset = cc0;
    float frequency = cc1;
    float y_offset = cc2;
    // ... etc

    // 2. ASPECT-CORRECT + MIRROR
    vec2 position = CorrectAspectRatio(tcoord);
    position = mirror(position, mirror_amt, rotation_1);

    // 3. ROTATE + ASPECT NUDGE
    vec2 scn_pos = rotate2D(position, rotation_0);
    scn_pos = AspectNudge(scn_pos, aspect_x, aspect_y);

    // 4. OPTIONAL FEEDBACK MODULATION OF COORDINATES
    scn_pos += texture2D(feedback_frame, tcoord).xy
               * feedback_mod_toggle * fb_scale;

    // 5. POLAR/CARTESIAN SCAN
    vec2 scan = getScan2D(scn_pos, polarization);  // or getScan2D(scn_pos)

    // 6. CROSS-MOD / FB-MOD ON SCAN
    if(abs(cross_mod_amt) > 0.001){
        scan += cross_mod_amt * ((texture2D(cross_mod_shape, tcoord).x
                + texture2D(cross_mod_shape, tcoord).y) - 1.);
    }

    // 7. SHAPE FUNCTION → bipolar signal
    float colorX = myShape(scan, frequency, ...) * 2.0 - 1.0;

    // 8. LUMA KEY
    colorX *= luma_key(abs(colorX), luma_min, luma_max + 0.01);

    // 9. DUAL-CHANNEL ENCODING OUTPUT
    float colorY = colorX + 1.0;  // split range into 2 channels for more bit depth
    gl_FragColor = vec4(colorX, colorY, 0.0, 1.0);
}
```

### `ShapeUtil.frag` Provides

| Function | Purpose |
|----------|---------|
| `CorrectAspectRatio(uv)` | Aspect-corrected coordinates |
| `mirror(pos, amt, rot_mat)` | Mirror symmetry transform |
| `rotate2D(pos, rot)` | Rotation (uses `rotation_0` global) |
| `AspectNudge(pos, x, y)` | Fine aspect adjustment |
| `getScan2D(pos, polarization)` | Cartesian ↔ polar blend |
| `luma_key(v, lo, hi)` | Luminance gate |
| `noise(st)`, `tri(x)` | Hash noise, triangle wave |
| `rotation_0`, `rotation_1` | Global rotation matrices |
| `polarization_drift`, `y_phase` | Animated drift globals |
| `PI`, `TWO_PI` | Constants |

### The Dual-Channel Output Trick

Factory shape generators encode the shape as a **bipolar signal** in R, plus an offset copy in G:

```glsl
float colorX = shape * 2.0 - 1.0;   // -1..+1 bipolar
float colorY = colorX + 1.0;        // 0..2 (recover extra bit depth)
gl_FragColor = vec4(colorX, colorY, 0.0, 1.0);
```

The downstream mixer reconstructs full precision from the two channels. Preserve this pattern — don't just output grayscale `vec3(colorX)`.

### Factory Generative Shaders (13 on device)

`circle`, `square`, `poly`, `sin`, `tan`, `star-bright`, `octagrams`, `phantom-star`, `fbm`, `fractal-pyramid`, `radar1`, `smaller-waterfall`, `ether-energy`.

Local archive: `/home/rjodouin/Downloads/hypno2_fx_DLs/shaders/gen/`

### User-Style Generative Shaders (e.g. `ether-energy.frag`)

The newer user-ported generative shaders use a **different, ShaderToy-like dialect** — `mainImage()`, explicit `uniform vec2 resolution; uniform float time;`, max 5 custom float uniforms (CC 0–4), `precision mediump float;`, and inline hash/noise helpers with no includes. `ether-energy.frag` is the reference: a raymarch→FBM domain-warp port with a documented adaptation strategy in its header comments. Use this dialect for NEW generative shaders; use the factory dialect only when modifying factory shapes.

## Porting / Patching Logic Flow (headless local verification)

When porting factory or user-style shaders for local playback (glslViewer) and
reconstructing Hypno behavior off-device, follow this exact flow. Every step was
validated against real headless frame captures (ImageMagick `%k` + `compare -metric AE`).

### 1. The glslViewer 3.0.7 uniform contract (CRITICAL)

glslViewer 3.0.7 auto-fills ONLY **`u_resolution`** and **`u_time`**. Everything else
stays 0.0:

- Plain `uniform vec2 resolution` / `uniform float time` → stays **0.0**.
  Shaders that *divide* by them get NaN → black frames. Shaders that only *multiply*
  by them silently survive (coords collapse to 0) — that's why some shaders "worked."
- Custom uniforms (`warp_scale`, `camera_dist`, `frequency`, …) → stay **0.0**.

**Fix (two options):**
1. Rename declarations to `u_resolution` / `u_time`, or
2. Add `uniform vec2 u_resolution;` then `#define resolution u_resolution` /
   `#define time u_time` at the top.

**Do NOT** "fix" by guarding with `max(resolution, vec2(1.0))` — that silently
degrades `tcoord` to raw pixel coords 0..480 and changes the whole look.

### 2. Mezzz CC-emulation formula (replacing raw sine placeholders)

Real Hypno modulates every parameter with its Internal LFO. Emulate it as:

```glsl
param = clamp(base + depth * lfo(waveform, time * rate), 0.0, 1.0);
```

- `base` = the Mezzz knob position (CC 0–127 → 0.0–1.0)
- `depth` = modulation depth
- `lfo(waveform, t)` — the **14 Hypno LFO waveforms**: Sin, Cos, Tri, Ramp,
  Tan, Rnd, Pulse, Exp, Log, StpRnd, Bounce, Chaos, Heart, Pend.
- Wire `rotation_0` ← cc4 and `rotation_1` ← cc13 (real Hypno wiring).

Declare forward declarations for `tri()` / `hash21()` before the `lfo()` that
uses them, or the fragment may fail to resolve.

### 3. Verification recipe (objective, not compile checks)

Do NOT trust a bare compile (glslangValidator ignores `#include` → false failures).
Verify by rendering frames and measuring them:

```sh
# One shader per call, from an EMPTY CWD (sequence writes NNNNN.png here)
timeout 40 glslViewer --headless --noncurses -w 480 -h 480 /abs/path/shader.frag \
  -e "sequence,0,2,4"
# ~40s wall for a 0–2s@4fps recording; then:
identify -format '%k' 00000.png                     # distinct colors (>~100 = rich)
compare -metric AE 00000.png 00004.png null: 2>&1   # % pixels changed (>~30% = real motion)
```

- Frames write as `NNNNN.png` into the process CWD → run each audited shader from
  its own isolated subdir.
- **One-per-call foreground ONLY.** Background/batch/looping glslViewer runs return
  0 frames (race with any live glslViewer instance sharing the GPU). Never batch.
- Keep headless runs small (480×480, ≤2–3s) when a live rotation shares the GPU.
- `timeout` exit 124 short-circuits `&&` chains — judge success by frames + metrics,
  not exit code.

### 4. Uniform-binding audit for user-style shaders

For ShaderToy-style (`mainImage`) ports, audit every uniform used:
- `time` → `u_time` (or alias)
- `resolution` → `u_resolution` (or alias)
- custom uniforms → give **const defaults** from the documented CC ranges
  (glslViewer fills no custom uniforms; a 0 default flattens the shader).
  Tune the const (e.g. `warp_scale` 0.5 → 3.5) until the frame shows real structure.

### 5. Root-cause discipline

Symptom → probe, don't guess:
- Flat black with varying frames: check if a dividing uniform is 0 (probe by
  rendering the value directly, e.g. `fragColor = vec4(fract(gl_FragCoord/u_resolution*3.5),0,0,1)`).
- Flat single color, byte-identical frames: uniform is spatially constant → the
  coordinate math is broken (likely `resolution`=0).
- Some shaders work, others don't: compare which ones *divide* vs only *multiply*.

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
