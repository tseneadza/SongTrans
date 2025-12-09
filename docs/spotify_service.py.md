# spotify_service.py Documentation

## Overview
Service class for fetching artist and album data from Spotify API using the spotipy library.

## Dependencies
- **os**: Environment variable access
- **spotipy**: Spotify API client library
- **spotipy.oauth2**: Authentication manager
- **dotenv**: Load environment variables from .env file

## Class: SpotifyService

### `__init__(self)`
**Description**: Initialize the Spotify API client with client credentials authentication

**Process**:
1. Loads environment variables from .env file
2. Retrieves SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET
3. If credentials missing: prints warning, sets `self.sp = None`
4. If credentials present: creates authenticated spotipy.Spotify client

**Authentication**: Uses Client Credentials Flow (no user auth required)

**Graceful Degradation**: App continues without Spotify features if credentials missing

**Example**:
```python
spotify_service = SpotifyService()
if spotify_service.sp:
    # Spotify features available
else:
    # Fall back to Genius-only data
```

---

### `search_artist(self, artist_name)`
**Description**: Search for an artist on Spotify by name

**Parameters**:
- `artist_name` (str): Name of artist to search

**Returns**:
- `dict`: First matching artist object (full Spotify artist data)
- `None`: If not found, no credentials, or error

**Spotify Artist Object** (selected fields):
```python
{
    'id': str,           # Spotify artist ID
    'name': str,         # Artist name
    'followers': dict,   # Follower count
    'genres': list,      # Associated genres
    'images': list,      # Artist images
    'popularity': int    # 0-100 popularity score
}
```

**Search Behavior**:
- Searches for exact and fuzzy matches
- Returns only first result (most relevant)
- Case-insensitive matching

**Example**:
```python
artist = spotify_service.search_artist("Drake")
if artist:
    print(f"Found: {artist['name']} (ID: {artist['id']})")
else:
    print("Artist not found")
```

---

### `get_artist_albums(self, spotify_artist_id)`
**Description**: Get all albums and singles for an artist

**Parameters**:
- `spotify_artist_id` (str): Spotify artist ID (from search_artist)

**Returns**:
- `list[dict]`: List of album objects
- `[]`: Empty list if no albums, no credentials, or error

**Album Object Structure**:
```python
{
    'id': str,            # Spotify album ID
    'name': str,          # Album name
    'type': str,          # 'album' or 'single'
    'release_date': str,  # ISO date string
    'total_tracks': int,  # Number of tracks
    'image_url': str      # Album cover URL (or None)
}
```

**Features**:
- Fetches up to 50 albums per request
- Automatically handles pagination
- Removes duplicate albums (same name in different markets)
- Includes both albums and singles
- Sorts by release date (newest first)

**Pagination**:
```python
# Automatically fetches all pages
while results['next']:
    results = self.sp.next(results)
```

**Example**:
```python
albums = spotify_service.get_artist_albums("artist_id_here")
for album in albums:
    print(f"{album['name']} ({album['type']}) - {album['total_tracks']} tracks")
```

---

### `get_album_tracks(self, spotify_album_id)`
**Description**: Get all tracks from a specific album

**Parameters**:
- `spotify_album_id` (str): Spotify album ID

**Returns**:
- `list[dict]`: List of track objects
- `[]`: Empty list if no tracks, no credentials, or error

**Track Object Structure**:
```python
{
    'name': str,          # Track name
    'track_number': int,  # Position on album
    'duration_ms': int,   # Duration in milliseconds
    'artists': list[str]  # List of artist names
}
```

**Features**:
- Fetches up to 50 tracks per request
- No pagination (single request for most albums)
- Extracts only essential track information

**Example**:
```python
tracks = spotify_service.get_album_tracks("album_id_here")
for track in tracks:
    duration_sec = track['duration_ms'] / 1000
    print(f"{track['track_number']}. {track['name']} - {duration_sec}s")
```

---

## Error Handling
All methods:
- Return `None` or `[]` on error (never raise exceptions)
- Print error messages to console
- Check if `self.sp` is None before API calls
- Gracefully handle API failures

---

## Rate Limiting
Spotify API limits:
- **Client Credentials**: ~100 requests per minute
- No specific per-method limits
- Errors return HTTP 429 with Retry-After header

**Mitigation** (implemented in app.py):
- Caching (7 days for album/track data)
- Batch requests where possible

---

## Authentication Flow

### Client Credentials Flow
```
1. App sends client_id + client_secret
2. Spotify returns access_token
3. Token used for all API requests
4. Token auto-refreshed by spotipy
```

**Advantages**:
- No user authentication required
- Suitable for server-side apps
- Access to public data only

**Limitations**:
- Cannot access user-specific data (playlists, liked songs, etc.)
- Cannot modify user data

---

## Usage Patterns

### Pattern 1: Search and Get Albums
```python
# 1. Search for artist
artist = spotify_service.search_artist("Taylor Swift")

# 2. Get albums
if artist:
    albums = spotify_service.get_artist_albums(artist['id'])
    for album in albums:
        print(album['name'])
```

### Pattern 2: Get Album Tracks
```python
# Get tracks from specific album
tracks = spotify_service.get_album_tracks("album_id")
for track in tracks:
    print(f"{track['track_number']}. {track['name']}")
```

### Pattern 3: Full Artist Discography
```python
artist = spotify_service.search_artist("The Beatles")
if artist:
    albums = spotify_service.get_artist_albums(artist['id'])
    
    for album in albums:
        tracks = spotify_service.get_album_tracks(album['id'])
        print(f"\n{album['name']} ({len(tracks)} tracks)")
        for track in tracks:
            print(f"  {track['track_number']}. {track['name']}")
```

---

## Integration with app.py

**Data Flow**:
1. User selects artist → `search_artist(name)`
2. App fetches albums → `get_artist_albums(artist_id)`
3. User selects album → `get_album_tracks(album_id)`
4. App matches tracks with Genius song IDs
5. User selects song → fetch lyrics from Genius

**Why Spotify + Genius?**
- Spotify: Structured album/track data
- Genius: Lyrics content
- Combined: Complete song information

---

## Troubleshooting

### No Credentials Warning
```
Warning: Spotify credentials not found. Album features will be limited.
```
**Solution**: Add credentials to .env file

### Empty Results
```python
albums = spotify_service.get_artist_albums(artist_id)
# albums == []
```
**Possible Causes**:
1. Invalid artist_id
2. Artist has no albums on Spotify
3. API error (check console logs)

### Duplicate Albums
**Cause**: Same album released in multiple markets  
**Solution**: Built-in deduplication by album name
