# Hypno 2 Confirmed Working Shader Variants

Deployed to `/home/pi/Documents/VIDOS-Resources/Shaders/fx/` on device `192.168.1.54`.

## Base Shaders (copy from device at `/opt/VIDOS/release/Resources/Shaders/fx/`)

| File | Description | Custom CC |
|------|-------------|-----------|
| `fx_hsv.frag` | HSV shift + luminance-driven hue + difference blend | — |
| `fx_feedback.frag` | Clean feedback pass + KeepForeground + ColorClamp | — |
| `fx_hyperdigital.frag` | Feedback divide mode (frame / (feedback * amp)) | — |
| `fx_lumakey.frag` | Edge detect + luminance key + hue shift | — |
| `fx_hsv_backup.frag` | Clean copy of original fx_hsv.frag | — |

## Custom Variants (deployed to Shaders/fx/)

| File | Base | Tweak | cc2 effect |
|------|------|-------|------------|
| `fx_hsv_satboost.frag` | fx_hsv | Saturation multiplier | cc2 scales saturation (0=normal, 2=oversaturated) |
| `fx_hsv_spiral.frag` | fx_hsv | Spiral twist in feedback UV | cc2 = twist strength proportional to radius |
| `fx_hsv_chroma.frag` | fx_hsv | Chroma aberration (RGB split from center) | cc2 = radial channel offset magnitude |
| `fx_hsv_pixelize.frag` | fx_hsv | Quantized color steps | cc2 → steps (2=blocky, 20=near-native) |
| `fx_hsv_strobe.frag` | fx_hsv | Strobe gate on feedback | cc2 = flash rate (strobe_gate = sin(time * cc2 * 30)) |
| `fx_hsv_contrast.frag` | fx_hsv | Power-curve contrast | cc2 → exponent (<1 flat, >1 punchy) |
| `fx_feedback_mirror.frag` | fx_feedback | Mirror flip feedback UV | cc2: 0=none, >0.15=hflip, >0.45=vflip, >0.85=both |

## Key Pattern (for future variants)

All variants use this structure:
```glsl
#include "FeedbackUtil.frag"
uniform sampler2D sampled_frame;
uniform sampler2D feedback_frame;
// ... uniforms ...
void main(void) {
    float feedback = cc1;
    float fb_x = cc3;
    float fb_y = cc5;
    float fb_zoom = cc4;
    float fb_rotate = cc6;
    float black_key = cc7;
    // frame grab + fb UV + effects...
    frame_color = srgb_from_linear_srgb(frame_color);
    gl_FragColor = vec4(frame_color, 1.0);
}
```

Custom parameter: `float my_param = max(0.0, cc2);` — cc2 is unused by all built-in shaders and safe for custom effects.