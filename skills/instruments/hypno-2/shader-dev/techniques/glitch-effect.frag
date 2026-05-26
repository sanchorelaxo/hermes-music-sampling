// glitch-effect.frag — Hypno 2 glitch / datamosh / CRT effects
// Edge detection + difference blend + scanline distortion
// Technique: edge-detection + blend-modes
// 5 CC parameters.

precision mediump float;

uniform vec2 resolution;
uniform float time;

uniform float edge_amt;     // CC 0 — edge detection intensity (0=none, 1.0=full)
uniform float glitch_strength; // CC 1 — UV offset for glitch (0=none, 0.1=extreme)
uniform float scanlines;    // CC 2 — CRT scanline overlay (0=none, 1.0=heavy)
uniform float palette_sel;  // CC 3 — palette phase (0.0=rainbow, 1.0=pastel)
uniform float speed;        // CC 4 — animation speed (0=frozen, 1.0=full)

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

// ──────────── SOBEL EDGE DETECTION ────────────
float sobel(vec2 p, float step) {
    float tl = fbm(p + vec2(-step,  step));
    float t  = fbm(p + vec2( 0.0,   step));
    float tr = fbm(p + vec2( step,  step));
    float l  = fbm(p + vec2(-step,   0.0));
    float r  = fbm(p + vec2( step,   0.0));
    float bl = fbm(p + vec2(-step, -step));
    float b  = fbm(p + vec2( 0.0,  -step));
    float br = fbm(p + vec2( step, -step));
    float gx = -tl - 2.0 * l - bl + tr + 2.0 * r + br;
    float gy = -tl - 2.0 * t - tr + bl + 2.0 * b + br;
    return sqrt(gx * gx + gy * gy);
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
    vec2 p = uv * 4.0;
    p += vec2(time * speed * 0.1, time * speed * 0.07);

    // Base pattern
    float n = fbm(p);

    // Glitch: offset copy of pattern → difference
    float offsetAmt = glitch_strength;
    float nOffset = fbm(p + vec2(sin(time * 2.0) * offsetAmt, 0.0));
    float diff = abs(n - nOffset);

    // Edge detection from base pattern
    float edge = sobel(uv, 2.0 / resolution.y);

    // Combine glitch artifacts with edge detection
    float glitch = max(diff, edge * 0.5);

    // Colorize base, overlay glitch in magenta/cyan
    vec3 baseCol = palette(n + time * speed * 0.05, palette_sel);
    vec3 glitchCol = mix(vec3(0.0, 1.0, 1.0), vec3(1.0, 0.0, 1.0),
                        sin(glitch * 10.0 + time) * 0.5 + 0.5);
    vec3 col = mix(baseCol, glitchCol, smoothstep(0.05, 0.3, glitch) * edge_amt);

    // CRT scanlines
    float scan = sin(uv.y * resolution.y * 2.0) * 0.5 + 0.5;
    scan = mix(1.0, 0.7 + scan * 0.3, scanlines);
    col *= scan;

    fragColor = vec4(col, 1.0);
}