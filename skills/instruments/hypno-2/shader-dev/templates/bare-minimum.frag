// bare-minimum.frag — Hypno 2 minimal template
// Copy this to start a new shader. The Hypno 2 web UI will detect
// uniform names and create labeled CC sliders automatically.

precision mediump float;

// Built-in uniforms (provided by Hypno 2, no CC slot consumed)
uniform vec2 resolution;   // canvas width, height
uniform float time;        // seconds since shader load

// Custom uniforms (max 5 — each uses one CC slot)
uniform float speed;       // CC 0 — animation speed
uniform float scale;       // CC 1 — pattern zoom
uniform float param2;      // CC 2 — generic parameter
uniform float param3;      // CC 3 — generic parameter
uniform float param4;      // CC 4 — generic parameter

// ──────────── GLSL utility functions ────────────

// Hash function (deterministic pseudo-random)
float hash(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}

// HSV to RGB (hue 0-1)
vec3 hsv2rgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

void main() {
    // Normalized UV (0..1)
    vec2 uv = gl_FragCoord.xy / resolution;

    // Centered coordinate (-1..1, aspect-corrected)
    vec2 p = (gl_FragCoord.xy - 0.5 * resolution) / resolution.y;

    // ──────────── YOUR SHADER CODE ────────────

    // Simple gradient + pulse
    float pulse = 1.0 + sin(time * speed * 0.5) * 0.3;
    p *= scale * pulse;

    float r = length(p);
    float hue = fract(r * 2.0 + time * speed * 0.1);

    vec3 col = hsv2rgb(vec3(hue, 0.8, 1.0 - r * 0.5));

    // ──────────── OUTPUT ────────────
    gl_FragColor = vec4(col, 1.0);
}
