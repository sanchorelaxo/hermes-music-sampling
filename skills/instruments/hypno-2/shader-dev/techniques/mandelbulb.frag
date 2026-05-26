// mandelbulb.frag — Hypno 2 single-pass 3D fractal
// Mandelbulb with soft shadow. 48 steps.
// PI 5: use low fractal_power (CC4, try 4-6).
// 5 CC params.
#include "ShapeUtil.frag"

uniform float speed;         // CC 0 — animation speed
uniform float brightness;    // CC 1 — overall brightness
uniform float color_phase;   // CC 2 — palette hue phase
uniform float shadow_k;      // CC 3 — soft shadow hardness (10=sharp, 50=diffuse)
uniform float fractal_power; // CC 4 — Mandelbulb power (8=classic, 4-6 for PI 5)

void ry(inout vec3 p, float a) {
    float c = cos(a), s = sin(a);
    p.xz = mat2(c, s, -s, c) * p.xz;
}

vec3 mb(vec3 p) {
    p.xzy;
    vec3 z = p;
    float power = fractal_power;
    float r, theta, phi;
    float dr = 1.0;
    float t0 = 1.0;

    for (int i = 0; i < 6; i++) {
        r = length(z);
        if (r > 2.0) continue;
        theta = atan(z.y, z.x);
        phi   = asin(z.z / r) + time * speed * 0.1;
        dr    = pow(r, power - 1.0) * dr * power + 1.0;
        r     = pow(r, power);
        theta *= power;
        phi   *= power;
        z = r * vec3(cos(theta) * cos(phi), sin(theta) * cos(phi), sin(phi)) + p;
        t0 = min(t0, r);
    }
    return vec3(0.5 * log(r) * r / dr, t0, 0.0);
}

vec3 f(vec3 p) { ry(p, time * speed * 0.2); return mb(p); }

float softshadow(vec3 ro, vec3 rd, float k) {
    float res = 1.0;
    float t   = 0.01;
    for (int i = 0; i < 40; i++) {
        float h = f(ro + rd * t).x;
        if (h < 0.001) return 0.02;
        res = min(res, k * h / t);
        t  += clamp(h, 0.01, 2.0);
    }
    return clamp(res, 0.0, 1.0);
}

vec3 nor(vec3 pos) {
    vec3 eps = vec3(0.001, 0.0, 0.0);
    return normalize(vec3(
        f(pos + eps.xyy).x - f(pos - eps.xyy).x,
        f(pos + eps.yxy).x - f(pos - eps.yxy).x,
        f(pos + eps.yyx).x - f(pos - eps.yyx).x
    ));
}

vec3 hsv2rgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0/3.0, 1.0/3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

void main(void) {
    vec2 uv = tcoord - 0.5;
    uv.x *= resolution.x / resolution.y;

    float stime = stime = 0.7 + 0.3 * sin(time * speed * 0.4);
    float ctime = 0.7 + 0.3 * cos(time * speed * 0.4);
    vec3 ta = vec3(0.0);
    vec3 ro = vec3(0.0, 3.0 * stime * ctime, 3.0 * (1.0 - stime * ctime));
    vec3 cf = normalize(ta - ro);
    vec3 cs = normalize(cross(cf, vec3(0.0, 1.0, 0.0)));
    vec3 cu = normalize(cross(cs, cf));
    vec3 rd = normalize(uv.x * cs + uv.y * cu + 3.0 * cf);

    vec3 sundir   = normalize(vec3(0.1, 0.8, 0.6));
    vec3 sun      = vec3(1.64, 1.27, 0.99);
    vec3 skycolor = vec3(0.6, 1.5, 1.0);
    vec3 bg       = exp(uv.y - 2.0) * vec3(0.4, 1.6, 1.0);

    float halo = clamp(dot(normalize(-ro), rd), 0.0, 1.0);
    vec3 col  = bg + vec3(1.0, 0.8, 0.4) * pow(halo, 17.0);

    float t      = 0.0;
    float res_t  = 0.0;
    float res_d  = 1000.0;
    float max_error = -1.0;
    float d      = 1.0;
    float pd     = 100.0;
    float os     = 0.0;
    float step_sz = 0.0;
    float error  = 1000.0;

    for (int i = 0; i < 48; i++) {
        if (error < (1.0 / (resolution.x * 3.0)) * 0.5 || t > 20.0) { }
        else {
            vec3 c = f(ro + rd * t倾);
            d = c.x;
            if (d > os) {
                os = 0.4 * d * d / pd;
                step_sz = d + os;
                pd = d;
            } else {
                step_sz = -os;
                os = 0.0;
                pd = 100.0;
                d = 1.0;
            }
            error = d / t;
            if (error < max_error || max_error < 0.0) {
                max_error = error;
                res_t = t;
                res_d = d;
            }
            t += step_sz;
        }
    }

    if (res_t > 0.0 && res_t < 20.0) {
        vec3 p = ro + res_t * rd;
        vec3 n = nor(p);
        float shadow = softshadow(p, sundir, shadow_k);
        float dif  = max(0.0, dot(n, sundir));
        float sky  = 0.6 + 0.4 * max(0.0, dot(n, vec3(0.0, 1.0, 0.0)));
        float bac  = max(0.3 + 0.7 * dot(vec3(-sundir.x, -1.0, -sundir.z), n), 0.0);
        float spe  = max(0.0, pow(clamp(dot(sundir, reflect(rd, n)), 0.0, 1.0), 10.0));

        vec3 lin = 4.5 * sun * dif * shadow;
        lin += 0.8 * bac * sun;
        lin += 0.6 * sky * skycolor * shadow;
        lin += 3.0 * spe * shadow;

        float t0 = pow(clamp(res_d, 0.0, 1.0), 0.55);
        vec3 tc0 = 0.5 + 0.5 * sin(3.0 + 4.2 * t0 + vec3(0.0, 0.5, 1.0) + color_phase);
        col = lin * vec3(0.9, 0.8, 0.6) * 0.2 * tc0;
        col = mix(col, bg, 1.0 - exp(-0.001 * res_t * res_t));
    }

    col = pow(clamp(col, 0.0, 1.0), vec3(0.45));
    col = col * 0.6 + 0.4 * col * col * (3.0 - 2.0 * col);
    col = mix(col, vec3(dot(col, vec3(0.33))), -0.5);
    col *= 0.5 + 0.5 * pow(16.0 * tcoord.x * tcoord.y * (1.0 - tcoord.x) * (1.0 - tcoord.y), 0.7);

    gl_FragColor = vec4(col * brightness, 1.0);
}
