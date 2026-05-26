// kaleidoscope.frag — Hypno 2 kaleidoscope / mirror symmetry / mandalas
// Technique: polar-uv-manipulation + color-palettes
// 5 CC parameters.

precision mediump float;

uniform vec2 resolution;
uniform float time;

uniform float segments;    // CC 0 — mirror segments (2–16)
uniform float rotation;    // CC 1 — kaleidoscope rotation (0–2π)
uniform float scale;       // CC 2 — zoom into center (0.5=wide, 5.0=zoomed)
uniform float speed;       // CC 3 — animation speed (0=frozen, 1.0=full)
uniform float palette_idx; // CC 4 — palette phase (0.0=rainbow, 1.0=pastel)

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

// ──────────── COSINE PALETTE ────────────
vec3 palette(float t, float idx) {
    vec3 a = vec3(0.5);
    vec3 b = vec3(0.5);
    vec3 c = vec3(1.0);
    vec3 d = mix(vec3(0.0, 0.33, 0.67), vec3(0.263, 0.416, 0.557), idx);
    return a + b * cos(6.28318 * (c * t + d));
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 p = (fragCoord - 0.5 * resolution.xy) / resolution.y;

    // Segments from CC uniform: 2–16
    float segs = floor(segments * 14.0) + 2.0;

    // Rotation
    float rot = rotation * 6.28318;

    // Kaleidoscope transform
    float angle = atan(p.y, p.x) + rot;
    float radius = length(p);
    angle = mod(angle, 6.28318 / segs);
    angle = abs(angle - 3.14159 / segs);
    vec2 kp = vec2(cos(angle), sin(angle)) * radius;

    // Scale and drift
    kp *= scale;
    kp += vec2(time * speed * 0.1, time * speed * 0.07);

    // Noise inside mirrored space
    float n = fbm(kp + time * speed * 0.2);

    // Color from angle in original space + palette
    float origAngle = atan(p.y, p.x) / 6.28318 + 0.5;
    vec3 col = palette(n + origAngle, palette_idx);

    fragColor = vec4(col, 1.0);
}