// radar1.frag — Hypno 2 single-pass generative
// Sci-fi radar: concentric circles, rotating sweep, animated blips.
// 5 CC params. PI 5 SAFE — pure 2D procedural.
precision mediump float;

uniform vec2 resolution;
uniform float time;

uniform float sweep_speed;   // CC 0 — sweep arm rotation speed
uniform float sweep_width;   // CC 1 — sweep glow width
uniform float blip_activity; // CC 2 — random blip frequency
uniform float tri_size;      // CC 3 — corner triangle scale
uniform float color_temp;    // CC 4 — warm→cool color shift

#define SMOOTH(r,R) (1.0 - smoothstep(R - 1.0, R + 1.0, r))
#define RS(a,b,x) (smoothstep(a - 1.0, a + 1.0, x) * (1.0 - smoothstep(b - 1.0, b + 1.0, x)))
#define M_PI 3.141592654

const vec3 blue1 = vec3(0.74, 0.95, 1.00);
const vec3 blue2 = vec3(0.87, 0.98, 1.00);
const vec3 blue3 = vec3(0.35, 0.76, 0.83);
const vec3 blue4 = vec3(0.953, 0.969, 0.89);
const vec3 red   = vec3(1.00, 0.38, 0.227);

float movingLine(vec2 uv, vec2 center, float radius) {
    float theta0 = 90.0 * time * sweep_speed;
    vec2 d = uv - center;
    float r = length(d);
    if (r < radius) {
        vec2 p = radius * vec2(cos(theta0 * M_PI / 180.0), -sin(theta0 * M_PI / 180.0));
        float l = length(d - p * clamp(dot(d, p) / dot(p, p), 0.0, 1.0));
        d = normalize(d);
        float theta = mod(180.0 * atan(d.y, d.x) / M_PI + theta0, 360.0);
        float gradient = clamp(1.0 - theta / 90.0, 0.0, 1.0);
        return SMOOTH(l, 1.0) + 0.5 * gradient;
    }
    return 0.0;
}

float circle(vec2 uv, vec2 center, float radius, float width) {
    float r = length(uv - center);
    return SMOOTH(r - width / 2.0, radius) - SMOOTH(r + width / 2.0, radius);
}

float circle2(vec2 uv, vec2 center, float radius, float width, float opening) {
    vec2 d = uv - center;
    float r = length(d);
    d = normalize(d);
    if (abs(d.y) > opening) return SMOOTH(r - width / 2.0, radius) - SMOOTH(r + width / 2.0, radius);
    return 0.0;
}

float circle3(vec2 uv, vec2 center, float radius, float width) {
    vec2 d = uv - center;
    float r = length(d);
    d = normalize(d);
    float theta = 180.0 * (atan(d.y, d.x) / M_PI);
    return smoothstep(2.0, 2.1, abs(mod(theta + 2.0, 45.0) - 2.0)) *
        mix(0.5, 1.0, step(45.0, abs(mod(theta, 180.0) - 90.0))) *
        (SMOOTH(r - width / 2.0, radius) - SMOOTH(r + width / 2.0, radius));
}

float triangles(vec2 uv, vec2 center, float radius) {
    vec2 d = uv - center;
    float s = tri_size;
    return RS(-8.0 * s, 0.0, d.x - radius)   * (1.0 - smoothstep(7.0 + d.x - radius,  9.0 + d.x - radius,  abs(d.y))) +
           RS( 0.0, 8.0 * s, d.x + radius)   * (1.0 - smoothstep(7.0 - d.x - radius,  9.0 - d.x - radius,  abs(d.y))) +
           RS(-8.0 * s, 0.0, d.y - radius)   * (1.0 - smoothstep(7.0 + d.y - radius,  9.0 + d.y - radius,  abs(d.x))) +
           RS( 0.0, 8.0 * s, d.y + radius)   * (1.0 - smoothstep(7.0 - d.y - radius,  9.0 - d.y - radius,  abs(d.x)));
}

float dots(vec2 uv, vec2 center, float radius) {
    vec2 d = uv - center;
    float r = length(d);
    if (r <= 2.5) return 1.0;
    if (r <= radius && abs(d.y + 0.5) <= 1.0 && mod(d.x + 1.0, 50.0) < 2.0) return 1.0;
    if (abs(d.y + 0.5) <= 1.0 && r >= 50.0 && r < 115.0) return 0.5;
    return 0.0;
}

float bip1(vec2 uv, vec2 center) { return SMOOTH(length(uv - center), 3.0); }

float bip2(vec2 uv, vec2 center) {
    float r = length(uv - center);
    float R = 8.0 + mod(87.0 * time, 80.0);
    return (0.5 - 0.5 * cos(30.0 * time)) * SMOOTH(r, 5.0)
         + SMOOTH(6.0, r) - SMOOTH(8.0, r)
         + smoothstep(max(8.0, R - 20.0), R, r) - SMOOTH(R, r);
}

void main() {
    vec3 finalColor = vec3(0.0);
    vec2 uv  = gl_FragCoord.xy;
    vec2 c   = resolution * 0.5;

    float colorMix = clamp(color_temp, 0.0, 1.0);
    finalColor = mix(blue3, blue1, colorMix) * 0.3 * dots(uv, c, 240.0);

    finalColor += (circle(uv, c, 100.0, 1.0) + circle(uv, c, 165.0, 1.0)) * mix(blue1, blue2, colorMix);
    finalColor += circle(uv, c, 240.0, 2.0) * mix(blue1, blue4, colorMix);
    finalColor += circle3(uv, c, 313.0, 4.0) * mix(blue1, blue2, colorMix);

    float triScale = tri_size * (1.0 + sin(time * 0.5) * 0.1);
    finalColor += triangles(uv, c, 315.0 + 30.0 * sin(time)) * mix(blue2, blue1, colorMix);
    finalColor += movingLine(uv, c, 240.0) * sweep_width * mix(blue3, blue4, colorMix);
    finalColor += circle(uv, c, 10.0, 1.0) * mix(blue3, blue1, colorMix);

    float opening = 0.5 + 0.2 * cos(time * sweep_speed);
    finalColor += 0.7 * circle2(uv, c, 262.0, 1.0, opening) * mix(blue3, blue4, colorMix);

    if (length(uv - c) < 240.0) {
        finalColor += bip1(uv, c + vec2(130.0 * cos(3.0 + 0.1 * time * blip_activity),
                                        130.0 * sin(3.0 + 0.1 * time * blip_activity)));
        finalColor += bip1(uv, c + vec2(130.0 * cos(-2.0 + sin(0.1 * time) + 0.15 * time),
                                        130.0 * sin(-2.0 + sin(0.1 * time) + 0.15 * time)));
        finalColor += bip2(uv, c + vec2(50.0 * cos(1.54 + 1.37 + sin(0.1 * time + 7.0) + 0.2 * time),
                                        50.0 * sin(1.54 + 1.37 + sin(0.1 * time + 7.0) + 0.2 * time))) * red;
    }

    gl_FragColor = vec4(finalColor, 1.0);
}