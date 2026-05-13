// video-effect.frag — Hypno 2 video processing effect
// Post-processing style shader: takes video input and applies
// color grading, feedback-style ghosting, and edge detection.
// Designed to work with Hypno 2's video input passthrough.
// 5 CC parameters.

precision mediump float;

uniform vec2 resolution;
uniform float time;

uniform float color_shift;  // CC 0 — hue rotation
uniform float ghost_strength; // CC 1 — feedback ghost intensity
uniform float edge_amt;     // CC 2 — edge detection amount
uniform float contrast;     // CC 3 — contrast (center=1.0, range 0.5–3.0)
uniform float scanlines;    // CC 4 — CRT scanline strength

// ──────────── UTILITIES ────────────
vec3 hsv2rgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0/3.0, 1.0/3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

vec3 rgb2hsv(vec3 c) {
    vec4 K = vec4(0.0, -1.0/3.0, 2.0/3.0, -1.0);
    vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
    vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));
    float d = q.x - min(q.w, q.y);
    float e = 1.0e-10;
    return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
}

float sobel(vec2 p, float step) {
    vec4 s;
    s.x = length(gl_FragCoord.xy + vec2(-step,  step));
    s.y = length(gl_FragCoord.xy + vec2( 0.0,   step));
    s.z = length(gl_FragCoord.xy + vec2( step,  step));
    s.w = length(gl_FragCoord.xy + vec2(-step,   0.0));
    float r = length(gl_FragCoord.xy + vec2( step,   0.0));
    float bl = length(gl_FragCoord.xy + vec2(-step, -step));
    float b = length(gl_FragCoord.xy + vec2( 0.0,  -step));
    float br = length(gl_FragCoord.xy + vec2( step, -step));
    float gx = -s.x - 2.0*s.w - bl + s.z + 2.0*r + br;
    float gy = -s.x - 2.0*s.y - s.z + bl + 2.0*b + br;
    return sqrt(gx*gx + gy*gy);
}

void main() {
    vec2 uv = gl_FragCoord.xy / resolution;

    // NOTE: In the actual Hypno 2, replace the gradient below with your
    // video input texture sample. The Hypno 2 provides a texture sampler
    // named 'video' for video passthrough effects.
    //
    // vec3 src = texture2D(video, uv).rgb;
    //
    // Placeholder: procedural gradient for testing without video
    vec3 src = vec3(uv.x, uv.y, 0.5 + 0.5 * sin(time));

    vec3 col = src;

    // 1. Contrast
    col = (col - 0.5) * contrast + 0.5;

    // 2. Color shift (rotate hue)
    vec3 hsv = rgb2hsv(col);
    hsv.x = fract(hsv.x + color_shift);
    hsv.y = clamp(hsv.y * 1.2, 0.0, 1.0);
    col = hsv2rgb(hsv);

    // 3. Edge detection (Sobel operator)
    float edge = sobel(uv, 2.0 / resolution.y);
    float edge_mask = smoothstep(0.1, 0.3, edge);
    // Glow edges in cyan-magenta
    vec3 edge_color = mix(vec3(0.0, 1.0, 1.0), vec3(1.0, 0.0, 1.0),
                          sin(edge * 10.0 + time) * 0.5 + 0.5);
    col = mix(col, col + edge_color * 0.3, edge_mask * edge_amt);

    // 4. Feedback ghost (fake temporal blur with pixel offset)
    vec2 ghost_uv = uv + vec2(sin(uv.y * 20.0 + time) * ghost_strength * 0.02,
                              cos(uv.x * 20.0 + time) * ghost_strength * 0.02);
    // Mix with "previous frame" approximation — offset sample
    vec3 ghost = vec3(ghost_uv.x, ghost_uv.y,
                      0.5 + 0.5 * sin(time * 1.37));
    col = mix(col, ghost * 0.6, ghost_strength * 0.5);

    // 5. CRT scanlines
    float scan = sin(uv.y * resolution.y * 2.0) * 0.5 + 0.5;
    scan = mix(1.0, 0.7 + scan * 0.3, scanlines);
    col *= scan;

    // Vignette
    vec2 v = uv - 0.5;
    float vignette = 1.0 - dot(v, v) * 0.5;
    col *= vignette;

    gl_FragColor = vec4(col, 1.0);
}
