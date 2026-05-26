// domain-warping.frag — Hypno 2 single-pass domain warping
// Organic flowing visuals: lava lamp, gas giant, marble, smoke, aurora
// Technique: domain-warping + noise-generators + color-palettes
// 5 CC parameters.

precision mediump float;

uniform vec2 resolution;
uniform float time;

uniform float warp_strength; // CC 0 — warp intensity (0.5=subtle, 3.0=aggressive)
uniform float scale;        // CC 1 — noise zoom (1.0=coarse, 10.0=fine)
uniform float speed;        // CC 2 — animation speed (0=frozen, 1.0=full)
uniform float palette_idx;  // CC 3 — palette phase (0.0=rainbow, 1.0=pastel)
uniform float brightness;   // CC 4 — output brightness (0.5=dark, 1.5=bright)

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

float fbm(vec2 p) {
    float f = 0.0;
    f += 0.500000 * noise(p); p = mtx * p * 2.02;
    f += 0.250000 * noise(p); p = mtx * p * 2.03;
    f += 0.125000 * noise(p); p = mtx * p * 2.01;
    f += 0.062500 * noise(p);
    return f / 0.9375;
}

vec2 fbm2(vec2 p) {
    return vec2(fbm(p), fbm(p + vec2(1.0, 6.2)));
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
    vec2 p = (fragCoord - 0.5 * resolution.xy) / resolution.y;

    p *= scale;

    // Triple warp — classic organic/lava look
    float t = time * speed * 0.5;
    vec2 q = fbm2(p + t * 0.15);
    vec2 r = fbm2(p + q * warp_strength + t * 0.25 + vec2(1.7, 9.2));
    vec2 s = fbm2(p + r * warp_strength + t * 0.35);
    float n = fbm(p + s * warp_strength);

    vec3 col = palette(n, palette_idx) * brightness;
    fragColor = vec4(col, 1.0);
}