# Voronoi Patterns — Hypno 2

Voronoi (cellular) noise produces honeycomb, stained glass, and biological-looking patterns. It's more expensive than value noise but creates uniquely structured visuals that pair beautifully with color palettes. Safe on Pi 5 at moderate cell counts.

## Core Principle

Divide space into cells around random feature points. Each pixel's value comes from its relationship to nearby feature points (distance to nearest, second-nearest, edge proximity, etc.).

## Implementation

### Voronoi Distance (Nearest-Neighbor)

```glsl
float voronoi(vec2 p) {
    vec2 i = floor(p);   // cell index
    vec2 f = fract(p);   // position within cell
    
    float minDist = 1.0;  // max possible in unit cell
    
    // Check 3×3 neighborhood of cells
    for (int y = -1; y <= 1; y++) {
        for (int x = -1; x <= 1; x++) {
            vec2 neighbor = vec2(float(x), float(y));
            // Random point within this neighbor cell
            vec2 point = hash22(i + neighbor);
            // Distance from pixel to this feature point
            float dist = length(neighbor + point - f);
            minDist = min(minDist, dist);
        }
    }
    
    return minDist;
}
```

### Voronoi with Edge Distance (Stained Glass)

Returns both nearest and second-nearest distances for edge rendering:

```glsl
// Returns vec2: x = nearest distance, y = edge distance (2nd - 1st)
vec2 voronoiEdge(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    
    float d1 = 1.0;  // nearest
    float d2 = 1.0;  // second-nearest
    
    for (int y = -1; y <= 1; y++) {
        for (int x = -1; x <= 1; x++) {
            vec2 neighbor = vec2(float(x), float(y));
            vec2 point = hash22(i + neighbor);
            float dist = length(neighbor + point - f);
            
            if (dist < d1) {
                d2 = d1;
                d1 = dist;
            } else if (dist < d2) {
                d2 = dist;
            }
        }
    }
    
    return vec2(d1, d2 - d1);  // x = fill, y = edge thickness
}
```

### Animated Voronoi (Moving Feature Points)

```glsl
float voronoi(vec2 p, float time) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    
    float minDist = 1.0;
    
    for (int y = -1; y <= 1; y++) {
        for (int x = -1; x <= 1; x++) {
            vec2 neighbor = vec2(float(x), float(y));
            // Animate feature points
            vec2 point = hash22(i + neighbor);
            point = 0.5 + 0.5 * sin(time * 0.5 + 6.28318 * point);
            float dist = length(neighbor + point - f);
            minDist = min(minDist, dist);
        }
    }
    
    return minDist;
}
```

## Rendering Styles

### Fill (solid cells)
```glsl
float v = voronoi(p * scale);
vec3 col = palette(v, palette_idx);  // color by distance to nearest point
```

### Cell ID (each cell gets a unique color)
```glsl
// Returns the ID of the nearest feature point
float voronoiID(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    
    float minDist = 1.0;
    float cellID = 0.0;
    
    for (int y = -1; y <= 1; y++) {
        for (int x = -1; x <= 1; x++) {
            vec2 neighbor = vec2(float(x), float(y));
            vec2 point = hash22(i + neighbor);
            float dist = length(neighbor + point - f);
            if (dist < minDist) {
                minDist = dist;
                cellID = hash(i + neighbor);  // hash the cell as color ID
            }
        }
    }
    return cellID;
}

// Use: vec3 col = palette(voronoiID(p * scale), palette_idx);
```

### Edge Outlines (stained glass, wireframe)
```glsl
vec2 ve = voronoiEdge(p * scale);
float edge = smoothstep(0.0, 0.02, ve.y);  // edge = 1 where borders are
vec3 col = mix(cellColor, vec3(0.0), edge); // dark edges
```

### Dual Coloring (fill + edge in two colors)
```glsl
vec2 ve = voronoiEdge(p * scale);
float edge = smoothstep(0.0, 0.03, ve.y);
vec3 fillColor = palette(ve.x, 0.0);  // palette A for fills
vec3 edgeColor = palette(ve.y, 1.0);  // palette B for edges
vec3 col = mix(edgeColor, fillColor, edge);
```

## Performance Tuning

| Parameter | Effect | Pi 5 impact |
|-----------|--------|-------------|
| Cell scale | Fewer cells = faster | Scale < 3: very fast |
| 3×3 vs 5×5 search | 5×5 needed for sparse cells | Use 3×3 when cells < 1.5× per pixel |
| hash complexity | Simpler hash = faster | Use `hash()` not `hash22()` in inner loop |
| Smooth Voronoi | `smoothstep()` on distances | Adds ~2 ops per cell, negligible |

### Pi 5 Optimization: Voronoi Lite

For dense cell grids, skip the edge calculation:

```glsl
float voronoiFast(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    float d = 1.0;
    // Only check 2×2 grid (cells that can actually win at this density)
    for (int y = 0; y <= 1; y++) {
        for (int x = 0; x <= 1; x++) {
            vec2 point = hash22(i + vec2(x, y));
            d = min(d, length(vec2(x, y) + point - f));
        }
    }
    return d;
}
// Only valid when cell density is high (scale > 5)
// At low density, feature points outside 2×2 can win — use 3×3
```

## Full Hypno 2 Shader: Stained Glass

```glsl
uniform vec2 resolution;
uniform float time;
uniform float scale;          // CC 0 — voronoi cell density
uniform float edge_width;     // CC 1 — border thickness
uniform float palette_sel;    // CC 2 — color palette selector
uniform float speed;          // CC 3 — animation speed
uniform float brightness;     // CC 4 — output brightness

// Include hash(), hash22(), palette() from other techniques

vec2 voronoiEdge(vec2 p, float time) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    float d1 = 1.0, d2 = 1.0;
    for (int y = -1; y <= 1; y++) {
        for (int x = -1; x <= 1; x++) {
            vec2 n = vec2(float(x), float(y));
            vec2 point = hash22(i + n);
            point = 0.5 + 0.5 * sin(time * speed + 6.28318 * point);
            float dist = length(n + point - f);
            if (dist < d1) { d2 = d1; d1 = dist; }
            else if (dist < d2) { d2 = dist; }
        }
    }
    return vec2(d1, d2 - d1);
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = fragCoord / resolution.xy;
    vec2 p = uv * scale;
    
    vec2 ve = voronoiEdge(p, time);
    
    float edge = smoothstep(0.0, edge_width * 0.05, ve.y);
    vec3 cellCol = palette(ve.x * 3.0 + time * speed * 0.2, palette_sel);
    vec3 borderCol = palette(ve.y * 5.0, fract(palette_sel + 0.5));
    vec3 col = mix(borderCol, cellCol, edge) * brightness;
    
    fragColor = vec4(col, 1.0);
}
```

## See Also

- `color-palettes.md` — Voronoi distance fields make excellent palette inputs
- `polar-uv-manipulation.md` — Voronoi in polar space = mandala patterns
- `edge-detection.md` — Alternative edge rendering for Voronoi boundaries
