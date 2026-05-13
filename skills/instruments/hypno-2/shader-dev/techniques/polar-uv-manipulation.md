# Polar/UV Manipulation — Hypno 2

Transform screen coordinates to create kaleidoscopes, mandalas, spirals, and radial symmetry effects. These are some of the most visually striking techniques for video synthesis, and they're nearly free on the Pi 5 GPU.

## Core Transforms

### Cartesian → Polar
```glsl
vec2 toPolar(vec2 p) {
    return vec2(atan(p.y, p.x), length(p));
    // Returns: x=angle (-PI to PI), y=radius (0 to ~)
}

vec2 toCartesian(vec2 polar) {
    return vec2(cos(polar.x), sin(polar.x)) * polar.y;
}
```

### Normalized Polar (UI-friendly)
```glsl
vec2 toPolarNorm(vec2 p) {
    // angle: 0–1 (full circle), radius: 0–1 (normalized)
    float angle = atan(p.y, p.x) / (2.0 * 3.14159265) + 0.5;
    float radius = length(p);
    return vec2(angle, radius);
}
```

## Kaleidoscope / Radial Symmetry

Mirror the angle coordinate to create repeating segments:

```glsl
vec2 kaleidoscope(vec2 p, float segments) {
    float angle = atan(p.y, p.x);
    float radius = length(p);
    
    // Wrap angle into N segments
    angle = mod(angle, 2.0 * 3.14159265 / segments);
    // Center each segment
    angle = abs(angle - 3.14159265 / segments);
    
    return vec2(cos(angle), sin(angle)) * radius;
}
```

### Hypno 2 Shader: Kaleidoscope

```glsl
uniform vec2 resolution;
uniform float time;
uniform float segments;       // CC 0 — number of mirror segments (2–16)
uniform float rotation;       // CC 1 — kaleidoscope rotation
uniform float zoom;           // CC 2 — zoom into center
uniform float color_speed;    // CC 3 — hue rotation speed
uniform float offset_x;       // CC 4 — X offset (scroll through pattern)

vec2 kaleidoscope(vec2 p, float segs) {
    float angle = atan(p.y, p.x) + rotation;
    float radius = length(p);
    angle = mod(angle, 2.0 * 3.14159265 / segs);
    angle = abs(angle - 3.14159265 / segs);
    return vec2(cos(angle), sin(angle)) * radius;
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 p = (fragCoord - 0.5 * resolution.xy) / resolution.y;
    
    // Apply kaleidoscope
    int segs = int(segments * 14.0) + 2;  // 2–16 segments
    p = kaleidoscope(p, float(segs));
    
    // Scroll and zoom
    p *= zoom;
    p.x += offset_x;
    
    // Simple pattern in mirrored space
    float pattern = sin(p.x * 10.0) * cos(p.y * 10.0 + time * color_speed);
    pattern = smoothstep(0.3, 0.4, abs(pattern));
    
    // Color from angle in original space
    float orig_angle = atan(p.y - offset_x, p.x) / (2.0 * 3.14159265) + 0.5;
    vec3 col = 0.5 + 0.5 * cos(6.28318 * (orig_angle + vec3(0.0, 0.33, 0.67) + time * color_speed));
    col *= pattern;
    
    fragColor = vec4(col, 1.0);
}
```

## Mirror Symmetry

### Horizontal / Vertical Mirror
```glsl
// Quadrant mirror (4-way symmetry)
p = abs(p);

// Horizontal mirror only
p.x = abs(p.x);

// Diagonal mirror
p = abs(p);
p = p.x > p.y ? p.yx : p.xy;
```

### Rotational Mirror (N-fold)
```glsl
vec2 mirrorN(vec2 p, float n) {
    float angle = atan(p.y, p.x);
    angle = mod(angle, 6.28318 / n) - 3.14159 / n;
    angle = abs(angle);
    return vec2(cos(angle), sin(angle)) * length(p);
}
```

## Spiral / Swirl

```glsl
// Archimedean spiral
vec2 spiral(vec2 p, float turns) {
    float radius = length(p);
    float angle = atan(p.y, p.x) + radius * turns * 6.28318;
    return vec2(cos(angle), sin(angle)) * radius;
}

// Logarithmic zoom spiral
vec2 zoomSpiral(vec2 p, float turns, float zoom) {
    float radius = length(p);
    float logRadius = log(max(radius, 0.001)) * zoom;
    float angle = atan(p.y, p.x) + logRadius * turns * 6.28318;
    return vec2(angle / 6.28318, logRadius);
}
```

## Fisheye / Lens Distortion

```glsl
// Barrel distortion (fisheye)
vec2 fisheye(vec2 p, float strength) {
    float r = length(p);
    float r2 = r * r;
    float factor = 1.0 + strength * r2;
    return p * factor;
}

// Pincushion (inverse fisheye)
vec2 pincushion(vec2 p, float strength) {
    float r = length(p);
    float r2 = r * r;
    float factor = 1.0 / (1.0 + strength * r2);
    return p * factor;
}
```

## Tile / Repeat

```glsl
// Infinite tiling
vec2 tile(vec2 p, vec2 cellSize) {
    return mod(p, cellSize) - cellSize * 0.5;
}

// Mirrored tiling (no seams)
vec2 tileMirrored(vec2 p, vec2 cellSize) {
    vec2 cell = floor(p / cellSize);
    vec2 local = mod(p, cellSize) - cellSize * 0.5;
    // Mirror every other cell
    if (mod(cell.x, 2.0) > 0.5) local.x = -local.x;
    if (mod(cell.y, 2.0) > 0.5) local.y = -local.y;
    return local;
}
```

## Full Hypno 2 Shader: Kaleidoscope Noise

```glsl
uniform vec2 resolution;
uniform float time;
uniform float segments;       // CC 0 — mirror segments (2–16)
uniform float speed;          // CC 1 — animation speed
uniform float scale;          // CC 2 — noise zoom
uniform float warp;           // CC 3 — distortion amount
uniform float palette_sel;    // CC 4 — color palette

// Include hash(), noise(), fbm() from noise-generators.md
// Include palette() from color-palettes.md

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 p = (fragCoord - 0.5 * resolution.xy) / resolution.y;
    
    // Kaleidoscope mirror
    int segs = int(segments * 14.0) + 2;
    float angle = atan(p.y, p.x);
    float radius = length(p);
    angle = mod(angle, 6.28318 / float(segs));
    angle = abs(angle - 3.14159 / float(segs));
    vec2 kp = vec2(cos(angle), sin(angle)) * radius;
    
    // Apply warp and scale to mirrored coordinates
    kp *= scale;
    kp += fbm2(kp + time * speed * 0.1) * warp;  // domain warp inside kaleidoscope
    
    float n = fbm(kp + time * speed * 0.2);
    vec3 col = palette(n + time * speed * 0.1, palette_sel);
    
    fragColor = vec4(col, 1.0);
}
```

## Performance

All coordinate transforms are **O(1)** with negligible cost:
- Polar conversion: ~10 ops
- Kaleidoscope: ~15 ops
- Spiral: ~15 ops
- Mirror/tile: ~10 ops
- Combine freely — the heavy cost comes from what you do *after* the transform (noise, etc.)

## See Also

- `noise-generators.md` — Apply noise to mirrored/warped coordinates
- `voronoi-patterns.md` — Voronoi in polar space creates stunning mandalas
- `domain-warping.md` — Warp coordinates before mirroring for complex symmetry
