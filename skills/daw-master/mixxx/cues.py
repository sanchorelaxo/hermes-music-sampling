"""Mixxx cue point access.

Mixxx cue types (cues.type):
  0 = Cue (plain cue point)
  1 = MainCue (load point)
  2 = HotCue
  3 = Loop
  4 = BeatLoop
  5 = Intro
  6 = Outro
  7 = BeatJump (position = -1 sentinel in some versions)
  8 = PreRoll (Mixxx 2.5+)
"""
from .library import connect, _table_exists

CUE_TYPE_NAMES = {
    0: "cue",
    1: "main_cue",
    2: "hotcue",
    3: "loop",
    4: "beatloop",
    5: "intro",
    6: "outro",
    7: "beatjump",
    8: "preroll",
}


def list_cues_for_track(track_id):
    """Return cue points for a track: {id, type, type_name, position, length,
    hotcue, label, color}. Positions/lengths are in frames unless 0."""
    conn = connect()
    if conn is None:
        return []
    try:
        cur = conn.cursor()
        if not _table_exists(cur, "cues"):
            return []
        rows = conn.execute(
            """SELECT id, track_id, type, position, length, hotcue, label, color
               FROM cues WHERE track_id = ? ORDER BY position, id""",
            (track_id,),
        ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            ctype = d.get("type")
            d["type_name"] = CUE_TYPE_NAMES.get(ctype, f"unknown({ctype})") if isinstance(ctype, int) else f"unknown({ctype})"
            out.append(d)
        return out
    finally:
        conn.close()
