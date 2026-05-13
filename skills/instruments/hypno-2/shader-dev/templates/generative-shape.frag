// generative-shape.frag — Hypno 2 SDF shape visuals
// Uses 2D signed distance functions to draw clean anti-aliased geometry
// with voronoi noise and animated rotation. 5 CC parameters.

precision mediump float;

uniform vec2 resolution;
uniform float time;

uniform float shape_type;   // CC 0 — 0=circle 0.5=box 1=ring
uniform float count;        // CC 1 — number of shapes (1–20)
uniform float size;         // CC 2 — shape size
uniform float rotation;     // CC 3 — rotation speed
uniform float noise_amt;    // CC 4 — noise distortion amount

// ──────────── UTILITIES ────────────
float hash(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}

float valueNoise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x),
               mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
}

vec3 hsv2rgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0/3.0, 1.0/3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

// SDF: circle
float sdCircle(vec2 p, float r) { return length(p) - r; }

// SDF: box
float sdBox(vec2 p, vec2 b) {
    vec2 d = abs(p) - b;
    return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0);
}

// SDF: ring
float sdRing(vec2 p, float outer, float inner) {
    return abs(length(p) - (outer + inner) * 0.5) - (outer - inner) * 0.5;
}

void main() {
    vec2 uv = gl_FragCoord.xy / resolution;
    vec2 p = (gl_FragCoord.xy - 0.5 * resolution) / resolution.y;

    vec3 col = vec3(0.0);

    // Grid of shapes
    int n = int(count * 19.0) + 1;

    for (int i = 0; i < 20; i++) {
        if (i >= n) break;

        // Grid position with noise jitter
        float fi = float(i);
        vec2 cell = vec2(mod(fi, 5.0) - 2.0, floor(fi / 5.0) - 2.0);
        vec2 jitter = vec2(valueNoise(cell * 3.0 + time * 0.2),
                          valueNoise(cell * 3.0 + 5.0 + time * 0.2));

        vec2 center = cell * 0.4 + jitter * noise_amt * 0.4;
        vec2 pp = p - center;

        // Rotation
        float angle = time * rotation * (1.0 + hash(cell) * 0.5);
        mat2 rot = mat2(cos(angle), -sin(angle), sin(angle), cos(angle));
        pp = rot * pp;

        // Shape distance
        float d;
        if (shape_type < 0.33) {
            d = sdCircle(pp, size * 0.15);
        } else if (shape_type < 0.66) {
            d = sdBox(pp, vec2(size * 0.15));
        } else {
            d = sdRing(pp, size * 0.15, size * 0.08);
        }

        // Anti-aliased fill
        float aa = 3.0 / resolution.y;
        float mask = 1.0 - smoothstep(-aa, aa, d);

        // Color from cell position and time
        float hue = fract(hash(cell) + time * 0.1);
        vec3 shapeCol = hsv2rgb(vec3(hue, 0.7, mask));

        // Composite with screen blend
        col = col + shapeCol * (1.0 - length(col) * 0.5);
    }

    gl_FragColor = vec4(col, 1.0);
}
