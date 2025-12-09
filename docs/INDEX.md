# SongTrans Documentation Index

## Overview
Complete documentation for the SongTrans AI-Powered Lyrics Translation application.

---

## Python Backend Files

### 1. [app.py](./app.py.md)
**Main Flask application** - RESTful API server

**Key Components**:
- 9 API endpoints (translate, search, albums, songs, cache)
- Request handling and routing
- Service integration and orchestration
- Error handling and validation

**Endpoints**:
- `GET /` - Serve web interface
- `POST /api/translate` - Translate song lyrics
- `GET /api/search-artists` - Search artists (autocomplete)
- `GET /api/artist-albums` - Get artist albums from Spotify
- `GET /api/album-songs` - Get songs from album
- `POST /api/translate-word` - Translate individual words
- `GET /api/cache/stats` - Cache statistics
- `POST /api/cache/clear` - Clear cache
- `GET /api/health` - Health check

---

### 2. [lyrics_service.py](./lyrics_service.py.md)
**Lyrics fetching service** - Genius API integration

**Class**: `LyricsService`

**Methods**:
- `__init__()` - Initialize Genius API client
- `fetch_lyrics(song_name, artist_name)` - Fetch lyrics from Genius

**Features**:
- Artist-specific search for accuracy
- Section header removal
- Error handling and logging

---

### 3. [translation_service.py](./translation_service.py.md)
**Translation service** - OpenAI GPT-4o-mini integration

**Class**: `TranslationService`

**Methods**:
- `__init__()` - Initialize OpenAI client
- `translate_lyrics(lyrics, target_language, source_language)` - Translate lyrics

**Features**:
- Line-by-line structure preservation
- 7 strict translation rules
- Low temperature (0.3) for consistency
- Context-aware translations

---

### 4. [spotify_service.py](./spotify_service.py.md)
**Spotify data service** - Spotify API integration

**Class**: `SpotifyService`

**Methods**:
- `__init__()` - Initialize Spotify client (Client Credentials flow)
- `search_artist(artist_name)` - Search for artist
- `get_artist_albums(spotify_artist_id)` - Get all albums
- `get_album_tracks(spotify_album_id)` - Get album tracks

**Features**:
- Album/single differentiation
- Duplicate removal
- Sorted by release date
- Pagination handling

---

### 5. [cache_service.py](./cache_service.py.md)
**Caching service** - File-based caching system

**Class**: `CacheService`

**Methods**:
- `__init__(cache_dir)` - Initialize cache directories
- `get(cache_type, *key_parts, ttl_hours)` - Retrieve cached data
- `set(cache_type, data, *key_parts)` - Store data in cache
- `clear(cache_type)` - Clear cache files
- `get_cache_stats()` - Get cache statistics

**Cache Types**:
- Lyrics (30-day TTL)
- Translations (30-day TTL)
- Words (30-day TTL)
- Spotify (7-day TTL)

---

## Frontend Files

### templates/index.html
**Single-page web application** - Complete UI and client logic

**Major Sections**:
1. **HTML Structure** (~600 lines)
   - Header with controls (dark mode, font size)
   - Search form (artist, album, song, language)
   - Lyrics display (side-by-side columns)
   - Vocabulary mode (flashcard interface)
   - Metadata display

2. **CSS Styling** (~550 lines)
   - Dark/light theme support
   - Responsive grid layout
   - Flashcard animations
   - Dropdown styling
   - Custom scrollbars

3. **JavaScript Logic** (~900 lines)
   - Artist search with autocomplete
   - Cascading dropdowns (artist → album → song)
   - Lyrics translation and display
   - Line highlighting and sync scrolling
   - Vocabulary flashcard system
   - Spaced repetition algorithm
   - localStorage persistence

**Key JavaScript Functions**:

#### Search & Selection
- `searchArtists(query)` - Search Genius for artists
- `displayArtistDropdown(artists)` - Show autocomplete results
- `selectArtist(artist)` - Handle artist selection
- `populateAlbumDropdown(albums)` - Fill album dropdown
- `populateSongDropdown(songs)` - Fill song dropdown

#### Translation & Display
- `cleanLyrics(lyrics)` - Remove Genius metadata
- `displayLyrics(original, translated)` - Show side-by-side
- `displayMetadata()` - Show song info card
- `highlightLine(lineNumber)` - Highlight corresponding lines
- `setupSyncScrolling()` - Synchronized scrolling

#### Vocabulary Mode
- `VocabKnowledge` class - localStorage-based word tracking
  - `markAsKnown(word, lang)` - Record known word
  - `markAsLearning(word, lang)` - Record learning word
  - `shouldShowWord(word, lang)` - Spaced repetition logic
  - `getStats()` - Get vocabulary statistics

- `extractVocabularyFromLine(lineNumber)` - Extract words from line
- `enterVocabModeForLine(lineNumber)` - Start flashcards for line
- `toggleVocabMode()` - Enter/exit vocabulary mode
- `showCard(index)` - Display current flashcard
- `showLineSummary()` - Show complete line translation
- `flipCard()` - Toggle flashcard front/back
- `markCard(status)` - Mark word as known/learning
- `nextCard()` - Advance to next card
- `moveToNextLine()` - Auto-advance to next lyrics line

#### Utilities
- `toggleDarkMode()` - Switch light/dark theme
- `adjustFontSize(change)` - Increase/decrease font
- `copyLyrics(elementId)` - Copy lyrics to clipboard

---

## Data Flow

### 1. Song Translation Flow
```
User Input → Artist Search → Select Artist → 
Get Albums → Select Album → Get Songs → 
Select Song → Translate → Display Lyrics
```

### 2. Vocabulary Learning Flow
```
Double-click Line → Extract Words → 
Translate Each Word (parallel) → Show Flashcards → 
Mark Known/Learning → Update Knowledge → 
Show Line Summary → Next Line
```

### 3. Caching Flow
```
API Request → Check Cache → 
  If Hit: Return Cached Data
  If Miss: Fetch from API → Cache → Return Data
```

---

## Technology Stack

### Backend
- **Flask 3.0.0** - Web framework
- **OpenAI 1.3.0** - GPT-4o-mini for translations
- **lyricsgenius 3.3.1** - Genius API client
- **spotipy 2.25.2** - Spotify API client
- **flask-cors 4.0.0** - CORS support

### Frontend
- **Vanilla JavaScript** - No frameworks
- **CSS Variables** - Theme system
- **LocalStorage** - Vocabulary persistence
- **Fetch API** - HTTP requests

### Data Storage
- **File-based JSON cache** - Organized by type
- **Browser localStorage** - User vocabulary data

---

## Configuration

### Environment Variables (.env)
```bash
GENIUS_API_TOKEN=your_genius_token
OPENAI_API_KEY=your_openai_key
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
```

### Cache Configuration
- Root directory: `./cache/`
- Subdirectories: lyrics, translations, words, spotify
- TTL: 7-30 days depending on type

---

## API Rate Limits

### Genius API
- ~1000 requests/hour
- No published hard limits
- Use caching to minimize calls

### OpenAI API
- gpt-4o-mini: 10,000 requests/minute (tier-dependent)
- ~$0.0001-0.0005 per song translation
- **Important**: Rate limiting can occur with rapid word translations

### Spotify API
- Client Credentials: ~100 requests/minute
- Token auto-refreshes
- Caching essential for performance

---

## Key Features Documented

### Core Features
✅ Smart song search (artist → album → song)  
✅ Multi-language translation (10+ languages)  
✅ Line-by-line synchronized display  
✅ Click/double-click line highlighting  

### User Experience
✅ Dark mode with localStorage persistence  
✅ Font size controls  
✅ Copy lyrics buttons  
✅ Synchronized scrolling toggle  
✅ Responsive design  

### Vocabulary Learning
✅ Flashcard mode with spaced repetition  
✅ Word-level context-aware translations  
✅ Progress tracking (mastered/learning/new)  
✅ Line summary after completing words  
✅ Auto-advance to next line  
✅ Skip known words (level >= 3)  

### Performance
✅ Intelligent caching (4 types)  
✅ Parallel word translations  
✅ Album filtering (>5 tracks)  
✅ Singles/EPs grouping  

---

## File Organization

```
SongTrans/
├── app.py                    # Main Flask app
├── lyrics_service.py         # Genius API
├── translation_service.py    # OpenAI translation
├── spotify_service.py        # Spotify API
├── cache_service.py          # Caching system
├── templates/
│   └── index.html           # Frontend SPA
├── docs/                     # This documentation
│   ├── INDEX.md             # This file
│   ├── app.py.md
│   ├── lyrics_service.py.md
│   ├── translation_service.py.md
│   ├── spotify_service.py.md
│   └── cache_service.py.md
├── cache/                    # Cache storage (git-ignored)
│   ├── lyrics/
│   ├── translations/
│   ├── words/
│   └── spotify/
├── .env                      # API keys (git-ignored)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Development Workflow

### 1. Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add API keys
```

### 2. Run
```bash
python app.py  # http://localhost:5000
```

### 3. Test Features
- Search artist
- Select album/song
- Translate lyrics
- Try vocabulary mode
- Check cache stats

---

## Maintenance Tasks

### Clear Cache
```bash
curl -X POST http://localhost:5000/api/cache/clear \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Check Cache Stats
```bash
curl http://localhost:5000/api/cache/stats
```

### Monitor Disk Usage
```bash
du -sh cache/
```

---

## Future Enhancements
See [README.md](../README.md#todo---planned-features) for complete list of planned features.

---

## Support

### Debugging
- Check Flask console for errors
- Browser console for frontend issues
- Verify API keys in .env
- Clear cache if data seems stale

### Common Issues
1. **Translation fails**: Check OpenAI API key and credits
2. **No albums shown**: Check Spotify credentials
3. **Slow flashcards**: OpenAI rate limiting - wait or upgrade tier
4. **Cache growing large**: Run cache clear periodically

---

## Version History
- **v1.0** - Initial release with basic translation
- **v1.1** - Added vocabulary mode
- **v1.2** - Added caching system
- **v1.3** - Added Spotify integration
- **v1.4** - Added spaced repetition and line summaries
- **v1.5** - Added double-click vocabulary entry

**Last Updated**: December 3, 2024
