# app.py Documentation

## Overview
Main Flask application file that serves the web interface and provides RESTful API endpoints for lyrics fetching, translation, artist/album search, and cache management.

## Dependencies
- **Flask**: Web framework
- **flask_cors**: Cross-Origin Resource Sharing support
- **lyrics_service**: Genius API lyrics fetching
- **translation_service**: OpenAI translation
- **spotify_service**: Spotify API for album data
- **cache_service**: File-based caching system

## Global Objects
```python
app = Flask(__name__)  # Flask application instance
lyrics_service = LyricsService()  # Lyrics fetching service
translation_service = TranslationService()  # Translation service
spotify_service = SpotifyService()  # Spotify data service
cache_service = CacheService()  # Caching service
```

---

## Routes / Endpoints

### `GET /`
**Function**: `index()`  
**Description**: Serves the main HTML interface  
**Returns**: Rendered `index.html` template  
**Parameters**: None

---

### `POST /api/translate`
**Function**: `translate_song()`  
**Description**: Fetches and translates song lyrics with caching  

**Request Body** (JSON):
```json
{
  "song_id": 123456,           // Optional, Genius song ID (preferred)
  "song_name": "Song Title",   // Fallback if song_id not provided
  "artist_name": "Artist",     // Optional
  "target_language": "English" // Optional, default: English
}
```

**Response** (JSON):
```json
{
  "title": "Song Title",
  "artist": "Artist Name",
  "original_lyrics": "...",
  "translated_lyrics": "...",
  "target_language": "English"
}
```

**Caching**:
- Lyrics cached for 30 days (720 hours)
- Translations cached for 30 days per language
- Cache keys: `{song_id/name}_{artist}` and `{song_id/name}_{artist}_{language}`

**Special Mode**:
- If `target_language == "original_only"`, returns original lyrics in both fields

**Error Responses**:
- `400`: Missing required parameters
- `404`: Song not found
- `500`: Fetch or translation failed

---

### `GET /api/search-artists`
**Function**: `search_artists()`  
**Description**: Search for artists with autocomplete functionality  

**Query Parameters**:
- `q`: Artist name query (optional, defaults to popular artists)

**Response** (JSON):
```json
{
  "artists": [
    {
      "id": 123,
      "name": "Artist Name",
      "image_url": "https://..."
    }
  ]
}
```

**Features**:
- Returns up to 30 unique artists
- Empty query returns popular artists
- 1-2 character queries search popular artists starting with that letter
- Filters results by query relevance

**Error Responses**:
- `500`: Search failed

---

### `GET /api/artist-albums`
**Function**: `get_artist_albums()`  
**Description**: Get albums for an artist from Spotify API  

**Query Parameters**:
- `artist_id`: Genius artist ID (optional)
- `artist_name`: Artist name (optional)
- At least one parameter required

**Response** (JSON):
```json
{
  "albums": [
    {
      "id": "spotify_album_id",
      "name": "Album Name",
      "type": "album",
      "release_date": "2023-01-01",
      "total_tracks": 12,
      "image_url": "https://..."
    }
  ]
}
```

**Features**:
- Filters albums to show only those with >5 tracks (excludes singles)
- Adds "All Songs" option at index 0
- Adds "Singles & EPs" option if singles exist
- Cached for 7 days (168 hours)
- Sorts albums by release date (newest first)

**Error Responses**:
- `400`: Missing required parameters
- Returns fallback "All Songs" option on error

---

### `GET /api/album-songs`
**Function**: `get_album_songs()`  
**Description**: Get songs from a specific album or collection  

**Query Parameters**:
- `artist_id`: Genius artist ID
- `album_id`: Spotify album ID, 'all', or 'singles'
- `artist_name`: Artist name

**Response** (JSON):
```json
{
  "songs": [
    {
      "id": 123456,
      "title": "Song Title",
      "artist": "Artist Name",
      "track_number": 1  // Only for specific albums
    }
  ]
}
```

**Modes**:
1. **`album_id == 'all'`**: Returns up to 150 songs from Genius sorted by popularity
2. **`album_id == 'singles'`**: Returns all songs from singles/EPs
3. **Specific album ID**: Returns tracks from that Spotify album matched with Genius

**Features**:
- Matches Spotify tracks with Genius song IDs
- Removes duplicates
- Sorts by track number for specific albums
- Cached for 7 days (168 hours)
- Fetches up to 3 pages (150 songs) for "All Songs"

**Error Responses**:
- `400`: Missing required parameters
- `500`: Fetch failed

---

### `POST /api/translate-word`
**Function**: `translate_word()`  
**Description**: Translate individual words/phrases with context awareness  

**Request Body** (JSON):
```json
{
  "word": "palabra",
  "context": "Esta es una palabra",
  "target_language": "English"
}
```

**Response** (JSON):
```json
{
  "word": "palabra",
  "translation": "word",
  "context": "Esta es una palabra"
}
```

**Features**:
- Context-aware translation using GPT-4o-mini
- Single word → single word translation
- Short phrase → phrase translation
- Temperature: 0.3 (more deterministic)
- Max tokens: 50
- Cached for 30 days (720 hours)
- Cache key: `{word}_{context}_{language}`

**Error Responses**:
- `400`: Missing word or context
- `500`: Translation failed

---

### `GET /api/cache/stats`
**Function**: `cache_stats()`  
**Description**: Get cache statistics  

**Response** (JSON):
```json
{
  "lyrics": {
    "count": 42,
    "size_mb": 1.23
  },
  "translations": {
    "count": 100,
    "size_mb": 3.45
  },
  "words": {
    "count": 500,
    "size_mb": 0.89
  },
  "spotify": {
    "count": 30,
    "size_mb": 0.56
  }
}
```

**Parameters**: None

---

### `POST /api/cache/clear`
**Function**: `clear_cache()`  
**Description**: Clear all or specific cache types  

**Request Body** (JSON, optional):
```json
{
  "cache_type": "translation"  // Optional: lyrics, translation, word, spotify, or null for all
}
```

**Response** (JSON):
```json
{
  "success": true,
  "message": "Cache cleared: translation"
}
```

**Parameters**: None required (clears all if body is empty)

---

### `GET /api/health`
**Function**: `health()`  
**Description**: Health check endpoint  

**Response** (JSON):
```json
{
  "status": "ok"
}
```

**Parameters**: None

---

## Error Handling
- All endpoints include try-catch blocks
- Errors are logged to console
- Client receives JSON error responses with appropriate HTTP status codes
- Common status codes: 400 (Bad Request), 404 (Not Found), 500 (Internal Server Error)

## Main Execution
```python
if __name__ == '__main__':
    app.run(debug=True, port=5000)
```
- Runs Flask development server on port 5000
- Debug mode enabled for development
- Auto-reloads on code changes

## Cache TTL Summary
| Cache Type | TTL | Use Case |
|------------|-----|----------|
| Lyrics | 30 days | Song lyrics don't change |
| Translations | 30 days | Translations are static |
| Words | 30 days | Word translations are static |
| Spotify | 7 days | Album data may update |

## API Flow Examples

### Example 1: Translate a Song
1. Client searches artist → `/api/search-artists?q=drake`
2. Client selects artist, fetches albums → `/api/artist-albums?artist_id=123`
3. Client selects album, fetches songs → `/api/album-songs?artist_id=123&album_id=xyz`
4. Client translates song → `/api/translate` with song_id

### Example 2: Vocabulary Mode
1. User double-clicks a line
2. Frontend extracts words from the line
3. For each word → `/api/translate-word` in parallel
4. Display flashcards with word-level translations
