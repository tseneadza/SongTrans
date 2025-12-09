# lyrics_service.py Documentation

## Overview
Service class for fetching song lyrics from the Genius API using the lyricsgenius library.

## Dependencies
- **os**: Environment variable access
- **lyricsgenius**: Genius API client library
- **dotenv**: Load environment variables from .env file

## Class: LyricsService

### `__init__(self)`
**Description**: Initialize the Genius API client with authentication

**Process**:
1. Loads environment variables from .env file
2. Retrieves GENIUS_API_TOKEN from environment
3. Raises ValueError if token not found
4. Creates lyricsgenius.Genius instance with token
5. Configures genius client settings

**Configuration**:
```python
self.genius.verbose = False  # Suppress debug output
self.genius.remove_section_headers = True  # Remove [Verse 1], [Chorus], etc.
```

**Raises**:
- `ValueError`: If GENIUS_API_TOKEN not found in environment

**Example**:
```python
try:
    lyrics_service = LyricsService()
except ValueError as e:
    print(f"Error: {e}")
```

---

### `fetch_lyrics(self, song_name, artist_name=None)`
**Description**: Fetch lyrics for a given song with optional artist name

**Parameters**:
- `song_name` (str): Title of the song to search for
- `artist_name` (str, optional): Name of the artist (improves accuracy)

**Returns**:
- `dict`: Song data if found
  ```python
  {
      'title': str,    # Official song title
      'artist': str,   # Artist name
      'lyrics': str    # Full lyrics text
  }
  ```
- `None`: If song not found or error occurs

**Behavior**:
1. If `artist_name` provided: searches for song by specific artist
2. If no artist: searches for song by name only (less accurate)
3. Uses Genius API's fuzzy matching to find best match
4. Section headers are removed automatically (configured in __init__)

**Error Handling**:
- Catches all exceptions
- Prints error message to console
- Returns None on any error

**Example Usage**:
```python
# With artist (recommended)
lyrics = lyrics_service.fetch_lyrics("Imagine", "John Lennon")

# Without artist (less accurate)
lyrics = lyrics_service.fetch_lyrics("Imagine")

# Check result
if lyrics:
    print(f"Title: {lyrics['title']}")
    print(f"Artist: {lyrics['artist']}")
    print(f"Lyrics:\n{lyrics['lyrics']}")
else:
    print("Song not found")
```

**API Limitations**:
- Requires valid GENIUS_API_TOKEN
- Subject to Genius API rate limits
- May return wrong song if name is ambiguous without artist
- Genius database may not have all songs

**Notes**:
- Lyrics are returned as plain text
- Section headers ([Verse], [Chorus]) are removed
- May include Genius annotations/metadata in lyrics text
- Results cached by the caller (app.py), not internally
