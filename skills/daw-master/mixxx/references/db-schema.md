# Mixxx Database Schema Notes

## Modern schema (Mixxx 2.4+, used by flatpak 2.5.6 on this machine)

The track path lives in a separate table. `library.location` is an **integer
foreign key** into `track_locations.id`, NOT a path string:

```sql
-- track_locations
CREATE TABLE track_locations (
    id INTEGER PRIMARY KEY,
    location TEXT          -- absolute filesystem path
);

-- library (relevant columns)
CREATE TABLE library (
    id INTEGER PRIMARY KEY,
    artist TEXT,
    title TEXT,
    album TEXT,
    duration REAL,         -- seconds
    bpm REAL,
    key TEXT,
    location INTEGER,      -- FK -> track_locations.id
    mixxx_deleted INTEGER DEFAULT 0
);

-- Playlists
CREATE TABLE Playlists (
    id INTEGER PRIMARY KEY,
    name TEXT,
    hidden INTEGER DEFAULT 0
);

-- PlaylistTracks
CREATE TABLE PlaylistTracks (
    id INTEGER PRIMARY KEY,
    playlist_id INTEGER,
    track_id INTEGER,      -- FK -> library.id
    position INTEGER
);

-- cues
CREATE TABLE cues (
    id INTEGER PRIMARY KEY,
    track_id INTEGER,
    type INTEGER,          -- see type map below
    position INTEGER,      -- frames (44100 = 1 second)
    length INTEGER,
    hotcue INTEGER,
    label TEXT,
    color TEXT
);
```

The core query used for path resolution:

```sql
SELECT l.id, l.artist, l.title, t.location
FROM library l
JOIN track_locations t ON l.location = t.id
WHERE l.mixxx_deleted = 0;
```

## Legacy schema (Mixxx ≤ 2.3)

`library` had a `filepath` column (or `location` was a literal path string)
and no `track_locations` table. The port's `_resolve_location` handles both:
- int/str-digit `location` -> look up `track_locations`
- any other value -> treated as a literal path

## Cue type map (Mixxx 2.5+)

| type | name       | notes                          |
|------|------------|--------------------------------|
| 0    | cue        | plain cue point                |
| 1    | main_cue   | load point                     |
| 2    | hotcue     | hot cue button                 |
| 3    | loop       | loop                           |
| 4    | beatloop   | beat-synced loop               |
| 5    | intro      | intro start marker             |
| 6    | outro      | outro start marker             |
| 7    | beatjump   | position may be -1 sentinel    |
| 8    | preroll    | Mixxx 2.5+                     |

## Practical notes for this machine

- Flatpak DB: `~/.var/app/org.mixxx.Mixxx/.mixxx/mixxxdb.sqlite` (17,830
  tracks, 9 playlists, live).
- Snap (`mixxx-community` 2.4.0) has **no** `mixxxdb.sqlite` — only logs under
  `~/snap/mixxx-community/`. Don't point MIXXX_DB_PATH there.
- Some library rows point at paths that no longer exist (e.g. playlist 8 has 2
  of 6 dead). Always guard with `os.path.exists()` before feeding ffmpeg.
- Reads are done with `sqlite3.connect(f"file:{path}?mode=ro", uri=True)` —
  Mixxx may hold the DB open; read-only access is safe and non-locking.
