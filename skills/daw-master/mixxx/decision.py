"""Rule-based natural-language to autopilot-action mapping.

Maps short text suggestions (e.g. "more energy", "crossfade to 12") into
autopilot actions. Ported from cli-anything-mixxx autopilot/decision.py.
"""
import re


def _extract_number(text):
    m = re.search(r"(\d+(?:\.\d+)?)", text or "")
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            return None
    return None


def decide(text):
    """Return a dict {type, params} action for a natural-language suggestion.

    Returns None for empty input.
    """
    t = (text or "").lower()
    if not t.strip():
        return None

    # Energy heuristics
    if any(k in t for k in ("more energy", "higher energy", "raise energy", "faster")):
        return {"type": "play_next", "params": {"crossfade": 6.0}}
    if any(k in t for k in ("less energy", "calm", "soft", "chill")):
        return {"type": "play_next", "params": {"crossfade": 12.0}}

    # Crossfade commands
    if "crossfade now" in t or (t.startswith("crossfade") and "now" in t):
        secs = _extract_number(t) or 8.0
        return {"type": "crossfade_now", "params": {"crossfade": float(secs)}}
    if "set crossfade" in t or "crossfade to" in t:
        secs = _extract_number(t) or 8.0
        return {
            "type": "set_crossfade",
            "params": {"value": int(max(0, min(127, (secs / 12.0) * 127)))},
        }

    # Load a specific deck
    m = re.search(r"deck\s*(\d+)", t)
    if m:
        slot = int(m.group(1))
        return {"type": "load_and_play", "params": {"slot": slot}}

    # Keywords for explicit actions
    if any(k in t for k in ("next", "play next", "skip")):
        secs = _extract_number(t) or 8.0
        return {"type": "play_next", "params": {"crossfade": float(secs)}}

    # Default fallback
    return {"type": "play_next", "params": {"crossfade": 8.0}}
