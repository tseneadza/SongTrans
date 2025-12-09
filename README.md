# SongTrans - AI-Powered Lyrics Translation App

An AI-driven application that fetches song lyrics and translates them on-the-fly, displaying original and translated lyrics side-by-side.

## Features

### Core Features
- 🎵 **Smart Song Search**: Cascading dropdowns with Artist → Album → Song selection
- 🔍 **Artist Autocomplete**: Real-time search with 30+ results from Genius
- 💿 **Spotify Integration**: Album artwork and track listings
- 🌍 **Multi-Language Translation**: Support for 10+ languages
- 📊 **Line-by-Line Display**: Synchronized scrolling between original and translated lyrics
- 🤖 **AI-Powered Translation**: Using OpenAI GPT-4o-mini

### User Experience
- 🎨 **Dark Mode**: Toggle between light and dark themes
- 🔤 **Font Size Control**: A-/A+ buttons for accessibility
- 📋 **Copy Buttons**: Copy original or translated lyrics with one click
- 🖱️ **Click-to-Highlight**: Click any line to highlight it and its translation
- 🎯 **Synchronized Scrolling**: Toggle to keep original and translated lyrics aligned
- 📱 **Responsive Design**: Works on desktop and mobile

### Vocabulary Learning
- 🎴 **Flashcard Mode**: Study vocabulary from selected lines
- 🧠 **Word-Level Translations**: Context-aware individual word translations
- 📚 **Spaced Repetition**: Smart algorithm shows known words less frequently
- 📊 **Progress Tracking**: See mastered, learning, and new words
- 💾 **Persistent Storage**: Vocabulary knowledge saved in browser

### Performance
- ⚡ **Intelligent Caching**: 30-day cache for lyrics and translations
- 🚀 **Fast Word Translations**: Parallel API calls for flashcards
- 💾 **Spotify Data Cache**: 7-day cache for album/song listings

## Setup

### 1. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Get API Keys

#### Genius API (for lyrics)
1. Go to https://genius.com/api-clients
2. Sign in or create an account
3. Click "New API Client"
4. Fill in the form (use any URL for the app website)
5. Copy your "Client Access Token"

#### OpenAI API (for translation)
1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (you won't see it again!)

#### Spotify API (for album data)
1. Go to https://developer.spotify.com/dashboard
2. Log in with your Spotify account
3. Click "Create an App"
4. Fill in the name and description
5. Copy your "Client ID" and "Client Secret"

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```
GENIUS_API_TOKEN=your_actual_genius_token
OPENAI_API_KEY=your_actual_openai_key
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
```

### 4. Run the App

```bash
python app.py
```

Open your browser to: http://localhost:5000

## Usage

### Basic Translation
1. Type an artist name in the search box (autocomplete will show suggestions)
2. Select an artist from the dropdown
3. Choose an album (or "All Songs")
4. Select a song from the album
5. Choose your target language
6. Click "Translate"
7. View the original and translated lyrics side-by-side!

### Vocabulary Learning Mode
1. After translating a song, click any line to highlight it
2. Click "🎴 Vocabulary Mode" button
3. Study individual words with their translations
4. Mark words as "I Know This" or "Still Learning"
5. The system remembers your progress and shows known words less often

### Tips
- Use dark mode toggle (🌙/☀️) for comfortable reading
- Adjust font size with A-/A+ buttons
- Copy lyrics with the copy button in each panel
- Toggle synchronized scrolling on/off as needed

## API Endpoint

You can also use the API directly:

```bash
curl -X POST http://localhost:5000/api/translate \
  -H "Content-Type: application/json" \
  -d '{
    "song_name": "Imagine",
    "artist_name": "John Lennon",
    "target_language": "Spanish"
  }'
```

## Technologies

- **Backend**: Flask (Python)
- **Lyrics**: Genius API via lyricsgenius (v3.3.1)
- **Album Data**: Spotify Web API via spotipy
- **Translation**: OpenAI GPT-4o-mini
- **Caching**: File-based JSON cache system
- **Frontend**: HTML, CSS, JavaScript (Vanilla)

## Cache Management

View cache statistics:
```bash
curl http://localhost:5000/api/cache/stats
```

Clear all cache:
```bash
curl -X POST http://localhost:5000/api/cache/clear \
  -H "Content-Type: application/json" \
  -d '{}'
```

Clear specific cache type:
```bash
curl -X POST http://localhost:5000/api/cache/clear \
  -H "Content-Type: application/json" \
  -d '{"cache_type": "translation"}'
```

Cache types: `lyrics`, `translation`, `word`, `spotify`

## Notes

- The app respects copyright by only displaying lyrics for educational/personal use
- Translation quality may vary depending on the complexity of the lyrics
- API costs apply for OpenAI usage (approximately $0.0001-0.0005 per song translation)
- Vocabulary knowledge is stored in browser localStorage
- Cache files are stored in the `cache/` directory (automatically created)

## TODO - Planned Features

### High Priority
- [ ] **Export Vocabulary**: Export learned words to CSV/Anki format
- [ ] **Phrase Detection**: Identify and translate common phrases (not just individual words)
- [ ] **Audio Sync**: Integrate with Spotify/YouTube for audio playback with lyrics
- [ ] **Lyrics Highlighting**: Highlight current word/line during audio playback

### Medium Priority
- [ ] **User Accounts**: Save vocabulary progress across devices
- [ ] **Custom Vocabulary Lists**: Create themed word lists from multiple songs
- [ ] **Quiz Mode**: Test vocabulary knowledge with multiple choice/fill-in-the-blank
- [ ] **Pronunciation Guide**: Add phonetic pronunciations or audio for words
- [ ] **Translation Notes**: Add cultural context or idiom explanations
- [ ] **Batch Translation**: Queue multiple songs for translation
- [ ] **Playlist Support**: Import and translate entire Spotify playlists

### Low Priority
- [ ] **Keyboard Shortcuts**: Navigate flashcards with arrow keys, space to flip
- [ ] **Alternative Translations**: Show multiple translation options for ambiguous words
- [ ] **Grammar Tips**: Explain grammar structures found in lyrics
- [ ] **Share Feature**: Share translated lyrics or vocabulary lists
- [ ] **Offline Mode**: Download translations for offline study
- [ ] **Statistics Dashboard**: Visualize learning progress over time
- [ ] **Collaborative Learning**: Share and compare vocabulary with friends
- [ ] **Theme Customization**: Custom color schemes beyond light/dark

### Performance Enhancements
- [ ] **Pre-load Translations**: Translate all lines in background after initial load
- [ ] **Database Backend**: Replace file cache with SQLite or PostgreSQL
- [ ] **Redis Caching**: Add Redis layer for faster cache access
- [ ] **Batch API Calls**: Translate multiple words in a single API call
- [ ] **Progressive Loading**: Show partial results while translation continues

### Technical Improvements
- [ ] **Testing**: Add unit tests and integration tests
- [ ] **Error Handling**: Better error messages and retry logic
- [ ] **Logging**: Structured logging for debugging
- [ ] **Rate Limiting**: Add rate limiting to API endpoints
- [ ] **API Documentation**: Generate OpenAPI/Swagger docs
- [ ] **Docker Support**: Containerize the application
- [ ] **CI/CD Pipeline**: Automated testing and deployment
