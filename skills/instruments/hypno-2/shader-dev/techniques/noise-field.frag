// noise-field.frag — Hypno 2 animated procedural noise field
// Clouds, terrain, smooth textures, smoke
// Technique: noise-generators + color-palettes
// 5 CC parameters.

precision mediump float;

uniform vec2 resolution;
uniform float time;

uniform float speed;       // CC 0 — animation speed (0=frozen, 1.0=full)
uniform float scale;       // CC 1 — noise zoom/density (1.0=coarse, 10.0=fine)
uniform float contrast;    // CC 2 — brightness contrast (0.5=flat, 2.0=high)
uniform float palette_sel; // CC 3 — palette phase (0.0=rainbow, 1.0=pastel)
uniform float brightness;  // CC 4 — output brightness (0.5=dark, 1.5=bright)

// ──────────── HASH / NOISE ────────────
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

const mat2 mtx = mat2(0.80, 0.60, -0.60, 0.80);

// 4-octave FBM — Pi 5 safe
float fbm(vec2 p) {
    float f = 0.0;
    f += 0.500000 * noise(p); p = mtx * p * 2.02;
    f += 0.250000 * noise(p); p = mtx * p * 2.03;
    f += 0.125000 * noise(p); p = mtx * p * 2.01;
    f += 0.062500 * noise(p);
    return f / 0.9375;
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

    // Animate: global drift
    p += vec2(time * speed * 0.1, time * speed * 0.07);

    float n = fbm(p);

    // Contrast adjustment
    n = (n - 0.5) * contrast + 0.5;
    n = clamp(n, 0.0, 1.0);

    vec3 col = palette(n, palette_sel) * brightness;
    fragColor = vec4(col, 1.0);
}