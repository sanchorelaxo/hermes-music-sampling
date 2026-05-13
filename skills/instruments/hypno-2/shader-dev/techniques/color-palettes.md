# Color Palettes — Hypno 2

Color is the cheapest visual effect on any GPU. A good palette turns a grayscale noise field into a stunning visual. This guide covers palette techniques that cost nearly zero compute on the Pi 5.

## Core Principles

**Map a scalar `t` (0–1) to an RGB `vec3`**. The noise/pattern produces `t`, the palette produces the color.

## Cosine Palette (Recommended Primary)

The cosine palette is the Swiss Army knife of shader coloring. Three parameters control the entire color range:

```glsl
// a: brightness offset (~0.5)
// b: amplitude (~0.5)
// c: frequency (1.0 = full rainbow)
// d: phase — THE KEY PARAMETER controlling color character
vec3 palette(float t, vec3 a, vec3 b, vec3 c, vec3 d) {
    return a + b * cos(6.28318 * (c * t + d));
}
```

### Classic Preset Phases (d parameter only)

```glsl
// Rainbow:        d = vec3(0.0, 0.33, 0.67)
// Warm sunset:    d = vec3(0.0, 0.10, 0.20)
// Blue-purple:    d = vec3(0.0, 0.15, 0.20)     c = vec3(1.0, 0.7, 0.4)
// Pastel:         d = vec3(0.263, 0.416, 0.557)
// Neon synthwave: d = vec3(0.5, 0.5, 0.5)       b = vec3(0.5, 0.5, 0.5)
// Deep ocean:     d = vec3(0.8, 0.5, 0.2)       b = vec3(0.3, 0.3, 0.5)
// Fire/lava:      d = vec3(0.0, 0.25, 0.25)     a = vec3(0.5, 0.2, 0.0)
// Northern lights:d = vec3(0.1, 0.4, 0.7)       b = vec3(0.7, 0.4, 0.7)
// Cyberpunk:      d = vec3(0.9, 0.3, 0.6)       c = vec3(2.0, 1.0, 0.5)
```

### Simplified Palette (fixed a/b/c)

For Hypno 2 CC-mapped parameters, expose just the d phase:

```glsl
// Build preset palettes into a single uniform choice
uniform float palette_choice;  // CC N — 0.0–1.0 maps to different presets

vec3 palette(float t) {
    vec3 a = vec3(0.5);
    vec3 b = vec3(0.5);
    vec3 c = vec3(1.0);
    
    // Blend between two preset phases
    vec3 d1 = vec3(0.0, 0.33, 0.67);   // rainbow
    vec3 d2 = vec3(0.263, 0.416, 0.557); // pastel
    vec3 d = mix(d1, d2, palette_choice);
    
    return a + b * cos(6.28318 * (c * t + d));
}
```

## HSV → RGB (Branchless)

Fast conversion, good for audio-reactive hue shifts:

```glsl
vec3 hsv2rgb(vec3 c) {
    vec3 rgb = clamp(abs(mod(c.x * 6.0 + vec3(0.0, 4.0, 2.0), 6.0) - 3.0) - 1.0, 0.0, 1.0);
    return c.z * mix(vec3(1.0), rgb, c.y);
}
// c.x = hue (0–1), c.y = saturation (0–1), c.z = value (0–1)
```

### Audio-Reactive Hue Shift Pattern

```glsl
uniform float hue;           // CC 63 — OKLab hue shift is built-in, but custom control is fine
uniform float saturation;    // CC 64 — color intensity
uniform float brightness;    // CC 65 — overall level

vec3 colorize(float t) {
    return hsv2rgb(vec3(
        fract(t + hue),       // shift hue based on pattern value + CC
        saturation * 0.8 + 0.2,
        brightness * 0.7 + 0.3
    ));
}
```

## Mix Chain Palette (Most Flexible)

Build complex color maps by layering mix() calls:

```glsl
vec3 palette_mix(float t) {
    vec3 col = vec3(0.2, 0.1, 0.4);                    // deep purple base
    col = mix(col, vec3(0.3, 0.05, 0.05), t);           // → dark red
    col = mix(col, vec3(0.9, 0.9, 0.9), t * t);         // → white (squared for late transition)
    col = mix(col, vec3(0.0, 0.2, 0.4), smoothstep(0.6, 0.8, t)); // → blue highlights
    return col * t * 2.0;
}
```

## Gray → Color Tinting

Map grayscale to tinted color (cheapest technique of all):

```glsl
uniform float tint_r;   // CC N
uniform float tint_g;   // CC N+1
uniform float tint_b;   // CC N+2

vec3 tint(float gray) {
    // Gray input (0–1) mapped to colored output
    vec3 tint_color = vec3(tint_r, tint_g, tint_b);
    return gray * tint_color;
}
```

## Full Hypno 2 Shader: Noise + Palette

```glsl
uniform vec2 resolution;
uniform float time;
uniform float speed;          // CC 0 — animation speed
uniform float scale;          // CC 1 — noise density
uniform float palette_idx;    // CC 2 — palette selection (0–1 cycles presets)
uniform float brightness;     // CC 3 — output brightness
uniform float color_shift;    // CC 4 — hue offset

// Include hash(), noise(), and fbm() from noise-generators.md

vec3 palette(float t, float idx) {
    vec3 a = vec3(0.5);
    vec3 b = vec3(0.5);
    vec3 c = vec3(1.0);
    // Cycle through 4 preset phases
    float phase_idx = fract(idx) * 4.0;
    vec3 d = mix(
        mix(vec3(0.0, 0.33, 0.67), vec3(0.0, 0.10, 0.20), smoothstep(0.0, 1.0, phase_idx)),
        mix(vec3(0.263, 0.416, 0.557), vec3(0.5, 0.5, 0.5), smoothstep(1.0, 2.0, phase_idx)),
        smoothstep(1.0, 3.0, phase_idx)
    );
    return a + b * cos(6.28318 * (c * (t + color_shift) + d));
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = fragCoord / resolution.xy;
    vec2 p = uv * scale;
    p += vec2(time * speed * 0.1, time * speed * 0.07);
    
    float n = fbm(p);
    vec3 col = palette(n, palette_idx) * brightness;
    
    fragColor = vec4(col, 1.0);
}
```

## Performance

All palette techniques are **O(1) with negligible cost** on Pi 5:
- Cosine palette: ~6 multiply-add ops
- HSV → RGB: ~12 ops
- Mix chain: ~4 mix() calls (~16 ops)
- All run at 1080p @ 60 fps with overhead to spare

## See Also

- `noise-generators.md` — Generate the scalar values to colorize
- `domain-warping.md` — Warp coordinates before feeding to a palette for organic color flow
- `voronoi-patterns.md` — Voronoi distance fields pair beautifully with palettes
