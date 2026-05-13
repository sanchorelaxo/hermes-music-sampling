# GLSL Quick Reference — Hypno 2

Cheat sheet for GLSL built-in functions commonly used in Hypno 2 `.frag` shaders. The Hypno 2 runs GLSL ES (embedded subset) on a Raspberry Pi 5 GPU. All functions below are available.

## Types

| Type | Description | Example |
|------|-------------|---------|
| `float` | Scalar | `1.0`, `0.5` |
| `vec2` | 2-component vector | `vec2(1.0, 0.0)` |
| `vec3` | 3-component vector (RGB) | `vec3(1.0, 0.0, 0.0)` |
| `vec4` | 4-component vector (RGBA) | `vec4(1.0, 0.0, 0.0, 1.0)` |
| `mat2` | 2×2 matrix | `mat2(c, -s, s, c)` |
| `int` | Integer (limited use in ES) | `int i = 0` |

**Swizzling:** `p.x`, `p.y`, `col.rgb`, `col.xxx` (splat), `col.rg`

## Math

| Function | Description |
|----------|-------------|
| `abs(x)` | Absolute value |
| `sign(x)` | -1.0, 0.0, or 1.0 |
| `floor(x)` | Round down |
| `ceil(x)` | Round up |
| `fract(x)` | Fractional part: `x - floor(x)` |
| `mod(x, y)` | Modulo: `x - y * floor(x / y)` |
| `min(x, y)` | Minimum |
| `max(x, y)` | Maximum |
| `clamp(x, a, b)` | Clamp to [a, b] |
| `mix(a, b, t)` | Linear interpolate: `a + (b - a) * t` |
| `step(edge, x)` | 0.0 if x < edge, else 1.0 |
| `smoothstep(a, b, x)` | Smooth Hermite interpolation (0→1 between a and b) |
| `pow(x, y)` | x raised to y |
| `sqrt(x)` | Square root |
| `inversesqrt(x)` | `1.0 / sqrt(x)` (GPU-optimized) |
| `exp(x)` | e^x |
| `log(x)` | Natural log |
| `exp2(x)` | 2^x |
| `log2(x)` | Base-2 log |

## Trig

| Function | Description |
|----------|-------------|
| `sin(x)` | Sine (radians) |
| `cos(x)` | Cosine |
| `tan(x)` | Tangent |
| `asin(x)` | Arc sine |
| `acos(x)` | Arc cosine |
| `atan(x)` | Arc tangent |
| `atan(y, x)` | Arc tangent of y/x (quadrant-correct) |

## Vector

| Function | Description |
|----------|-------------|
| `length(v)` | Euclidean length |
| `distance(a, b)` | Distance between two points |
| `dot(a, b)` | Dot product — most useful math function in GLSL |
| `cross(a, b)` | Cross product (vec3 only) |
| `normalize(v)` | Unit vector |
| `reflect(I, N)` | Reflection vector |
| `refract(I, N, eta)` | Refraction vector |

## Derivatives (screen-space)

| Function | Description | Pi 5 Note |
|----------|-------------|-----------|
| `dFdx(v)` / `fwidth(v)` | Screen-space gradient | Works but quality varies; prefer explicit neighbor sampling for precise edge detection |

## Rotation Matrix (2D)

```glsl
float angle = time * 0.5;
mat2 rot = mat2(cos(angle), -sin(angle),
                sin(angle),  cos(angle));
p = rot * p;  // rotates point around origin
```

## Common Conversions

| Task | Expression |
|------|-----------|
| Degrees → radians | `angle * 3.14159 / 180.0` |
| Cartesian → polar (angle) | `atan(p.y, p.x)` |
| Cartesian → polar (radius) | `length(p)` |
| Polar → cartesian | `vec2(cos(a), sin(a)) * r` |
| Normalize 0..1 UV | `gl_FragCoord.xy / resolution` |
| Center -1..1 aspect-correct | `(gl_FragCoord.xy - 0.5 * resolution) / resolution.y` |
| RGB → grayscale | `dot(col, vec3(0.299, 0.587, 0.114))` |

## Vector Swizzle Patterns

```glsl
vec3 col = vec3(1.0, 0.5, 0.0);

col.rgb   → (1.0, 0.5, 0.0)   // RGB accessor
col.bgr   → (0.0, 0.5, 1.0)   // reverse
col.rrr   → (1.0, 1.0, 1.0)   // splat red channel
col.xy    → (1.0, 0.5)         // drop Z
```

## Anti-Aliasing (mandatory)

Always smoothstep over a few pixels to avoid aliasing on the Pi 5:

```glsl
float aa = 2.0 / resolution.y;           // ~2 pixel width
float mask = 1.0 - smoothstep(-aa, aa, distance);
```

## Constants

| Name | Value | Usage |
|------|-------|-------|
| `PI` | `3.14159` | full circle |
| `TAU` / `2PI` | `6.28318` | one full rotation: `sin(time * TAU)` = 1 Hz |
| `resolution` | built-in uniform | canvas width × height |

## Hypno 2 Uniform Naming

Underscores become spaces in the UI. Keep names short and descriptive:

| GLSL | UI Label | CC |
|------|----------|----|
| `uniform float speed;` | `speed` | 0 |
| `uniform float zoom;` | `zoom` | 1 |
| `uniform float hue_shift;` | `hue shift` | 2 |
| `uniform float wave_amt;` | `wave amt` | 3 |
| `uniform float distort;` | `distort` | 4 |

Avoid: `uniform float my_parameter_name_is_too_long_for_ui;`

## GLSL ES Limitations (Pi 5)

- No `textureGather`, `textureQueryLOD` — basic `texture2D` only
- Loop bounds must be compile-time constants or uniforms (not dynamic variables)
- `int`-to-`float` in loop conditions: cast with `float(i)`
- No bitwise ops (`&`, `|`, `^`, `~`, `<<`, `>>`)
- `precision mediump float;` recommended at top of every shader

## Quick Debug Patterns

```glsl
// Visualize a float (green=high, red=low)
vec3 debug = mix(vec3(1.0, 0.0, 0.0), vec3(0.0, 1.0, 0.0), value);
gl_FragColor = vec4(debug, 1.0);

// Visualize UV coordinates (red=x, green=y)
gl_FragColor = vec4(uv.x, uv.y, 0.0, 1.0);

// Quantize to N colors for posterize debugging
float steps = 16.0;
gl_FragColor = vec4(floor(value * steps) / steps, 0.0, 0.0, 1.0);
```
