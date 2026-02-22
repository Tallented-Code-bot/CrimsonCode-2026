CREATE TABLE IF NOT EXISTS admins (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL
);

-- Known individuals the face model can recognize.
-- 'Unknown' is used in events when no match is found.
CREATE TABLE IF NOT EXISTS persons (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT    NOT NULL UNIQUE
);

-- One row per detection event from the camera feed.
CREATE TABLE IF NOT EXISTS events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    person_name TEXT    NOT NULL DEFAULT 'Unknown',
    confidence  REAL,   -- model confidence 0.0-1.0, NULL for unknowns
    image_path  TEXT,   -- optional snapshot path
    timestamp   TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);
