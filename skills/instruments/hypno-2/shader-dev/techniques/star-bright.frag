// star-bright.frag — Hypno 2 single-pass generative
// 2D radial glow with palette coloring. 5 CC params. PI 5 SAFE.
precision mediump float;

uniform vec2 resolution;
uniform float time;

uniform float speed;        // CC 0 — animation speed
uniform float glow_amt;     // CC 1 — radial glow intensity
uniform float color_phase;  // CC 2 — palette hue shift
uniform float brightness;   // CC 3 — overall brightness
uniform float ring_freq;    // CC 4 — ring frequency

vec3 hsv2rgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0/3.0, 1.0/3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

void main() {
    vec2 uv = gl_FragCoord.xy / resolution;
    vec2 p = (gl_FragCoord.xy - 0.5 * resolution) / resolution.y;
    p *= 2.0;

    float l = length(p);
    float z = time * speed;

    vec3 c = vec3(0.0);
    for (int i = 0; i < 3; i++) {
        float fi = float(i);
        vec2 uvp = p / (l + 0.01);
        uvp -= 0.5;
        uvp += p / l * (sin(z) + 1.0) * abs(sin(l * ring_freq - z - z));
        c[i] = glow_amt / length(mod(uvp, 1.0) - 0.5);
    }
    c /= l;

    float hue = fract(l * 0.3 + time * speed * 0.1 + color_phase);
    float sat  = 0.8;
    float val  = brightness * (0.5 + 0.5 * c.r);
    vec3 col   = hsv2rgb(vec3(hue, sat, val));

    gl_FragColor = vec4(col, 1.0);
}