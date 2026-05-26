// smaller-waterfall.frag — Hypno 2 single-pass generative
// 3-layer concentric ring accumulation. 5 CC params. PI 5 SAFE.
precision mediump float;

uniform vec2 resolution;
uniform float time;

uniform float speed;         // CC 0 — animation speed
uniform float ring_density;  // CC 1 — ring frequency
uniform float color_phase;   // CC 2 — palette hue offset
uniform float brightness;    // CC 3 — output brightness
uniform float saturation;     // CC 4 — color saturation

vec3 hsv2rgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0/3.0, 1.0/3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

void main() {
    vec2 uv = gl_FragCoord.xy / resolution;
    vec2 p  = (gl_FragCoord.xy - 0.5 * resolution) / resolution.y;

    float z = time * speed * 0.1 + 0.9;

    vec3 c = vec3(0.0);
    for (int i = 0; i < 3; i++) {
        float fi = float(i);
        vec2 uvp = uv + p / (length(p) + 0.01)
                   * (sin(z * (1.0 + fi * 0.3)) + 1.0)
                   * abs(sin(length(p) * ring_density * 9.0 - z - z));
        c[i] = 0.01 / length(mod(uvp, 1.0) - 0.5);
    }
    c /= (length(p) + 0.01);

    float hue = fract(c.r * 0.5 + time * speed * 0.08 + color_phase);
    float sat  = clamp(saturation, 0.3, 1.0);
    float val  = clamp(brightness * (0.3 + c.r * 0.7), 0.0, 1.0);
    vec3 col   = hsv2rgb(vec3(hue, sat, val));

    gl_FragColor = vec4(col, 1.0);
}