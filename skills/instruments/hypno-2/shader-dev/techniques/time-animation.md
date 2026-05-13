# Time Animation — Hypno 2

The Hypno 2 provides a built-in `uniform float time` — a monotonically increasing value in seconds since shader load or reset. This is your primary animation driver and is "free" (no uniform slot consumed).

## Core Principles

`time` is a **float in seconds** — use it to drive:
- Coordinate offsets (scroll, pan, drift)
- Phase shifts (sin/cos oscillation)
- Noise field motion
- Rotation and scaling
- Parameter sweeps

## Basic Patterns

### Smooth Scroll / Pan
```glsl
p += vec2(time * scroll_speed, time * scroll_speed * 0.5);
```

### Oscillation (breathe, pulse, swing)
```glsl
float pulse = 1.0 + sin(time * pulse_speed) * pulse_amount;
p *= pulse;  // breathing zoom

float rotation = time * rotation_speed;
// rotate p by rotation
```

### Cyclic (sawtooth reset)
```glsl
float cycle = fract(time / cycle_duration);  // 0→1→0→1...
```

### Ping-Pong (back and forth)
```glsl
float pingpong = abs(fract(time / cycle_duration) * 2.0 - 1.0);  // 0→1→0...
```

### Staggered (phase-shifted copies)
```glsl
// Multiple elements with phase offset
float phase1 = sin(time * speed);
float phase2 = sin(time * speed + 1.5);   // 1.5 rad offset
float phase3 = sin(time * speed + 3.0);
```

## Speed Control Pattern

Always expose speed as a uniform for CC mapping:

```glsl
uniform float speed;  // CC N — 0.0 (frozen) to 1.0 (full speed)

float t = time * speed * 2.0;  // speed 0.5 = real-time, 1.0 = 2× speed
```

Or with a range multiplier:

```glsl
uniform float speed;  // CC N — maps 0.0–10.0× real time

float t = time * speed * 5.0;  // CC midpoint = real-time, full CC = 5× speed
```

## Time-Driven Effects Catalog

### 1. Noise Field Drift
```glsl
// Offset noise coordinates over time
float n = fbm(uv * 3.0 + time * speed * 0.1);
```

### 2. Rotating Pattern
```glsl
float angle = time * speed;
mat2 rot = mat2(cos(angle), -sin(angle), sin(angle), cos(angle));
p = rot * p;
```

### 3. Breathing Scale
```glsl
float scale = 1.0 + sin(time * speed) * 0.3;
p *= scale;
```

### 4. Wobble / Warble
```glsl
p.x += sin(time * speed + p.y * 5.0) * 0.1;
p.y += cos(time * speed * 0.7 + p.x * 3.0) * 0.1;
```

### 5. Color Cycle
```glsl
float hue = fract(time * speed * 0.1);
vec3 col = hsv2rgb(vec3(hue, 0.8, 1.0));
```

### 6. Strobe / Blink
```glsl
float strobe = step(0.5, fract(time * speed * 4.0));  // 4 Hz at speed=1
col *= strobe * 0.8 + 0.2;  // never fully dark
```

### 7. Multi-Scale Time
```glsl
// Different speeds create complex motion
float slow = time * speed * 0.05;   // background drift
float med  = time * speed * 0.5;    // mid-frequency detail
float fast = time * speed * 3.0;    // high-frequency shimmer

p += vec2(slow, slow * 0.7);
float n = fbm(p * 3.0);
n += sin(p.x * 10.0 + fast) * 0.1;
```

### 8. Repeating Sweep / Trigger
```glsl
// A value that sweeps 0→1 every N seconds
float sweep = fract(time * speed / sweep_period);
// Use to crossfade between states
col = mix(stateA, stateB, smoothstep(0.3, 0.7, sweep));
```

## Time Reset / Phase Control

The Hypno 2 time uniform **resets on shader load** and counts upward. For loops, use `fract()`:

```glsl
float looped_time = fract(time / loop_duration) * loop_duration;
```

For synchronized multi-parameter animations:
```glsl
// All parameters driven from the same phase
float phase = time * speed;
float p1 = sin(phase);           // parameter 1
float p2 = sin(phase + 2.0);     // parameter 2 (offset)
float p3 = sin(phase * 0.5);     // parameter 3 (half-speed)
float p4 = fract(phase / 6.28);  // parameter 4 (cyclic 0–1)
```

## Full Hypno 2 Shader: Animated Everything

```glsl
uniform vec2 resolution;
uniform float time;
uniform float speed;          // CC 0 — master animation speed
uniform float scale;          // CC 1 — pattern zoom
uniform float rotate;         // CC 2 — rotation speed
uniform float pulse;          // CC 3 — pulse/breath amount
uniform float drift;          // CC 4 — drift/scroll speed

// Include fbm(), palette() from other techniques

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = fragCoord / resolution.xy;
    vec2 p = (fragCoord - 0.5 * resolution.xy) / resolution.y;
    
    // Animate: drift
    p += vec2(time * drift * 0.5, time * drift * 0.3);
    
    // Animate: rotate
    float angle = time * rotate * 0.5;
    mat2 rot = mat2(cos(angle), -sin(angle), sin(angle), cos(angle));
    p = rot * p;
    
    // Animate: breathe (scale pulse)
    float breathe = 1.0 + sin(time * speed * 0.5) * pulse;
    p *= scale * breathe;
    
    // Generate pattern
    float n = fbm(p + time * speed * 0.1);
    
    // Animate: color cycle from time
    vec3 col = 0.5 + 0.5 * cos(6.28318 * (n + time * speed * 0.05 + vec3(0.0, 0.33, 0.67)));
    
    fragColor = vec4(col, 1.0);
}
```

## Performance

Time-based animation costs nothing extra — you're just changing the inputs to existing functions. The `sin()`, `cos()`, `fract()`, and `mat2` constructor are all single-cycle or near-single-cycle operations even on the Pi 5 GPU.

## See Also

- `noise-generators.md` — Time-driven noise field motion
- `domain-warping.md` — Animate each warp layer at different speeds
- `feedback-effects.md` — Time-based ghosting echoes
