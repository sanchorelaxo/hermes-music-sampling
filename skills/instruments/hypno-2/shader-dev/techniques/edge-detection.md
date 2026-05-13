# Edge Detection — Hypno 2

Edge detection creates outlines, glow halos, and glitch aesthetics from any scalar field (noise, SDF shapes, Voronoi). It's a post-processing technique applied to your pattern before coloring.

## Core Principle

Sample the scalar field at neighboring pixels and compute the gradient. Where the gradient is steep → edge. Where flat → no edge.

## Sobel Operator (Classic Edge Detection)

Sample 8 neighbors around each pixel. Standard for image processing:

```glsl
float sobel(vec2 p, float step) {
    // Sample 3×3 neighborhood
    float tl = pattern(p + vec2(-step,  step));
    float t  = pattern(p + vec2( 0.0,   step));
    float tr = pattern(p + vec2( step,  step));
    float l  = pattern(p + vec2(-step,   0.0));
    float r  = pattern(p + vec2( step,   0.0));
    float bl = pattern(p + vec2(-step, -step));
    float b  = pattern(p + vec2( 0.0,  -step));
    float br = pattern(p + vec2( step, -step));
    
    // Sobel kernels
    float gx = -tl - 2.0 * l - bl + tr + 2.0 * r + br;
    float gy = -tl - 2.0 * t - tr + bl + 2.0 * b + br;
    
    return sqrt(gx * gx + gy * gy);  // gradient magnitude
}
```

### Edge Outline (Dark)

```glsl
float n = pattern(p);              // base pattern
float e = sobel(p, 1.0 / resolution.y);  // edge intensity
float edge = smoothstep(0.1, 0.3, e);    // threshold edge
vec3 col = palette(n) * (1.0 - edge * 0.8);  // darken at edges
```

### Glow Halo (Bright)

```glsl
float n = pattern(p);
float e = sobel(p, 1.0 / resolution.y);
float glow = smoothstep(0.05, 0.2, e);
vec3 col = palette(n) + glow * 0.5;  // brighten at edges
```

## Laplacian Operator (Faster, Single-Pass)

Only 4 neighbors needed:

```glsl
float laplacian(vec2 p, float step) {
    float center = pattern(p);
    float n = pattern(p + vec2(0.0,  step));
    float s = pattern(p + vec2(0.0, -step));
    float e = pattern(p + vec2( step, 0.0));
    float w = pattern(p + vec2(-step, 0.0));
    
    return abs(4.0 * center - n - s - e - w);
}
```

### 2×2 Laplacian (Cheapest)

Fastest edge detection — only 3 extra samples:

```glsl
float laplacian2(vec2 p, float step) {
    float c = pattern(p);
    return abs(c - pattern(p + vec2(step, 0.0)))
         + abs(c - pattern(p + vec2(0.0, step)));
}
```

## Fwidth-Based Edge (Fastest)

Uses GPU's built-in derivative. One sample, but lower quality:

```glsl
float edge_fwidth(float n) {
    return length(vec2(dFdx(n), dFdy(n)));
}
// dFdx/dFdy return screen-space derivatives
// Quality varies by GPU — acceptable on Pi 5 for subtle effects
```

## Edge-Only Render (Wireframe / Line Art)

Render only the edges against black for a wireframe look:

```glsl
float n = pattern(p);
float e = sobel(p, 2.0 / resolution.y);
float edge = smoothstep(0.08, 0.25, e);

// Edge-only: color edges, leave rest dark
vec3 edgeColor = palette(n, 1.0);  // palette B for edges
vec3 col = edgeColor * edge;

// Subtle fill in dark areas
float fill = smoothstep(0.4, 0.5, n) * 0.15;
col += vec3(fill);
```

## Dual Color Edges (Fill + Edge Different Palettes)

```glsl
float n = pattern(p);
float e = sobel(p, 2.0 / resolution.y);
float edge = smoothstep(0.05, 0.2, e);

vec3 fillColor = palette(n, palette_a);
vec3 edgeColor = palette(e, palette_b);

vec3 col = mix(fillColor, edgeColor, edge);
```

## Glitch Effect (Difference Blend + Edge)

```glsl
// Offset copy of the pattern creates difference
float n = pattern(p);
float n_offset = pattern(p + vec2(sin(time) * 0.02, 0.0));
float diff = abs(n - n_offset);

// Edge detect the difference — enhances glitch tearing
float e = sobel(p, 2.0 / resolution.y);
float glitch = max(diff, e * 0.5);

vec3 col = palette(n, 0.0);
col = mix(col, vec3(1.0, 0.0, 1.0), glitch);  // magenta glitch artifacts
```

## Full Hypno 2 Shader: Voronoi Wireframe

```glsl
uniform vec2 resolution;
uniform float time;
uniform float scale;          // CC 0 — voronoi cell density
uniform float edge_thick;     // CC 1 — line thickness
uniform float edge_bright;    // CC 2 — edge brightness
uniform float palette_sel;    // CC 3 — color palette
uniform float speed;          // CC 4 — animation speed

// Include voronoiEdge(), palette() from other techniques

float sobel(vec2 p, float step) {
    float tl = voronoiEdge(p + vec2(-step,  step) * scale, time).x;
    float t  = voronoiEdge(p + vec2( 0.0,   step) * scale, time).x;
    float tr = voronoiEdge(p + vec2( step,  step) * scale, time).x;
    float l  = voronoiEdge(p + vec2(-step,   0.0) * scale, time).x;
    float r  = voronoiEdge(p + vec2( step,   0.0) * scale, time).x;
    float bl = voronoiEdge(p + vec2(-step, -step) * scale, time).x;
    float b  = voronoiEdge(p + vec2( 0.0,  -step) * scale, time).x;
    float br = voronoiEdge(p + vec2( step, -step) * scale, time).x;
    float gx = -tl - 2.0 * l - bl + tr + 2.0 * r + br;
    float gy = -tl - 2.0 * t - tr + bl + 2.0 * b + br;
    return sqrt(gx * gx + gy * gy);
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = fragCoord / resolution.xy;
    vec2 p = uv;
    
    // Get voronoi fill + natural edges
    vec2 ve = voronoiEdge(p * scale, time);
    
    // Sobel on the distance field for cleaner edges
    float e = sobel(uv, 1.0 / resolution.y);
    float edge = smoothstep(0.02, 0.02 + edge_thick * 0.1, e);
    
    // Dual color
    vec3 fillCol = palette(ve.x * 2.0 + time * speed * 0.1, palette_sel);
    vec3 edgeCol = palette(fract(ve.x * 5.0), fract(palette_sel + 0.5)) * edge_bright;
    
    vec3 col = mix(fillCol, edgeCol, edge);
    
    fragColor = vec4(col, 1.0);
}
```

## Performance

| Method | Extra samples | Pi 5 cost |
|--------|--------------|-----------|
| fwidth | 0 (GPU derivative) | Free (but quality varies) |
| Laplacian 2×2 | 2 extra | Very low |
| Laplacian 4-neighbor | 4 extra | Low |
| Sobel 3×3 | 8 extra | Moderate — 8× pattern cost |

**Recommendation:** Use Sobel for quality (composited shapes, voronoi lines), Laplacian for speed (noise fields where edges are less critical).

## See Also

- `voronoi-patterns.md` — Natural Voronoi edges vs Sobel edges compared
- `blend-modes.md` — Difference blend + edge detection = glitch pipeline
- `sdf-2d-shapes.md` — SDF shapes naturally produce clean edges via fill(), so edge detection often isn't needed for geometry
