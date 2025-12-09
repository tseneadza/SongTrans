# cache_service.py Documentation

## Overview
File-based caching service for storing API responses and translations with TTL (time-to-live) support and organized subdirectories.

## Dependencies
- **json**: JSON serialization/deserialization
- **os**: File system operations
- **hashlib**: MD5 hash generation for cache keys
- **datetime/timedelta**: Timestamp and expiration handling
- **pathlib.Path**: Modern file path handling

## Class: CacheService

### `__init__(self, cache_dir='cache')`
**Description**: Initialize cache service and create directory structure

**Parameters**:
- `cache_dir` (str, optional): Root cache directory name (default: 'cache')

**Directory Structure Created**:
```
cache/
├── lyrics/        # Song lyrics from Genius
├── translations/  # Full song translations
├── words/        # Individual word translations
└── spotify/      # Album and track data
```

**Process**:
1. Creates root cache directory if not exists
2. Creates 4 subdirectories for different cache types
3. All directories created with `exist_ok=True` (no error if exists)

**Example**:
```python
# Default location
cache = CacheService()  # Creates ./cache/

# Custom location
cache = CacheService(cache_dir='/tmp/songtrans_cache')
```

---

### `_get_cache_key(self, *args)`
**Description**: Generate MD5 hash cache key from arguments

**Parameters**:
- `*args`: Variable number of arguments to form cache key

**Returns**:
- `str`: 32-character MD5 hex digest

**Process**:
1. Join all arguments with '|' separator
2. Encode to bytes (UTF-8)
3. Generate MD5 hash
4. Return hex digest

**Examples**:
```python
key1 = cache._get_cache_key("drake", "hotline bling")
# Result: "a3f8d9e2..." (32 chars)

key2 = cache._get_cache_key("song_123", "artist_456", "Spanish")
# Result: "b7c1a4f3..." (32 chars)
```

**Why MD5?**:
- Fast hashing for cache keys
- Fixed length (32 chars) - good for filenames
- Collision risk negligible for this use case
- Not cryptographic (not for security)

---

### `_get_cache_file(self, cache_type, cache_key)`
**Description**: Get Path object for a cache file

**Parameters**:
- `cache_type` (str): Type of cache (lyrics, translation, word, spotify)
- `cache_key` (str): MD5 hash key

**Returns**:
- `Path`: Full path to cache file (.json extension)

**File Naming**:
```
cache/{cache_type}/{cache_key}.json
```

**Examples**:
```python
path = cache._get_cache_file('lyrics', 'abc123...')
# Returns: Path('cache/lyrics/abc123....json')

path = cache._get_cache_file('word', 'def456...')
# Returns: Path('cache/words/def456....json')
```

---

### `get(self, cache_type, *key_parts, ttl_hours=None)`
**Description**: Retrieve cached data with optional TTL check

**Parameters**:
- `cache_type` (str): Type of cache
- `*key_parts`: Variable args to form cache key
- `ttl_hours` (int, optional): Time-to-live in hours (None = never expire)

**Returns**:
- Data if found and not expired
- `None` if not found, expired, or corrupted

**Cache File Format**:
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "data": { ... }
}
```

**TTL Logic**:
```python
if ttl_hours is not None:
    if now > (cached_time + ttl_hours):
        # Delete expired cache
        return None
```

**Error Handling**:
- Catches JSON decode errors
- Deletes corrupted cache files
- Prints error to console
- Returns None

**Examples**:
```python
# No TTL (never expires)
lyrics = cache.get('lyrics', 'song_id', 'artist_name')

# With 24-hour TTL
translation = cache.get('translation', 'song_id', 'English', ttl_hours=24)

# Check if None
if lyrics is None:
    # Cache miss - fetch from API
```

---

### `set(self, cache_type, data, *key_parts)`
**Description**: Store data in cache with timestamp

**Parameters**:
- `cache_type` (str): Type of cache
- `data`: Data to cache (must be JSON-serializable)
- `*key_parts`: Variable args to form cache key

**Returns**: None

**Cache File Created**:
```json
{
  "timestamp": "2024-01-15T10:30:00.123456",
  "data": {
    "title": "Song Title",
    "lyrics": "..."
  }
}
```

**JSON Options**:
- `ensure_ascii=False`: Supports Unicode characters
- `indent=2`: Pretty-printed (human-readable)

**Error Handling**:
- Catches all exceptions
- Prints error message
- Does not raise (fails silently)

**Examples**:
```python
# Cache lyrics
lyrics_data = {'title': 'Song', 'artist': 'Artist', 'lyrics': '...'}
cache.set('lyrics', lyrics_data, 'song_id', 'artist_name')

# Cache translation
translation = {'translated': '...', 'source': 'Spanish'}
cache.set('translation', translation, 'song_id', 'English')

# Cache word
word_data = {'word': 'hola', 'translation': 'hello'}
cache.set('word', word_data, 'hola', 'context_text', 'English')
```

---

### `clear(self, cache_type=None)`
**Description**: Clear all or specific cache files

**Parameters**:
- `cache_type` (str, optional): Type to clear (None = clear all)

**Behavior**:
- `cache_type=None`: Deletes all .json files in all subdirectories
- `cache_type='lyrics'`: Deletes only lyrics cache
- Similar for other types

**Examples**:
```python
# Clear all cache
cache.clear()

# Clear only translations
cache.clear('translation')

# Clear only word translations
cache.clear('word')
```

**Use Cases**:
- Manual cache invalidation
- Clear after app update
- Free disk space
- Reset for testing

---

### `get_cache_stats(self)`
**Description**: Get statistics about cache usage

**Parameters**: None

**Returns**:
```python
{
    'lyrics': {
        'count': 42,      # Number of cached items
        'size_mb': 1.23   # Total size in megabytes
    },
    'translations': { ... },
    'words': { ... },
    'spotify': { ... }
}
```

**Calculation**:
- Counts all .json files in each subdirectory
- Sums file sizes using `stat().st_size`
- Converts bytes to MB (1024 * 1024)
- Rounds to 2 decimal places

**Example**:
```python
stats = cache.get_cache_stats()
print(f"Total lyrics cached: {stats['lyrics']['count']}")
print(f"Lyrics cache size: {stats['lyrics']['size_mb']} MB")

# Check if cache getting too large
total_mb = sum(s['size_mb'] for s in stats.values())
if total_mb > 100:
    print("Cache over 100MB - consider clearing")
```

---

## Cache Types

### 1. Lyrics Cache
- **Type**: `'lyrics'`
- **Key**: `song_id/name + artist_name`
- **TTL**: 30 days (720 hours)
- **Data**: Song title, artist, lyrics text

### 2. Translations Cache
- **Type**: `'translation'`
- **Key**: `song_id/name + artist_name + target_language`
- **TTL**: 30 days (720 hours)
- **Data**: Translated lyrics, source language

### 3. Words Cache
- **Type**: `'word'`
- **Key**: `word + context + target_language`
- **TTL**: 30 days (720 hours)
- **Data**: Word, translation, context

### 4. Spotify Cache
- **Type**: `'spotify'`
- **Key**: Various (albums, songs, singles lists)
- **TTL**: 7 days (168 hours)
- **Data**: Album metadata, track lists

---

## Cache Strategies

### Read-Through Caching (in app.py)
```python
# 1. Check cache
cached = cache_service.get('lyrics', song_id)

# 2. If miss, fetch from API
if not cached:
    cached = lyrics_service.fetch_lyrics(song, artist)
    cache_service.set('lyrics', cached, song_id)

# 3. Use cached data
return cached
```

### TTL Strategy
- **Long TTL (30 days)**: Static data (lyrics, translations)
- **Medium TTL (7 days)**: Semi-static (albums, tracks)
- **No TTL**: Rarely changes (could add for lyrics)

---

## Disk Usage

### Typical File Sizes
- Lyrics: ~5-10 KB
- Translation: ~5-10 KB
- Word: ~0.5 KB
- Spotify album: ~1-2 KB

### Estimation
```
100 songs cached:
- Lyrics: 1 MB
- Translations (2 languages each): 2 MB
- Words (20 words/song): 1 MB
- Spotify data: 0.5 MB
Total: ~4.5 MB
```

---

## Best Practices

### 1. Always Check for None
```python
lyrics = cache.get('lyrics', song_id)
if lyrics is None:
    # Handle cache miss
```

### 2. Use Appropriate TTL
```python
# Static data - long TTL
cache.get('lyrics', song_id, ttl_hours=720)

# Dynamic data - short TTL
cache.get('spotify', album_id, ttl_hours=24)
```

### 3. Monitor Cache Size
```python
stats = cache.get_cache_stats()
total = sum(s['size_mb'] for s in stats.values())
if total > 500:  # 500MB threshold
    cache.clear('words')  # Clear least important
```

### 4. Handle Errors Gracefully
```python
# Cache failures shouldn't break app
try:
    data = cache.get('lyrics', song_id)
except:
    data = None  # Fetch from API
```

---

## Maintenance

### Clear Old Cache
```python
# Clear all cache older than TTL
# (Automatic on next get() call)

# Or manually clear specific type
cache.clear('translations')
```

### Backup Important Cache
```bash
# Backup cache directory
cp -r cache/ cache_backup/

# Restore from backup
cp -r cache_backup/ cache/
```

### Cache Location
```python
# Find cache on disk
import os
cache_path = os.path.abspath('cache')
print(f"Cache location: {cache_path}")
```
