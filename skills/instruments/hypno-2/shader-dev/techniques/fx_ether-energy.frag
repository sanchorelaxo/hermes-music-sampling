// ether-energy.frag — Hypno 2 port of CodePen "The Birth of Energy from the Ether"
// by sabosugi (https://codepen.io/sabosugi/pen/WbGqrKy)
//
// Original: Raymarching with space twisting (99 iterations, too heavy for Pi 5)
// Port: Domain-warping with FBM (Pi 5 friendly, single-pass)
//
// Adaptation strategy:
//   - Raymarching → triple FBM warp (similar organic complexity)
//   - Space twist with cos/rotation → polar coords + animated domain warp
//   - Fractal sin() loop → animated FBM layers
//   - Cosine palette with offsets → palette with CC-controllable phase
//   - Film grain → hash-based noise overlay (cheap)
//
// Hypno 2 constraints: 5 uniforms max, single-pass, Pi 5 GPU

precision mediump float;

// Built-in uniforms
uniform vec2 resolution;
uniform float time;

// Custom uniforms (5 max — CC 0–4)
uniform float speed;        // CC 0 — animation speed (flight speed in original)
uniform float warp_scale;  // CC 1 — spatial scale
uniform float intensity;   // CC 2 — light intensity / contrast
uniform float color_r;      // CC 3 — red color offset (default 4.2)
uniform float color_g;      // CC 4 — green color offset (default -1.6)
// NOTE: blue offset (5.4) fixed to avoid consuming 6th uniform

// ──────────── Hash (sin-free, Pi 5 stable) ────────────

float hash12(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

// ──────────── Value Noise ────────────

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    return mix(
        mix(hash12(i), hash12(i + vec2(1.0, 0.0)), f.x),
        mix(hash12(i + vec2(0.0, 1.0)), hash12(i + vec2(1.0, 1.0)), f.x),
        f.y
    );
}

// ──────────── FBM (4 octaves — Pi 5 friendly) ────────────

const mat2 mtx = mat2(0.80, 0.60, -0.60, 0.80);

float fbm(vec2 p) {
    float f = 0.0;
    f += 0.500000 * noise(p); p = mtx * p * 2.02;
    f += 0.250000 * noise(p); p = mtx * p * 2.03;
    f += 0.125000 * noise(p); p = mtx * p * 2.01;
    f += 0.062500 * noise(p);
    return f / 0.9375;
}

// ──────────── Cosine Palette (from original color logic) ────────────
// Original: palette = cos(structuralVal + vec4(uColorOffset, 0.0)) + 1.2
// Port: a=1.2, b=1.0, c=1.0, d = color offsets passed as uniforms

vec3 palette(float t, float r, float g) {
    vec3 a = vec3(1.2);  // brightness offset (was +1.2 in original)
    vec3 b = vec3(1.0);  // amplitude
    vec3 c = vec3(1.0);  // frequency
    vec3 d = vec3(r, g, 5.4);  // phase offsets (r/g from CC, blue fixed)
    return a + b * cos(6.28318 * (c * t + d));
}

// ──────────── Main ────────────

void main() {
    // Normalized coordinates
    vec2 uv = gl_FragCoord.xy / resolution;
    vec2 p = (gl_FragCoord.xy - 0.5 * resolution) / resolution.y;

    // Scale (warp_density equivalent)
    p *= warp_scale;

    // Animate — time drives all motion layers
    float t = time * speed;

    // ─── Domain Warp (port of original's space twisting + fractal sin loop) ───
    // Original: twistedSpace += sin(twistedSpace * scale + tAnim).yzx / scale;
    //          scale started at 8.3, added 13.3 each iteration (8 total iterations)
    // Port: triple FBM warp — each layer adds sin-like oscillation via noise

    // First warp layer (slow drift — equivalent to original's totalDist rotation)
    vec2 q = vec2(
        fbm(p + t * 0.08),
        fbm(p + t * 0.05 + vec2(6.3, 2.8))
    );

    // Second warp layer (medium distortion)
    vec2 r = vec2(
        fbm(p + q * 1.2 + t * 0.12 + vec2(1.7, 9.2)),
        fbm(p + q * 1.2 + t * 0.09 + vec2(4.2, 3.1))
    );

    // Third warp layer (fine detail — 8 original iterations collapsed to 3)
    float n = fbm(p + r * 0.9 + t * 0.15);

    // ─── Color Accumulation (port of original's palette + light accumulation) ───
    // Original: accumulatedLight += (palette / max(stepDist, 0.01)) * totalDist;
    // Port: palette applied to pattern value, scaled by intensity

    vec3 col = palette(n, color_r, color_g) * intensity;

    // ─── Film Grain (from original's grain overlay) ────────────
    // Original: grain = hash13(vec3(absolute pixel coords));
    //          gl_FragColor.rgb += (grain - 1.1) * uGrainAmount;
    // uGrainAmount default was 0.0, so grain is off by default.
    // Enable via intensity micro-variation if desired (cheap):
    // float grain = hash12(gl_FragCoord.xy) * 0.02;
    // col += (grain - 0.5) * 0.0;  // set multiplier to enable

    // Output
    gl_FragColor = vec4(col, 1.0);
}