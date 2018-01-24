```sql
CREATE TABLE artists(
artist_name TEXT,
artist_id TEXT PRIMARY KEY,
artist_popularity TEXT,
artist_type TEXT 
);

CREATE TABLE tracks(
album_art TEXT,
album_id TEXT,
album_name TEXT,
artist_id TEXT PRIMARY KEY,
duration_ms REAL,
energy REAL,
livesness REAL, 
loudness REAL,
speechiness REAL,
tempo REAL,
track_id TEXT,
track_name TEXT
);

CREATE TABLE lyrics(
track_id TEXT PRIMARY KEY,
lyrics TEXT
);

CREATE TABLE track_previews(
track_id TEXT PRIMARY KEY,
track_preview_url TEXT
);
```
