// feedback-field.frag — Hypno 2 single-pass faux feedback / ghosting
// Accumulated echo trails, spiral feedback, zoom echo
// Technique: feedback-effects + noise-generators + blend-modes
// 5 CC parameters.

precision mediump float;

uniform vec2 resolution;
uniform float time;

uniform float feedback_strength; // CC 0 — ghost intensity (0=none, 1.0=intense)
uniform float scale;             // CC 1 — base pattern scale (0.5=out, 4.0=in)
uniform float spiral;            // CC 2 — spiral twist amount (0=radial, 1.0=heavy)
uniform float palette_sel;      // CC 3 — palette phase (0.0=rainbow, 1.0=pastel)
uniform float speed;             // CC 4 — animation speed (0=frozen, 1.0=full)

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
    return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x,
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
    vec2 uv = fragCoord / resolution.xy;
    vec2 p = (fragCoord - 0.5 * resolution.xy) / resolution.y;

    p *= scale;
    p += vec2(time * speed * 0.1, time * speed * 0.07);

    // Base layer
    float n = fbm(p);
    vec3 col = palette(n, palette_sel);

    // Accumulate spiral ghost echoes
    float alpha = 1.0;
    float spiralStrength = spiral * 0.3;
    vec2 offset = vec2(0.0);

    for (int i = 0; i < 6; i++) {
        if (alpha < 0.05) break;

        float t = float(i) * 0.02;
        // Spiral: each echo rotated slightly more
        float angle = float(i) * spiralStrength;
        float cs = cos(angle), sn = sin(angle);
        offset = mat2(cs, -sn, sn, cs) * (offset + vec2(0.01));

        float ghostN = fbm(p + offset);
        vec3 ghost = palette(ghostN, fract(palette_sel + float(i) * 0.1));
        col = mix(col, ghost, alpha * feedback_strength * 0.5);
        alpha *= 0.6;
    }

    fragColor = vec4(col, 1.0);
}