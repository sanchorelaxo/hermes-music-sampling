// audio-reactive.frag — Hypno 2 audio-reactive visuals
// Processes Hypno 2 audio analysis uniforms to drive visual effects.
// The Hypno 2 exposes audio data via additional built-in uniforms.
//
// Built-in audio uniforms (no CC slot consumed):
//   uniform float bass;        // low frequency energy 0–1
//   uniform float mid;         // mid frequency energy 0–1
//   uniform float treble;      // high frequency energy 0–1
//   uniform float volume;      // overall amplitude 0–1
//
// Custom audio-reactive parameters use CC slots.
// 5 CC parameters + 4 free audio uniforms.
//
// Known limitation: audio uniforms may be named differently
// on your Hypno 2 firmware version. Check the web UI uniform list
// and rename accordingly (e.g., 'bass' → 'low', 'volume' → 'amp').

precision mediump float;

uniform vec2 resolution;
uniform float time;

// Audio uniforms (free — provided by Hypno 2)
uniform float bass;          // 0–1 low frequency
uniform float mid;           // 0–1 mid frequency
uniform float treble;        // 0–1 high frequency
uniform float volume;        // 0–1 overall amplitude

// Custom CC parameters
uniform float symmetry;       // CC 0 — kaleidoscope segments
uniform float zoom;           // CC 1 — audio-reactive zoom sensitivity
uniform float color_speed;    // CC 2 — palette cycling speed
uniform float bass_warp;      // CC 3 — how much bass warps geometry
uniform float treble_spark;   // CC 4 — high-frequency sparkle intensity

// ──────────── UTILITIES ────────────
float hash(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}

float fbm(vec2 p) {
    float v = 0.0, a = 0.5;
    for (int i = 0; i < 4; i++) {
        v += a * hash(p);
        p *= 2.0;
        a *= 0.5;
    }
    return v;
}

vec3 palette(float t) {
    return 0.5 + 0.5 * cos(6.28318 * (t + vec3(0.0, 0.33, 0.67)));
}

void main() {
    vec2 uv = gl_FragCoord.xy / resolution;
    vec2 p = (gl_FragCoord.xy - 0.5 * resolution) / resolution.y;

    // ── Kaleidoscope (symmetry) ──
    // Convert to polar, mirror angle
    float angle = atan(p.y, p.x);
    float radius = length(p);
    float seg_angle = 6.28318 / (symmetry * 7.0 + 1.0);
    angle = mod(angle, seg_angle) - seg_angle * 0.5;
    p = vec2(cos(angle), sin(angle)) * radius;

    // ── Audio-reactive zoom ──
    float zoom_factor = 1.0 + (bass + volume * 0.5) * zoom * 4.0;
    p *= zoom_factor;

    // ── Audio-reactive warping ──
    float warp = (bass * bass_warp * 3.0 + mid * 0.3);
    p.x += sin(p.y * 4.0 + time * 0.5) * warp * 0.3;
    p.y += cos(p.x * 4.0 + time * 0.4) * warp * 0.3;

    // ── FBM noise field ──
    float noise = fbm(p * 3.0 + time * 0.1 * (1.0 + volume));

    // ── Color from noise + audio ──
    float hue = noise +
                time * color_speed * 0.05 +
                bass * 0.2 +
                treble * 0.1;
    vec3 col = palette(hue);

    // ── Treble sparkles ──
    // High-frequency audio creates bright dots
    float spark = treble * treble_spark * 3.0;
    float dots = hash(floor(p * (20.0 + treble * 40.0)));
    float dot_mask = smoothstep(0.95, 1.0, dots) * spark;
    col += vec3(1.0) * dot_mask;

    // ── Bass pulse brightness ──
    col *= 0.5 + bass * 0.5 + 0.3;
    col *= 0.6 + volume * 0.4;

    // ── Vignette ──
    vec2 v = uv - 0.5;
    float vignette = 1.0 - dot(v, v) * 0.6;
    col *= vignette;

    gl_FragColor = vec4(col, 1.0);
}
