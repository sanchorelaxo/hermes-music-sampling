// fractal-pyramid.frag — Hypno 2 single-pass ray marched
// 3D folding fractal (Sierpinski-like). 64 steps. PI 5 SAFE.
// 5 CC params.
precision mediump float;

uniform vec2 resolution;
uniform float time;

uniform float speed;         // CC 0 — fractal rotation speed
uniform float brightness;    // CC 1 — overall brightness
uniform float color_phase;   // CC 2 — palette hue offset
uniform float camera_dist;   // CC 3 — camera orbit distance
uniform float fractal_scale; // CC 4 — fractal detail scale

mat2 rot(float a) { float c = cos(a), s = sin(a); return mat2(c, s, -s, c); }

vec3 palette(float d) {
    return mix(vec3(0.2, 0.7, 0.9), vec3(1.0, 0.0, 1.0), d);
}

float map(vec3 p) {
    for (int i = 0; i < 8; i++) {
        float t = time * speed * 0.2;
        p.xz = rot(t) * p.xz;
        p.xy = rot(t * 1.89) * p.xy;
        p.xz = abs(p.xz) - 0.5;
    }
    return dot(sign(p), p) / 5.0;
}

vec4 rm(vec3 ro, vec3 rd) {
    float t = 0.0;
    vec3 col = vec3(0.0);
    float d;
    for (int i = 0; i < 64; i++) {
        vec3 pp = ro + rd * t;
        d = map(pp) * 0.5;
        if (d < 0.02) break;
        if (d > 100.0) break;
        col += palette(length(pp) * fractal_scale) / (400.0 * d);
        t += d;
    }
    return vec4(col, 1.0 / (d * 100.0));
}

vec3 hsv2rgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0/3.0, 1.0/3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

void main() {
    vec2 uv = gl_FragCoord.xy;
    vec2 uv2D = (uv - 0.5 * resolution) / resolution.y;
    uv2D.x *= resolution.x / resolution.y;

    vec3 ro = vec3(0.0, 0.0, -camera_dist);
    ro.xz = rot(time * speed) * ro.xz;
    vec3 cf = normalize(-ro);
    vec3 cs = normalize(cross(cf, vec3(0.0, 1.0, 0.0)));
    vec3 cu = normalize(cross(cf, cs));

    vec3 uuv = ro + cf * 3.0 + uv2D.x * cs + uv2D.y * cu;
    vec3 rd  = normalize(uuv - ro);

    vec4 col = rm(ro, rd);
    col.rgb = clamp(col.rgb * brightness, 0.0, 1.0);

    float hue = fract(color_phase + col.a * 0.5 + time * speed * 0.05);
    float sat = 0.8;
    float val = clamp(col.r * 2.5, 0.0, 1.0);
    col.rgb = hsv2rgb(vec3(hue, sat, val));

    gl_FragColor = vec4(col.rgb, 1.0);
}