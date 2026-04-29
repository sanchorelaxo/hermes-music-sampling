#!/usr/bin/env python3
"""
Example: apply a VST plugin chain (compressor -> EQ -> limiter).
"""
from dawdreamer import transform

result = transform(
    input="drums.wav",
    pipeline=[
        {"op": "load_vst", "path": "/usr/local/vst/BlockFreq.vst3"},
        {"op": "set_param", "plugin_idx": 0, "param": "Ratio", "value": 4.0},
        {"op": "set_param", "plugin_idx": 0, "param": "Threshold", "value": -24.0},
        {"op": "load_vst", "path": "/usr/local/vst/SoX_Equalizer.vst3"},
        {"op": "set_param", "plugin_idx": 1, "param": "Gain1", "value": 3.0},
        {"op": "load_vst", "path": "/usr/local/vst/ Limiter.vst3"},
    ],
    output="drums_processed.wav"
)

print(result)
