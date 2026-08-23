"""Mixxx playlist access.

Resolves playlist membership to real track metadata and file paths using the
modern Mixxx schema (``library.location`` -> ``track_locations.id`` join).
"""
from .library import connect, _resolve_location, _table_exists


def list_playlists():
    """Return a list of {id, name, track_count, hidden} for all playlists."""
    conn = connect()
    if conn is None:
        return []
    try:
        cur = conn.cursor()
        if not _table_exists(cur, "Playlists"):
            return []
        out = []
        for r in conn.execute(
            "SELECT id, name, hidden FROM Playlists ORDER BY id"
        ).fetchall():
            count = 0
            if _table_exists(conn.cursor(), "PlaylistTracks"):
                row = conn.execute(
                    "SELECT COUNT(*) FROM PlaylistTracks WHERE playlist_id=?", (r["id"],)
                ).fetchone()
                count = row[0]
            out.append(
                {"id": r["id"], "name": r["name"], "track_count": count, "hidden": r["hidden"]}
            )
        return out
    finally:
        conn.close()


def get_playlist(playlist_id):
    """Return playlist metadata dict or None."""
    conn = connect()
    if conn is None:
        return None
    try:
        row = conn.execute("SELECT * FROM Playlists WHERE id=?", (playlist_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_playlist_tracks(playlist_id):
    """Return the tracks in a playlist in stored order.

    Each dict: id, artist, title, duration, bpm, key, file (resolved path),
    position. Missing/unresolvable files still appear (file may be None) so
    callers can decide how to handle them.
    """
    conn = connect()
    if conn is None:
        return []
    try:
        cur = conn.cursor()
        if not _table_exists(cur, "PlaylistTracks"):
            return []
        rows = conn.execute(
            """SELECT pt.position, l.id, l.artist, l.title, l.album, l.duration,
                      l.bpm, l.key, l.location
               FROM PlaylistTracks pt
               JOIN library l ON l.id = pt.track_id
               WHERE pt.playlist_id = ?
               ORDER BY pt.position""",
            (playlist_id,),
        ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["file"] = _resolve_location(conn, d.pop("location"))
            out.append(d)
        return out
    finally:
        conn.close()


def existing_files(playlist_id):
    """Return only the playlist's track files that exist on disk."""
    out = []
    for t in get_playlist_tracks(playlist_id):
        if t.get("file") and __import__("os").path.exists(t["file"]):
            out.append(t["file"])
    return out
