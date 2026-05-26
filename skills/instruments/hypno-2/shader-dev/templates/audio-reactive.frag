// audio-reactive.frag — Hypno 2 audio / MIDI-reactivity template
// Externally modulated visual: parameters respond to CC modulation
// Technique: time-animation + (any visual technique)
// 5 CC parameters.

precision mediump float;

uniform vec2 resolution;
uniform float time;

uniform float x_offset;    // CC 0 — horizontal pattern offset
uniform float frequency;   // CC 1 — noise frequency/density
uniform float y_offset;    // CC 2 — vertical pattern offset
uniform float hue;         // CC 3 — hue rotation (0.0–1.0 full cycle)
uniform float amplitude;   // CC 4 — pattern amplitude/brightness

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

// ──────────── HSV → RGB ────────────
vec3 hsv2rgb(vec3 c) {
    vec3 rgb = clamp(abs(mod(c.x * 6.0 + vec3(0.0, 4.0, 2.0), 6.0) - 3.0) - 1.0, 0.0, 1.0);
    return c.z * mix(vec3(1.0), rgb, c.y);
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = fragCoord / resolution.xy;
    vec2 p = (fragCoord - 0.5 * resolution.xy) / resolution.y;

    // Apply CC-mapped offsets — these respond to MIDI LFO modulation at CC+66
    p += vec2(x_offset, y_offset);

    // Frequency / scale — modulated by CC 1
    float n = fbm(p * max(frequency, 0.1));

    // Amplitude / brightness — modulated by CC 4
    n *= amplitude;
    n = clamp(n, 0.0, 1.0);

    // Color via hue + amplitude
    vec3 col = hsv2rgb(vec3(hue, 0.7, n + 0.3));

    fragColor = vec4(col, 1.0);
}