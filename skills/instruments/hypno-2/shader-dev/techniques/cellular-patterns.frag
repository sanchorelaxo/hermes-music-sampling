// cellular-patterns.frag — Hypno 2 Voronoi cellular / stained glass patterns
// Technique: voronoi-patterns + color-palettes + edge-detection
// 5 CC parameters.

precision mediump float;

uniform vec2 resolution;
uniform float time;

uniform float scale;       // CC 0 — voronoi cell density (2.0=sparse, 15.0=dense)
uniform float edge_width;  // CC 1 — border thickness (0.01=thin, 0.1=thick)
uniform float palette_sel; // CC 2 — palette phase (0.0=rainbow, 1.0=pastel)
uniform float speed;       // CC 3 — animation speed (0=frozen, 1.0=full)
uniform float brightness;  // CC 4 — output brightness (0.5=dark, 1.5=bright)

// ──────────── HASH / NOISE ────────────
float hash(vec2 p) {
    p = fract(p * 0.6180339887);
    p *= 25.0;
    return fract(p.x * p.y * (p.x + p.y));
}

vec2 hash22(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * vec3(0.1031, 0.1030, 0.0973));
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.xx + p3.yz) * p3.zy);
}

// ──────────── VORONOI EDGE ────────────
// Returns vec2: x = nearest distance, y = edge distance (d2 - d1)
vec2 voronoiEdge(vec2 p) {
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

// ──────────── COSINE PALETTE ────────────
vec3 palette(float t, float idx) {
    vec3 a = vec3(0.5);
    vec3 b = vec3(0.5);
    vec3 c = vec3(1.0);
    vec3 d = mix(vec3(0.0, 0.33, 0.67), vec3(0.263, 0.416, 0.557), idx);
    return a + b * cos(6.28318 * (c * t + d));
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = fragCoord / resolution.xy;
    vec2 p = uv * scale;

    vec2 ve = voronoiEdge(p);

    // Edge mask from border distance
    float edge = smoothstep(0.0, edge_width * 0.05, ve.y);

    // Dual coloring: cells from palette A, borders from palette B
    vec3 cellCol = palette(ve.x * 3.0 + time * speed * 0.2, palette_sel);
    vec3 borderCol = palette(ve.y * 5.0, fract(palette_sel + 0.5));

    vec3 col = mix(borderCol, cellCol, edge) * brightness;
    fragColor = vec4(col, 1.0);
}