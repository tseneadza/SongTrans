from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from lyrics_service import LyricsService
from translation_service import TranslationService
from spotify_service import SpotifyService
from cache_service import CacheService

app = Flask(__name__)
CORS(app)

lyrics_service = LyricsService()
translation_service = TranslationService()
spotify_service = SpotifyService()
cache_service = CacheService()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/translate', methods=['POST'])
def translate_song():
    """
    API endpoint to fetch and translate song lyrics.
    
    Expected JSON:
    {
        "song_id": 123456 (optional, preferred),
        "song_name": "Song Title" (fallback),
        "artist_name": "Artist Name (optional)",
        "target_language": "English (optional, default: English)"
    }
    """
    data = request.json
    
    if not data:
        return jsonify({'error': 'Request body is required'}), 400
    
    target_language = data.get('target_language', 'English')
    
    # Try to fetch by song_id first (more reliable)
    song_id = data.get('song_id')
    if song_id:
        import requests
        import os
        
        token = os.getenv('GENIUS_API_TOKEN')
        headers = {'Authorization': f'Bearer {token}'}
        
        try:
            # Get song details
            response = requests.get(
                f'https://api.genius.com/songs/{song_id}',
                headers=headers
            )
            song_data = response.json()['response']['song']
            
            # Fetch lyrics using lyricsgenius
            song_name = song_data['title']
            artist_name = song_data['primary_artist']['name']
            lyrics_data = lyrics_service.fetch_lyrics(song_name, artist_name)
        except Exception as e:
            print(f"Error fetching song by ID: {e}")
            return jsonify({'error': 'Failed to fetch song'}), 500
    else:
        # Fallback to name-based search
        song_name = data.get('song_name')
        artist_name = data.get('artist_name')
        
        if not song_name:
            return jsonify({'error': 'song_id or song_name is required'}), 400
        
        lyrics_data = lyrics_service.fetch_lyrics(song_name, artist_name)
    
    # Check cache for lyrics first
    cache_key_lyrics = f"{song_id or song_name}_{artist_name or ''}"
    cached_lyrics = cache_service.get('lyrics', cache_key_lyrics, ttl_hours=720)  # 30 days
    
    if cached_lyrics:
        lyrics_data = cached_lyrics
    else:
        if not lyrics_data:
            return jsonify({'error': 'Song not found or lyrics unavailable'}), 404
        # Cache the lyrics
        cache_service.set('lyrics', lyrics_data, cache_key_lyrics)
    
    # Check if original_only mode
    if target_language == 'original_only':
        return jsonify({
            'title': lyrics_data['title'],
            'artist': lyrics_data['artist'],
            'original_lyrics': lyrics_data['lyrics'],
            'translated_lyrics': lyrics_data['lyrics'],
            'target_language': 'Original'
        })
    
    # Check cache for translation
    cache_key_translation = f"{song_id or song_name}_{artist_name or ''}_{target_language}"
    cached_translation = cache_service.get('translation', cache_key_translation, ttl_hours=720)  # 30 days
    
    if cached_translation:
        translation_data = cached_translation
    else:
        # Translate lyrics
        translation_data = translation_service.translate_lyrics(
            lyrics_data['lyrics'],
            target_language=target_language
        )
        
        if not translation_data:
            return jsonify({'error': 'Translation failed'}), 500
        
        # Cache the translation
        cache_service.set('translation', translation_data, cache_key_translation)
    
    # Return both original and translated
    return jsonify({
        'title': lyrics_data['title'],
        'artist': lyrics_data['artist'],
        'original_lyrics': lyrics_data['lyrics'],
        'translated_lyrics': translation_data['translated'],
        'target_language': target_language
    })


@app.route('/api/search-artists', methods=['GET'])
def search_artists():
    """
    Search for artists by name (autocomplete)
    Query param: q=artist_name
    """
    query = request.args.get('q', '').strip()
    
    import requests
    import os
    
    token = os.getenv('GENIUS_API_TOKEN')
    headers = {'Authorization': f'Bearer {token}'}
    
    # If query is empty or very short, show popular artists
    if len(query) < 1:
        popular_artists = [
            'Drake', 'Taylor Swift', 'Bad Bunny', 'The Weeknd', 'Ariana Grande',
            'Kanye West', 'Beyoncé', 'Eminem', 'Rihanna', 'Ed Sheeran',
            'Post Malone', 'Billie Eilish', 'Travis Scott', 'J. Cole', 'Kendrick Lamar',
            'SZA', 'Justin Bieber', 'Bruno Mars', 'Doja Cat', 'Lil Baby'
        ]
        query = popular_artists[0]  # Use first popular artist as default search
    
    try:
        # Fetch more results and extract unique artists
        artists_dict = {}
        
        # Make multiple searches with different variations if needed
        search_queries = [query]
        
        # If query is very short (1-2 chars), search for multiple popular artists starting with it
        if len(query) <= 2:
            popular_starting = ['Drake', 'Doja Cat', 'DaBaby', 'Dua Lipa', 'DMX'] if query.lower().startswith('d') else []
            if popular_starting:
                search_queries = popular_starting[:5]
        
        for search_query in search_queries:
            response = requests.get(
                f'https://api.genius.com/search?q={search_query}&per_page=20',
                headers=headers
            )
            data = response.json()
            
            # Extract unique artists from search results
            for hit in data['response']['hits']:
                artist = hit['result']['primary_artist']
                if artist['id'] not in artists_dict:
                    artists_dict[artist['id']] = {
                        'id': artist['id'],
                        'name': artist['name'],
                        'image_url': artist.get('image_url')
                    }
                
                # Stop if we have enough unique artists
                if len(artists_dict) >= 50:
                    break
            
            if len(artists_dict) >= 50:
                break
        
        # Filter results to match the original query if it's specific enough
        if len(query) >= 2:
            filtered_artists = [
                artist for artist in artists_dict.values()
                if query.lower() in artist['name'].lower()
            ]
            # If filtering gives us results, use those; otherwise use all
            if filtered_artists:
                return jsonify({'artists': filtered_artists[:30]})
        
        return jsonify({'artists': list(artists_dict.values())[:30]})
    except Exception as e:
        print(f"Error searching artists: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/artist-albums', methods=['GET'])
def get_artist_albums():
    """
    Get albums for an artist using Spotify API
    Query param: artist_id=123 (Genius ID), artist_name=Artist Name
    """
    artist_id = request.args.get('artist_id')
    artist_name = request.args.get('artist_name')
    
    if not artist_id and not artist_name:
        return jsonify({'error': 'artist_id or artist_name is required'}), 400
    
    import requests
    import os
    
    try:
        # Check cache first
        cache_key = f"albums_{artist_id}_{artist_name}"
        cached_albums = cache_service.get('spotify', cache_key, ttl_hours=168)  # 7 days
        
        if cached_albums:
            return jsonify({'albums': cached_albums})
        
        # Get artist name from Genius if only ID provided
        if not artist_name:
            token = os.getenv('GENIUS_API_TOKEN')
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(
                f'https://api.genius.com/artists/{artist_id}',
                headers=headers
            )
            artist_data = response.json()['response']['artist']
            artist_name = artist_data['name']
        
        # Search for artist on Spotify
        spotify_artist = spotify_service.search_artist(artist_name)
        
        if not spotify_artist:
            return jsonify({'albums': [{'name': 'All Songs', 'id': 'all', 'total_tracks': 0}]})
        
        # Get albums from Spotify
        all_albums = spotify_service.get_artist_albums(spotify_artist['id'])
        
        # Filter to only show albums with more than 5 tracks (exclude singles/EPs)
        albums = [album for album in all_albums if album.get('total_tracks', 0) > 5]
        
        # Add "All Songs" option at the beginning
        albums.insert(0, {
            'name': 'All Songs',
            'id': 'all',
            'type': 'all',
            'total_tracks': 0
        })
        
        # Add "Singles & EPs" option if there are filtered items
        filtered_out = [album for album in all_albums if album.get('total_tracks', 0) <= 5]
        if filtered_out:
            albums.insert(1, {
                'name': 'Singles & EPs',
                'id': 'singles',
                'type': 'compilation',
                'total_tracks': sum(album.get('total_tracks', 0) for album in filtered_out)
            })
        
        # Cache both the albums list and the singles/EPs list
        cache_service.set('spotify', albums, cache_key)
        if filtered_out:
            singles_cache_key = f"singles_{artist_id}_{artist_name}"
            cache_service.set('spotify', filtered_out, singles_cache_key)
        
        return jsonify({'albums': albums})
    except Exception as e:
        print(f"Error fetching albums: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'albums': [{'name': 'All Songs', 'id': 'all', 'total_tracks': 0}]})


@app.route('/api/album-songs', methods=['GET'])
def get_album_songs():
    """
    Get songs for a specific album using Spotify tracks matched with Genius IDs
    Query params: artist_id=123, album_id=spotify_album_id or 'all', artist_name=Artist
    """
    artist_id = request.args.get('artist_id')
    album_id = request.args.get('album_id')
    artist_name = request.args.get('artist_name')
    
    if not artist_id and not artist_name:
        return jsonify({'error': 'artist_id or artist_name is required'}), 400
    
    import requests
    import os
    
    token = os.getenv('GENIUS_API_TOKEN')
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        # Check cache first
        cache_key = f"songs_{artist_id}_{album_id}"
        cached_songs = cache_service.get('spotify', cache_key, ttl_hours=168)  # 7 days
        
        if cached_songs:
            return jsonify({'songs': cached_songs})
        
        # If album_id is 'singles', get songs from all singles and EPs
        if album_id == 'singles':
            singles_cache_key = f"singles_{artist_id}_{artist_name}"
            filtered_albums = cache_service.get('spotify', singles_cache_key, ttl_hours=168)
            
            if not filtered_albums:
                # Fallback to all songs if singles cache not found
                album_id = 'all'
            else:
                # Get tracks from all singles/EPs
                all_tracks = []
                for single_album in filtered_albums:
                    spotify_tracks = spotify_service.get_album_tracks(single_album['id'])
                    if spotify_tracks:
                        for track in spotify_tracks:
                            track_name = track['name']
                            track_artist = track['artists'][0] if track['artists'] else artist_name
                            
                            # Search for song on Genius
                            search_query = f"{track_name} {track_artist}"
                            try:
                                response = requests.get(
                                    f'https://api.genius.com/search?q={search_query}',
                                    headers=headers
                                )
                                data = response.json()
                                
                                if data['response']['hits']:
                                    hit = data['response']['hits'][0]['result']
                                    all_tracks.append({
                                        'id': hit['id'],
                                        'title': hit['title'],
                                        'artist': hit['primary_artist']['name']
                                    })
                            except:
                                continue
                
                # Remove duplicates based on song ID
                seen_ids = set()
                unique_tracks = []
                for track in all_tracks:
                    if track['id'] not in seen_ids:
                        seen_ids.add(track['id'])
                        unique_tracks.append(track)
                
                # Cache the result
                cache_service.set('spotify', unique_tracks, cache_key)
                
                return jsonify({'songs': unique_tracks})
        
        # If album_id is 'all', return all artist songs from Genius
        if album_id == 'all' or not album_id:
            all_songs = []
            page = 1
            per_page = 50
            
            # Fetch up to 150 songs
            while page <= 3:
                response = requests.get(
                    f'https://api.genius.com/artists/{artist_id}/songs?per_page={per_page}&page={page}&sort=popularity',
                    headers=headers
                )
                data = response.json()
                songs = data['response']['songs']
                
                if not songs:
                    break
                
                for song in songs:
                    all_songs.append({
                        'id': song['id'],
                        'title': song['title'],
                        'artist': song['primary_artist']['name']
                    })
                
                if len(songs) < per_page:
                    break
                page += 1
            
            # Cache the result
            cache_service.set('spotify', all_songs, cache_key)
            
            return jsonify({'songs': all_songs})
        
        # Get tracks from Spotify album
        spotify_tracks = spotify_service.get_album_tracks(album_id)
        
        if not spotify_tracks:
            return jsonify({'songs': []})
        
        # Match Spotify tracks with Genius songs
        matched_songs = []
        for track in spotify_tracks:
            track_name = track['name']
            track_artist = track['artists'][0] if track['artists'] else artist_name
            
            # Search for song on Genius
            search_query = f"{track_name} {track_artist}"
            try:
                response = requests.get(
                    f'https://api.genius.com/search?q={search_query}',
                    headers=headers
                )
                data = response.json()
                
                if data['response']['hits']:
                    # Get the first matching result
                    hit = data['response']['hits'][0]['result']
                    matched_songs.append({
                        'id': hit['id'],
                        'title': hit['title'],
                        'artist': hit['primary_artist']['name'],
                        'track_number': track['track_number']
                    })
            except:
                # If search fails, skip this track
                continue
        
        # Sort by track number
        matched_songs.sort(key=lambda x: x.get('track_number', 999))
        
        # Cache the result
        cache_service.set('spotify', matched_songs, cache_key)
        
        return jsonify({'songs': matched_songs})
    except Exception as e:
        print(f"Error fetching album songs: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/translate-word', methods=['POST'])
def translate_word():
    """
    API endpoint to translate a word or phrase with context.
    
    Expected JSON:
    {
        "word": "palabra",
        "context": "Esta es una palabra",
        "target_language": "English"
    }
    """
    data = request.json
    
    if not data or 'word' not in data or 'context' not in data:
        return jsonify({'error': 'word and context are required'}), 400
    
    word = data['word']
    context = data['context']
    target_language = data.get('target_language', 'English')
    
    # Check cache first
    cache_key = f"{word}_{context}_{target_language}"
    cached_translation = cache_service.get('word', cache_key, ttl_hours=720)  # 30 days
    
    if cached_translation:
        return jsonify(cached_translation)
    
    # Use OpenAI to translate the word with context
    from openai import OpenAI
    import os
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    try:
        prompt = f"""Translate ONLY the word or phrase "{word}" from the following sentence to {target_language}.

Sentence: "{context}"

Provide ONLY the translation of "{word}" - nothing else. Consider the context but translate only that specific word/phrase.

If it's a single word, give a single word translation.
If it's a short phrase (2-3 words), give the phrase translation.
Do not include explanations, examples, or the original word."""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a precise translator. You only provide the translation requested, nothing more."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=50
        )
        
        translation = response.choices[0].message.content.strip()
        
        # Clean up common formatting issues
        translation = translation.strip('"\'.,')
        
        result = {
            'word': word,
            'translation': translation,
            'context': context
        }
        
        # Cache the result
        cache_service.set('word', result, cache_key)
        
        return jsonify(result)
    except Exception as e:
        print(f"Error translating word: {e}")
        return jsonify({'error': 'Translation failed'}), 500


@app.route('/api/cache/stats', methods=['GET'])
def cache_stats():
    """
    Get cache statistics.
    """
    stats = cache_service.get_cache_stats()
    return jsonify(stats)


@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """
    Clear cache.
    
    Expected JSON (optional):
    {
        "cache_type": "lyrics" | "translation" | "word" | "spotify" | null (all)
    }
    """
    data = request.json or {}
    cache_type = data.get('cache_type')
    
    cache_service.clear(cache_type)
    
    return jsonify({
        'success': True,
        'message': f'Cache cleared: {cache_type or "all"}'
    })


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
