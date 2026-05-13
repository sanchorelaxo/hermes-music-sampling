# Feedback Effects — Hypno 2

The Hypno 2's killer feature is real video feedback — but that happens at the **mixer level** (Main track), not inside fragment shaders. However, you can create faux-feedback and accumulation effects within a single shader pass using creative UV manipulation and the `time` uniform.

These techniques complement (not replace) the hardware feedback pipeline. Use them to add feedback-style effects to generative shape shaders running on Track A/B.

## Core Techniques

### 1. Temporal Ghosting (UV Offset by Time)

Simulate trailing by layering shifted copies of the current pattern:

```glsl
vec3 ghosting(vec2 p, float time, int ghosts) {
    vec3 col = vec3(0.0);
    float totalWeight = 0.0;
    
    for (int i = 0; i < 8; i++) {
        if (i >= ghosts) break;
        
        float t = float(i) * 0.02;
        float weight = 1.0 / (1.0 + float(i));  // fade older copies
        vec2 offset = vec2(sin(time - t * 10.0), cos(time - t * 10.0)) * float(i) * 0.01;
        col += patternColor(p + offset, time - t) * weight;
        totalWeight += weight;
    }
    
    return col / totalWeight;
}
```

### 2. Spiral Feedback (Rotating Echo)

```glsl
vec3 spiralEcho(vec2 p, float time, float strength) {
    vec3 col = vec3(0.0);
    float alpha = 1.0;
    vec2 offset = vec2(0.0);
    
    for (int i = 0; i < 6; i++) {
        // Each echo is rotated and attenuated
        float angle = float(i) * strength * 0.3;
        float s = sin(angle), c = cos(angle);
        offset = mat2(c, -s, s, c) * (offset + vec2(0.01));
        
        alpha *= 0.6;  // exponential fade
        col += patternColor(p + offset, time) * alpha;
    }
    
    return col;
}
```

### 3. Zoom Feedback (Inward Spiral)

```glsl
vec3 zoomFeedback(vec2 p, float time, float strength) {
    vec3 col = vec3(0.0);
    float scale = 1.0;
    float alpha = 1.0;
    
    for (int i = 0; i < 6; i++) {
        col += patternColor(p * scale, time) * alpha;
        scale *= 0.85;   // shrink each iteration
        alpha *= 0.5;
    }
    
    return col;
}
```

### 4. Displacement Feedback (Warped Echoes)

Combine with domain warping for organic feedback trails:

```glsl
vec3 displacementFeedback(vec2 p, float time) {
    vec3 col = patternColor(p, time);  // base layer
    float alpha = 0.5;
    vec2 displace = vec2(0.0);
    
    for (int i = 0; i < 5; i++) {
        // Warp displacement based on noise
        displace += vec2(
            noise(p * 3.0 + displace + time * 0.1),
            noise(p * 3.0 + displace + time * 0.1 + vec2(5.2))
        ) * 0.02;
        
        col += patternColor(p + displace, time) * alpha;
        alpha *= 0.5;
    }
    
    return col;
}
```

### 5. Faux Video Bleed (Luminance-Based Ghost)

Simulate the brightness-dependent ghosting of real video feedback:

```glsl
vec3 videoBleed(vec2 p, float time) {
    vec3 col = patternColor(p, time);
    float luminance = dot(col, vec3(0.299, 0.587, 0.114));
    
    // Brighter areas bleed more
    float bleedStrength = luminance * 0.3;
    
    for (int i = 0; i < 4; i++) {
        float t = float(i + 1) * 0.04;
        vec2 offset = vec2(cos(time * 0.5 + float(i)), sin(time * 0.5 + float(i))) * bleedStrength * float(i);
        
        vec3 ghost = patternColor(p + offset, time - t);
        float ghostLuma = dot(ghost, vec3(0.299, 0.587, 0.114));
        float blend = bleedStrength * ghostLuma / float(i + 1);
        col = mix(col, ghost, blend);
    }
    
    return col;
}
```

## Integration with Hypno 2's Hardware Feedback

These shader-level feedback effects are **additive** to the mixer feedback. Combine them:

| Layer | Where | Effect |
|-------|-------|--------|
| Shader-level ghosting | Track A/B .frag | Generates internal echo trails within the shape |
| Mixer feedback (CC 1) | Main track | Classic frame-to-frame feedback on the combined output |
| Mixer FB zoom (CC 4) | Main track | Fractal zoom on the feedback |
| Shader-level zoom echo | Track A/B .frag | Spiral/zoom distortion before the mixer |

A shader with ghosting loaded on Track A + Main feedback at 0.7 + slight FB zoom = massive, evolving visual complexity.

## Performance

All faux-feedback techniques use **fixed iteration counts**:
- 6 echoes: safe at 1080p 60 fps
- 8 echoes: manageable at 1080p 30 fps
- 10+ echoes: may need 720p or lower

Each iteration evaluates `patternColor()` once, so the cost multiplier = iteration count × pattern cost.

## See Also

- `domain-warping.md` — Combine warp + feedback echo for extra organic trails
- `blend-modes.md` — Use additive blending for brighter feedback accumulation
- Hypno 2 Main track feedback controls (CC 1, 3, 4, 5, 6) — the hardware feedback pipeline
