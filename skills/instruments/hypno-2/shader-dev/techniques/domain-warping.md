# Domain Warping — Hypno 2

Domain warping is the single most impactful technique for Hypno 2 generative visuals. Feed noise output back as a coordinate offset to create organic, flowing, liquid-like patterns. It's computationally cheap and produces results that look far more complex than they are.

## Core Principle

```
result = fbm(p + fbm(p + fbm(p)))
```

Each FBM layer's output serves as a coordinate offset for the next layer. Deeper nesting = more organic deformation.

## Use Cases on Hypno 2

- Lava lamp / fluid motion
- Gas giant atmosphere bands
- Marble / jade / agate textures
- Smoke / ink in water
- Aurora borealis
- Abstract art backgrounds
- Audio-reactive organic visuals

## Implementation

### Hash + Noise (from noise-generators.md)

```glsl
float hash(vec2 p) {
    p = fract(p * 0.6180339887);
    p *= 25.0;
    return fract(p.x * p.y * (p.x + p.y));
}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x),
               mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
}
```

### FBM (4 octaves — Pi 5 friendly)

```glsl
const mat2 mtx = mat2(0.80, 0.60, -0.60, 0.80);

float fbm(vec2 p) {
    float f = 0.0;
    f += 0.500000 * noise(p); p = mtx * p * 2.02;
    f += 0.250000 * noise(p); p = mtx * p * 2.03;
    f += 0.125000 * noise(p); p = mtx * p * 2.01;
    f += 0.062500 * noise(p);
    return f / 0.9375;
}

// 2D FBM — returns vec2 for coordinate warping (two independent noise fields)
vec2 fbm2(vec2 p) {
    return vec2(fbm(p), fbm(p + vec2(1.0, 6.2)));
}
```

## Warping Patterns

### Single Warp (subtle organic distortion)

```glsl
float pattern(vec2 p) {
    vec2 offset = fbm2(p) * 2.0 - 1.0;  // bipolar offset
    return fbm(p + offset);
}
```

### Double Warp (classic marble/lava look)

```glsl
float pattern(vec2 p) {
    vec2 q = fbm2(p);
    vec2 r = fbm2(p + q);
    return fbm(p + r);
}
```

### Triple Warp (deep organic, gas giant, heavy)

```glsl
float pattern(vec2 p) {
    vec2 q = fbm2(p);
    vec2 r = fbm2(p + q + vec2(1.7, 9.2));
    vec2 s = fbm2(p + r);
    return fbm(p + s);
}
```

### Cascade with Time (animate each layer differently)

```glsl
float pattern(vec2 p, float time) {
    vec2 q = fbm2(p + time * 0.15);
    vec2 r = fbm2(p + q + time * 0.25 + vec2(1.7, 9.2));
    vec2 s = fbm2(p + r + time * 0.35);
    return fbm(p + s);
}
```

## Tuning Parameters

| Parameter | Effect | Range |
|-----------|--------|-------|
| Warp depth (nesting) | More layers = more organic, less recognizable source | 1–3 for Pi 5 |
| Warp strength (multiplier) | How much each layer distorts coordinates | 0.5 (subtle) to 3.0 (aggressive) |
| Base scale | Overall noise zoom | 1.0 (coarse) to 10.0 (fine detail) |
| Time speed per layer | Different speeds create complex flow | 0.05–0.5 per layer |

### Tunable Warp Shader

```glsl
uniform float warp_strength;  // CC N — 0.5 to 3.0
uniform float base_scale;     // CC N+1 — noise zoom
uniform float time_scale;     // CC N+2 — animation speed
uniform float warp_depth;     // CC N+3 — 0=off, 0.33=single, 0.66=double, 1.0=triple

float pattern(vec2 p, float time) {
    p *= base_scale;
    
    vec2 q = fbm2(p + time * time_scale * 0.15) * warp_strength;
    
    // Blend between warp depths using warp_depth uniform
    if (warp_depth > 0.33) {
        vec2 r = fbm2(p + q + time * time_scale * 0.25 + vec2(1.7, 9.2)) * warp_strength;
        q = mix(q, r, smoothstep(0.33, 0.5, warp_depth));
    }
    if (warp_depth > 0.66) {
        vec2 s = fbm2(p + q + time * time_scale * 0.35) * warp_strength;
        q = mix(q, s, smoothstep(0.66, 0.83, warp_depth));
    }
    
    return fbm(p + q);
}
```

> **Pi 5 note:** The `if` branches above are static (based on a uniform) — the GPU will compile them out cleanly. No runtime branching cost.

## Full Hypno 2 Shader: Warped Color Field

```glsl
uniform vec2 resolution;
uniform float time;
uniform float speed;          // CC 0 — animation speed
uniform float scale;          // CC 1 — base noise zoom
uniform float warp_str;       // CC 2 — warp intensity
uniform float palette_idx;    // CC 3 — color palette selector
uniform float brightness;     // CC 4 — output brightness

// Include hash(), noise(), fbm(), fbm2() from above

vec3 palette(float t, float idx) {
    vec3 a = vec3(0.5);
    vec3 b = vec3(0.5);
    vec3 c = vec3(1.0);
    vec3 d = mix(vec3(0.0, 0.33, 0.67), vec3(0.263, 0.416, 0.557), idx);
    return a + b * cos(6.28318 * (c * t + d));
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    // Center and normalize
    vec2 uv = fragCoord / resolution.xy;
    vec2 p = (fragCoord - 0.5 * resolution.xy) / resolution.y;
    
    // Domain warp at chosen scale
    p *= scale;
    
    // Triple warp — classic gas giant look
    vec2 q = fbm2(p + time * speed * 0.15);
    vec2 r = fbm2(p + q * warp_str + time * speed * 0.25 + vec2(1.7, 9.2));
    vec2 s = fbm2(p + r * warp_str + time * speed * 0.35);
    float n = fbm(p + s * warp_str);
    
    // Color
    vec3 col = palette(n, palette_idx) * brightness;
    
    fragColor = vec4(col, 1.0);
}
```

## Performance

| Warp depth | FBM evals per pixel | Cost on Pi 5 |
|------------|-------------------|--------------|
| Single (1 layer) | 3 calls (~12 hash) | Very low — easy 60 fps |
| Double (2 layers) | 5 calls (~20 hash) | Low — 60 fps at 1080p |
| Triple (3 layers) | 7 calls (~28 hash) | Moderate — still 60 fps on Pi 5 |
| Quad+ (4+ layers) | 9+ calls | Diminishing returns, may drop frames |

**Recommendation:** Use double warp as your default. Triple warp for showcase presets. The visual difference between triple and quad is marginal.

## See Also

- `noise-generators.md` — The FBM building blocks
- `color-palettes.md` — Map your warped field to color
- `time-animation.md` — Animate the warp layers at different speeds
