// phantom-star.frag — Hypno 2 single-pass iterative SDF
// IFS box fractal with accumulation glow. 64 steps. PI 5 SAFE.
// 5 CC params.
precision mediump float;

uniform vec2 resolution;
uniform float time;

uniform float speed;       // CC 0 — rotation speed
uniform float glow_amt;    // CC 1 — accumulation brightness
uniform float grid_scale;  // CC 2 — IFS grid repetition scale
uniform float brightness;  // CC 3 — overall brightness
uniform float color_hue;   // CC 4 — hue offset

mat2 rot(float a) {
    float c = cos(a), s = sin(a);
    return mat2(c, s, -s, c);
}

const float PI  = 3.141592654;
const float PI2 = PI * 2.0;

vec2 pmod(vec2 p, float r) {
    float a = atan(p.x, p.y) + PI / r;
    float n = PI2 / r;
    a = floor(a / n) * n;
    return p * rot(-a);
}

float sdBox(vec3 p, vec3 b) {
    vec3 d = abs(p) - b;
    return min(max(d.x, max(d.y, d.z)), 0.0) + length(max(d, 0.0));
}

float ifsBox(vec3 p) {
    for (int i = 0; i < 5; i++) {
        p = abs(p) - 1.0;
        p.xy *= rot(time * speed * 0.3);
        p.xz *= rot(time * speed * 0.1);
    }
    p.xz *= rot(time * speed);
    return sdBox(p, vec3(0.4, 0.8, 0.3));
}

float map(vec3 p) {
    vec3 q = p;
    q.x = mod(q.x - 5.0 * grid_scale, 10.0 * grid_scale) - 5.0 * grid_scale;
    q.y = mod(q.y - 5.0 * grid_scale, 10.0 * grid_scale) - 5.0 * grid_scale;
    q.z = mod(q.z, 16.0) - 8.0;
    q.xy = pmod(q.xy, 5.0);
    return ifsBox(q);
}

vec3 hsv2rgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0/3.0, 1.0/3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

void main() {
    vec2 uv = gl_FragCoord.xy;
    vec2 uv2D = (uv - 0.5 * resolution) / resolution.y;
    float dRes = min(resolution.x, resolution.y);
    uv2D *= 2.0 / dRes;

    vec3 cPos  = vec3(0.0, 0.0, -3.0 * time * speed);
    vec3 cDir  = normalize(vec3(0.0, 0.0, -1.0));
    vec3 cUp   = vec3(sin(time * speed * 0.3), 1.0, 0.0);
    vec3 cSide = cross(cDir, cUp);
    vec3 ray   = normalize(cSide * uv2D.x + cUp * uv2D.y + cDir);

    float acc  = 0.0;
    float acc2 = 0.0;
    float t    = 0.0;

    for (int i = 0; i < 64; i++) {
        vec3 pos   = cPos + ray * t;
        float dist = map(pos);
        dist = max(abs(dist), 0.02);
        float a = exp(-dist * 3.0);
        float inPhantom = step(0.5, fract(length(pos) * 0.1 + time * speed * 0.5))
                        * step(0.0, mod(length(pos) + 24.0 * time * speed, 30.0) - 3.0);
        if (inPhantom > 0.5) { a *= 2.0; acc2 += a; }
        acc += a;
        t += dist * 0.5;
    }

    acc2 *= glow_amt * 0.002;
    acc  *= glow_amt * 0.01;

    float hue = fract(color_hue + acc * 0.05 + time * speed * 0.1);
    float val = clamp(acc * 3.0, 0.0, 1.0) * brightness;
    vec3 col  = hsv2rgb(vec3(hue, 0.8, val));
    col += vec3(0.0, 0.01 * acc2, 0.02 * acc2);

    gl_FragColor = vec4(col, 1.0 - t * 0.02);
}