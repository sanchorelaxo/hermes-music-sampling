# Blend Modes — Hypno 2

Photoshop/GIMP-style blend modes implemented in GLSL. Useful for compositing multiple pattern layers, creating glitch effects, and building complex visuals from simple components. All operations are per-pixel and negligible cost.

## Core Blend Functions

All functions take `base` (bottom layer) and `blend` (top layer), return the blended result.

### Normal / Mix
```glsl
vec3 blendNormal(vec3 base, vec3 blend, float opacity) {
    return mix(base, blend, opacity);
}
```

### Multiply (darken — like stacking transparencies)
```glsl
vec3 blendMultiply(vec3 base, vec3 blend) {
    return base * blend;
}
```

### Screen (lighten — inverse multiply)
```glsl
vec3 blendScreen(vec3 base, vec3 blend) {
    return 1.0 - (1.0 - base) * (1.0 - blend);
}
```

### Overlay (multiply + screen based on base luminance)
```glsl
vec3 blendOverlay(vec3 base, vec3 blend) {
    return mix(
        base * blend * 2.0,                        // dark areas: multiply
        1.0 - 2.0 * (1.0 - base) * (1.0 - blend), // bright areas: screen
        step(0.5, base)
    );
}
```

### Soft Light (gentler overlay — great for textures)
```glsl
vec3 blendSoftLight(vec3 base, vec3 blend) {
    vec3 d = mix(
        ((1.0 - base) * base * blend + base * base * (1.0 - blend)) * 2.0,
        sqrt(base) * (2.0 * blend - 1.0) + 2.0 * base * (1.0 - blend),
        step(0.5, blend)
    );
    return mix(base, d, 0.7);  // soft = partial application
}
```

### Hard Light (overlay inverted)
```glsl
vec3 blendHardLight(vec3 base, vec3 blend) {
    return blendOverlay(blend, base);  // swap order
}
```

### Additive (light build-up — glows, fire, lasers)
```glsl
vec3 blendAdd(vec3 base, vec3 blend) {
    return min(base + blend, 1.0);
}
```

### Difference (edge detection, glitch)
```glsl
vec3 blendDifference(vec3 base, vec3 blend) {
    return abs(base - blend);
}
```

### Exclusion (lower-contrast difference)
```glsl
vec3 blendExclusion(vec3 base, vec3 blend) {
    return base + blend - 2.0 * base * blend;
}
```

### Color Dodge (brighten + saturate)
```glsl
vec3 blendColorDodge(vec3 base, vec3 blend) {
    return base / max(1.0 - blend, 0.001);
}
```

### Color Burn (darken + saturate)
```glsl
vec3 blendColorBurn(vec3 base, vec3 blend) {
    return 1.0 - (1.0 - base) / max(blend, 0.001);
}
```

## Blend Mode Router

Single function to switch between modes (for CC-mapped blend selection):

```glsl
uniform float blend_mode;    // CC N — 0–1 maps to different blend modes
uniform float blend_opacity; // CC N+1 — 0–1 mix amount

vec3 applyBlend(vec3 base, vec3 blend, float mode, float opacity) {
    float idx = fract(mode) * 10.0;  // 10 blend modes
    vec3 result;
    
    if (idx < 1.0)       result = blendNormal(base, blend, 1.0);
    else if (idx < 2.0)  result = blendMultiply(base, blend);
    else if (idx < 3.0)  result = blendScreen(base, blend);
    else if (idx < 4.0)  result = blendOverlay(base, blend);
    else if (idx < 5.0)  result = blendSoftLight(base, blend);
    else if (idx < 6.0)  result = blendHardLight(base, blend);
    else if (idx < 7.0)  result = blendAdd(base, blend);
    else if (idx < 8.0)  result = blendDifference(base, blend);
    else if (idx < 9.0)  result = blendColorDodge(base, blend);
    else                 result = blendColorBurn(base, blend);
    
    return mix(base, result, opacity);
}
```

## Layering Patterns

### Noise + SDF Shape with Blend
```glsl
// Base: noise field
vec3 base = palette(fbm(p), 0.0);
// Blend layer: SDF circle
float d = sdCircle(p, 0.3);
float shape = fill(d);
vec3 shapeColor = palette(shape, 1.0);
// Composite with chosen blend mode
vec3 col = applyBlend(base, shapeColor * shape, blend_mode, blend_opacity);
```

### Two Noise Fields, Different Speeds
```glsl
vec3 layer1 = palette(fbm(p + time * 0.1), 0.0);
vec3 layer2 = palette(fbm(p * 1.5 + time * 0.2 + vec2(3.0)), 1.0);
vec3 col = applyBlend(layer1, layer2, blend_mode, blend_opacity);
```

## Full Hypno 2 Shader: Two-Layer Blend

```glsl
uniform vec2 resolution;
uniform float time;
uniform float blend_mode;     // CC 0 — blend mode selector
uniform float blend_amt;      // CC 1 — blend opacity
uniform float speed_a;        // CC 2 — layer A animation speed
uniform float speed_b;        // CC 3 — layer B animation speed
uniform float scale;          // CC 4 — pattern scale

// Include hash(), noise(), fbm(), palette() from other techniques
// Include blend functions from above

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = fragCoord / resolution.xy;
    vec2 p = (fragCoord - 0.5 * resolution.xy) / resolution.y * scale;
    
    // Layer A: slow noise field
    vec3 layerA = palette(fbm(p + time * speed_a * 0.1), 0.0);
    
    // Layer B: faster, offset noise field
    vec3 layerB = palette(fbm(p * 1.3 + time * speed_b * 0.15 + vec2(3.5, 1.2)), 0.5);
    
    vec3 col = applyBlend(layerA, layerB, blend_mode, blend_amt);
    
    fragColor = vec4(col, 1.0);
}
```

## Quick Pick — Best Blends per Use Case

| Use case | Best blend mode |
|----------|----------------|
| Glows / fire / lasers | Additive |
| Dark textures / shadows | Multiply |
| Light rays / fog beams | Screen |
| Vintage film / texture overlay | Soft Light |
| Glitch / datamosh | Difference |
| Color grading / tinting | Overlay |
| HDR blowout / solarize | Color Dodge |
| Crushed blacks / contrast | Color Burn |

## See Also

- `feedback-effects.md` — Blend accumulated echo layers
- `sdf-2d-shapes.md` — Blend shape layers together
- `edge-detection.md` — Difference blend + edge detection = instant glitch
