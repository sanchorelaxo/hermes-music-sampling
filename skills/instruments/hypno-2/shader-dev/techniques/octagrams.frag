// octagrams.frag — Hypno 2 single-pass SDF shape set
// Moving box SDFs with ray march accumulation. 64 steps. PI 5 SAFE.
// 5 CC params.
precision mediump float;

uniform vec2 resolution;
uniform float time;

uniform float speed;        // CC 0 — animation speed
uniform float scale;        // CC 1 — pattern scale
uniform float color_hue;    // CC 2 — palette hue shift
uniform float glow_amt;     // CC 3 — accumulation brightness
uniform float orbit_radius; // CC 4 — orbital motion radius

mat2 rot2(float a) { float c = cos(a), s = sin(a); return mat2(c, s, -s, c); }

float sdBox(vec3 p, vec3 b) {
    vec3 q = abs(p) - b;
    return length(max(q, 0.0)) + min(max(q.x, max(q.y, q.z)), 0.0);
}

float box(vec3 pos, float s) {
    pos *= s;
    float base = sdBox(pos, vec3(0.4, 0.4, 0.1)) / 1.5;
    pos.xy *= 5.0;
    pos.y -= 3.5;
    pos.xy *= rot2(0.75);
    return -base;
}

float boxSet(vec3 pos, float t) {
    vec3 origin = pos;
    pos.y += sin(t * speed * 0.4) * orbit_radius;
    pos.xy *= rot2(0.8);
    float box1 = box(pos, 2.0 - abs(sin(t * speed * 0.4)) * 1.5);

    pos = origin;
    pos.y -= sin(t * speed * 0.4) * orbit_radius;
    pos.xy *= rot2(0.8);
    float box2 = box(pos, 2.0 - abs(sin(t * speed * 0.4)) * 1.5);

    pos = origin;
    pos.x += sin(t * speed * 0.4) * orbit_radius;
    pos.xy *= rot2(0.8);
    float box3 = box(pos, 2.0 - abs(sin(t * speed * 0.4)) * 1.5);

    pos = origin;
    pos.x -= sin(t * speed * 0.4) * orbit_radius;
    pos.xy *= rot2(0.8);
    float box4 = box(pos, 2.0 - abs(sin(t * speed * 0.4)) * 1.5);

    pos = origin;
    pos.xy *= rot2(0.8);
    float box5 = box(pos, 0.5) * 6.0;

    pos = origin;
    float box6 = box(pos, 0.5) * 6.0;

    return max(max(max(max(max(box1, box2), box3), box4), box5), box6);
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

    vec3 ro  = vec3(0.0, -0.2, time * speed * 4.0);
    vec3 ray = normalize(vec3(uv2D, 1.5));
    ray.xy *= rot2(sin(time * speed * 0.03) * 5.0);
    ray.yz *= rot2(sin(time * speed * 0.05) * 0.2);

    float t  = 0.1;
    vec3 col = vec3(0.0);
    float ac = 0.0;

    for (int i = 0; i < 64; i++) {
        vec3 pos = ro + ray * t;
        pos = mod(pos - 2.0, 4.0) - 2.0;
        float gt = time - float(i) * 0.01;
        float d = boxSet(pos, gt);
        d = max(abs(d), 0.01);
        ac += exp(-d * 23.0);
        t += d * 0.55;
    }

    col  = vec3(ac * 0.02 * glow_amt);
    col += vec3(0.0, 0.2 * abs(sin(time * speed)), 0.5 + sin(time * speed) * 0.2);

    float hue = fract(color_hue + length(col) * 0.1 + time * speed * 0.05);
    float sat = 0.7;
    float val = clamp(length(col) * 2.0, 0.0, 1.0);
    col = hsv2rgb(vec3(hue, sat, val));

    gl_FragColor = vec4(col, 1.0 - t * 0.02);
}