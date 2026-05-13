# 2D SDF Shapes — Hypno 2

Signed distance functions for 2D shapes — circles, rectangles, polygons, lines, and rounded forms. SDFs produce anti-aliased edges naturally and compose effortlessly with noise fields. Perfect for geometric generative visuals.

## Core Principle

An SDF returns the **signed distance** from a point to the nearest edge of a shape:
- Negative = inside the shape
- Zero = on the edge
- Positive = outside the shape

Use `smoothstep()` to create anti-aliased shape masks from the distance field.

## Basic SDF Functions

### Circle
```glsl
float sdCircle(vec2 p, float r) {
    return length(p) - r;
}
```

### Rectangle (centered)
```glsl
float sdBox(vec2 p, vec2 b) {
    vec2 d = abs(p) - b;
    return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0);
}
```

### Rounded Rectangle
```glsl
float sdRoundedBox(vec2 p, vec2 b, float r) {
    vec2 d = abs(p) - b + r;
    return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0) - r;
}
```

### Line Segment
```glsl
float sdSegment(vec2 p, vec2 a, vec2 b) {
    vec2 pa = p - a, ba = b - a;
    float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
    return length(pa - ba * h);
}
```

### Equilateral Triangle
```glsl
float sdTriangle(vec2 p, float r) {
    const float k = sqrt(3.0);
    p.x = abs(p.x) - r;
    p.y = p.y + r / k;
    if (p.x + k * p.y > 0.0) p = vec2(p.x - k * p.y, -k * p.x - p.y) / 2.0;
    p.x -= clamp(p.x, -2.0 * r, 0.0);
    return -length(p) * sign(p.y);
}
```

### Regular N-gon
```glsl
float sdPolygon(vec2 p, int n, float r) {
    float an = 3.14159265 / float(n);
    float acs = cos(an), asn = sin(an);
    vec2 pn = vec2(p.x, abs(p.y));
    pn = pn - 2.0 * min(dot(vec2(-asn, acs), pn), 0.0) * vec2(-asn, acs);
    pn = pn - clamp(pn, -r * vec2(acs, asn), r * vec2(acs, asn));
    return length(pn) * sign(pn.y);
}
```

### Star
```glsl
float sdStar(vec2 p, int n, float r, float m) {
    float an = 3.14159265 / float(n);
    float acs = cos(an), asn = sin(an);
    vec2 pn = vec2(p.x, abs(p.y));
    pn = pn - 2.0 * min(dot(vec2(-asn, acs), pn), 0.0) * vec2(-asn, acs);
    pn = pn - r * vec2(acs, asn);
    float w = m * (pn.x * acs + pn.y * asn) + r;
    return length(pn - w * vec2(acos(an), asin(an)) * an) * sign(w);
}
```

## Anti-Aliased Shape Rendering

```glsl
// Smooth shape fill from SDF
float fill(float d) {
    return 1.0 - smoothstep(0.0, 2.0 / resolution.y, d);
    // 2.0/resolution.y = ~2-pixel AA band (works at any resolution)
}

// Smooth stroke/outline
float stroke(float d, float width) {
    return 1.0 - smoothstep(0.0, 2.0 / resolution.y, abs(d) - width * 0.5);
}
```

## Compositing Shapes

### Boolean Operations
```glsl
// Union (combine)
float opUnion(float d1, float d2) { return min(d1, d2); }

// Subtraction (cut out)
float opSubtract(float d1, float d2) { return max(d1, -d2); }

// Intersection (overlap only)
float opIntersect(float d1, float d2) { return max(d1, d2); }

// Smooth blend (rounded union)
float opSmoothUnion(float d1, float d2, float k) {
    float h = clamp(0.5 + 0.5 * (d2 - d1) / k, 0.0, 1.0);
    return mix(d2, d1, h) - k * h * (1.0 - h);
}
```

### Repetition (tile/grid)
```glsl
vec2 opRepeat(vec2 p, vec2 spacing) {
    return mod(p + spacing * 0.5, spacing) - spacing * 0.5;
}
```

## Full Hypno 2 Shader: Geometric Composition

```glsl
uniform vec2 resolution;
uniform float time;
uniform float rotation;       // CC 0 — overall rotation
uniform float shape_size;     // CC 1 — shape scale
uniform float blend_mode;     // CC 2 — 0=union, 0.5=subtract, 1.0=smooth blend
uniform float hue;            // CC 3 — color shift
uniform float pulse;          // CC 4 — size pulsing amount

// Include SDF functions from above
// Include hsv2rgb from color-palettes.md

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 p = (fragCoord - 0.5 * resolution.xy) / resolution.y;
    
    // Rotate
    float angle = rotation * 6.28318;
    p = mat2(cos(angle), -sin(angle), sin(angle), cos(angle)) * p;
    
    // Pulse size
    float s = shape_size * (1.0 + pulse * 0.3 * sin(time * 2.0));
    
    // Build a scene of shapes
    float d = sdCircle(p, s * 0.5);                    // central circle
    d = opUnion(d, sdBox(p - vec2(s * 0.6, 0.0), vec2(s * 0.15)));  // right bar
    d = opUnion(d, sdBox(p + vec2(s * 0.6, 0.0), vec2(s * 0.15)));  // left bar
    
    // Apply blend mode (uniform-driven)
    float d2 = sdCircle(p - vec2(0.0, s * 0.3), s * 0.2);
    if (blend_mode < 0.33) {
        d = opUnion(d, d2);
    } else if (blend_mode < 0.66) {
        d = opSubtract(d, d2);
    } else {
        d = opSmoothUnion(d, d2, 0.1);
    }
    
    // Render with AA
    float mask = fill(d);
    
    // Color
    float t = fract(atan(p.y, p.x) / 6.28318 + hue);
    vec3 col = hsv2rgb(vec3(t, 0.7, 1.0)) * mask;
    
    fragColor = vec4(col, 1.0);
}
```

## Performance

2D SDFs are extremely cheap on Pi 5:
- Circle: ~4 ops
- Box: ~15 ops
- N-gon: ~30 ops
- Multiple shape scenes: safe at 1080p 60 fps
- Smooth blending adds ~10 ops per blend

## See Also

- `edge-detection.md` — Add glow/outline effects to SDF shapes
- `blend-modes.md` — Layer SDF shapes with different blend modes
- `time-animation.md` — Animate shape positions and rotations
