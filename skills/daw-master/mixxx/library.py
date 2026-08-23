"""Mixxx database access layer.

Reads the Mixxx track library, playlists, and cues from a mixxxdb.sqlite.

Targets the **modern** Mixxx schema (2.4+), where ``library.location`` is a
foreign key into ``track_locations.id`` (not a path string). Upstream
cli-anything-mixxx looked for a ``filepath`` column on ``library`` which no
longer exists; this module resolves real file paths via the join.

The connection is opened **read-only** (``mode=ro``), so these functions can
safely be used against a live Mixxx database while Mixxx is running.
"""
import os
import sqlite3


# Auto-detection order for the Mixxx database.
CANDIDATE_DB_PATHS = [
    # Flatpak install (modern, populated on this machine).
    os.path.expanduser("~/.var/app/org.mixxx.Mixxx/.mixxx/mixxxdb.sqlite"),
    # Snap install.
    os.path.expanduser("~/snap/mixxx-community/common/.mixxx/mixxxdb.sqlite"),
    # Classic ~/.mixxx install.
    os.path.expanduser("~/.mixxx/mixxxdb.sqlite"),
]


def get_db_path():
    """Return the Mixxx DB path, honouring MIXXX_DB_PATH, else auto-detect."""
    env = os.environ.get("MIXXX_DB_PATH")
    if env:
        return env
    for p in CANDIDATE_DB_PATHS:
        if os.path.exists(p):
            return p
    return CANDIDATE_DB_PATHS[0]


def connect(db_path=None):
    """Open a read-only connection to the Mixxx database.

    Returns None if the database file does not exist. Raises on schema errors.
    """
    path = db_path or get_db_path()
    if not os.path.exists(path):
        return None
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _table_exists(cur, name):
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
    return cur.fetchone() is not None


def _resolve_location(conn, location_col_value):
    """Resolve a library.location value to a filesystem path.

    In the modern schema ``location`` is an int FK into ``track_locations.id``;
    in legacy schemas it may be a literal path string already.
    """
    if location_col_value is None:
        return None
    if isinstance(location_col_value, int) or str(location_col_value).isdigit():
        if not _table_exists(conn.cursor(), "track_locations"):
            return None
        row = conn.execute(
            "SELECT location FROM track_locations WHERE id=?", (int(location_col_value),)
        ).fetchone()
        if row and row["location"]:
            return row["location"]
        return None
    return str(location_col_value)


def _library_columns(conn):
    """Return the set of column names present on the library table."""
    cur = conn.cursor()
    if not _table_exists(cur, "library"):
        return set()
    cur.execute("PRAGMA table_info('library')")
    return {row[1] for row in cur.fetchall()}


def list_tracks(limit=10, include_deleted=False):
    """Return a list of track dicts from the Mixxx library.

    Each dict: id, artist, title, album, duration, bpm, key, file (resolved
    absolute path), location (raw column value). Returns [] if DB missing.
    """
    conn = connect()
    if conn is None:
        return []
    try:
        cols = _library_columns(conn)
        if "library" not in cols and not _table_exists(conn.cursor(), "library"):
            return []
        select = ["id", "artist", "title", "album", "duration", "bpm", "key"]
        select = [c for c in select if c in cols]
        where = "WHERE mixxx_deleted = 0" if ("mixxx_deleted" in cols and not include_deleted) else ""
        rows = conn.execute(
            f"SELECT {', '.join(select)} FROM library {where} ORDER BY id LIMIT ?",
            (limit,),
        ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            # location may or may not be selected; fetch it for path resolution
            loc_row = conn.execute("SELECT location FROM library WHERE id=?", (d["id"],)).fetchone()
            d["location"] = loc_row["location"] if loc_row else None
            d["file"] = _resolve_location(conn, d["location"])
            out.append(d)
        return out
    finally:
        conn.close()


def get_track(track_id):
    """Return a single track dict (with resolved 'file' path) or None."""
    conn = connect()
    if conn is None:
        return None
    try:
        row = conn.execute("SELECT * FROM library WHERE id=?", (track_id,)).fetchone()
        if row is None:
            return None
        d = dict(row)
        d["file"] = _resolve_location(conn, d.get("location"))
        return d
    finally:
        conn.close()


def export_library(include_deleted=False):
    """Return the full library as a list of track dicts with resolved paths."""
    conn = connect()
    if conn is None:
        return []
    try:
        where = "WHERE mixxx_deleted = 0" if not include_deleted else ""
        rows = conn.execute(f"SELECT * FROM library {where}").fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["file"] = _resolve_location(conn, d.get("location"))
            out.append(d)
        return out
    finally:
        conn.close()
