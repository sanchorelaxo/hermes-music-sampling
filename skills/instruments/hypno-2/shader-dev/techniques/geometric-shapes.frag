// geometric-shapes.frag — Hypno 2 SDF geometric composition
// Circles, polygons, rectangles with boolean ops and color gradients
// Technique: sdf-2d-shapes + edge-detection + blend-modes
// 5 CC parameters.

precision mediump float;

uniform vec2 resolution;
uniform float time;

uniform float rotation;    // CC 0 — overall scene rotation (0–2π)
uniform float shape_size;  // CC 1 — shape scale factor (0.2–1.0)
uniform float blend_mode;  // CC 2 — 0=union, 0.5=subtract, 1.0=smooth
uniform float hue;         // CC 3 — hue rotation offset (0.0–1.0)
uniform float pulse;       // CC 4 — size pulsing (0.0=none, 0.5=intense)

// ──────────── SDF PRIMITIVES ────────────
float sdCircle(vec2 p, float r) {
    return length(p) - r;
}

float sdBox(vec2 p, vec2 b) {
    vec2 d = abs(p) - b;
    return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0);
}

float sdTriangle(vec2 p, float r) {
    const float k = 1.7320508; // sqrt(3)
    p.x = abs(p.x) - r;
    p.y = p.y + r / k;
    if (p.x + k * p.y > 0.0) p = vec2(p.x - k * p.y, -k * p.x - p.y) / 2.0;
    p.x -= clamp(p.x, -2.0 * r, 0.0);
    return -length(p) * sign(p.y);
}

// Boolean ops
float opUnion(float d1, float d2) { return min(d1, d2); }
float opSubtract(float d1, float d2) { return max(d1, -d2); }
float opSmoothUnion(float d1, float d2, float k) {
    float h = clamp(0.5 + 0.5 * (d2 - d1) / k, 0.0, 1.0);
    return mix(d2, d1, h) - k * h * (1.0 - h);
}

// Anti-aliased fill
float fill(float d) {
    return 1.0 - smoothstep(0.0, 2.0 / resolution.y, d);
}

// ──────────── HSV → RGB ────────────
vec3 hsv2rgb(vec3 c) {
    vec3 rgb = clamp(abs(mod(c.x * 6.0 + vec3(0.0, 4.0, 2.0), 6.0) - 3.0) - 1.0, 0.0, 1.0);
    return c.z * mix(vec3(1.0), rgb, c.y);
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 p = (fragCoord - 0.5 * resolution.xy) / resolution.y;

    // Rotate
    float angle = rotation * 6.28318;
    float c = cos(angle), s = sin(angle);
    p = mat2(c, -s, s, c) * p;

    // Pulse size
    float pulseFactor = 1.0 + pulse * 0.3 * sin(time * 2.0);
    float sz = shape_size * pulseFactor;

    // Build a composed scene: central circle + two side bars
    float d = sdCircle(p, sz * 0.4);
    d = opUnion(d, sdBox(p - vec2(sz * 0.5, 0.0), vec2(sz * 0.12, sz * 0.3)));
    d = opUnion(d, sdBox(p + vec2(sz * 0.5, 0.0), vec2(sz * 0.12, sz * 0.3)));

    // Apply blend mode via CC uniform
    float d2 = sdCircle(p - vec2(0.0, sz * 0.25), sz * 0.2);
    if (blend_mode < 0.33) {
        d = opUnion(d, d2);
    } else if (blend_mode < 0.66) {
        d = opSubtract(d, d2);
    } else {
        d = opSmoothUnion(d, d2, 0.05);
    }

    // Render
    float mask = fill(d);

    // Color by angle + hue
    float t = fract(atan(p.y, p.x) / 6.28318 + hue);
    vec3 col = hsv2rgb(vec3(t, 0.7, 1.0)) * mask;

    fragColor = vec4(col, 1.0);
}