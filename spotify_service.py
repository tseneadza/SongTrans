import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv()


class SpotifyService:
    def __init__(self):
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            print("Warning: Spotify credentials not found. Album features will be limited.")
            self.sp = None
        else:
            auth_manager = SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
            self.sp = spotipy.Spotify(auth_manager=auth_manager)
    
    def search_artist(self, artist_name):
        """Search for an artist on Spotify"""
        if not self.sp:
            return None
        
        try:
            results = self.sp.search(q=f'artist:{artist_name}', type='artist', limit=1)
            if results['artists']['items']:
                return results['artists']['items'][0]
            return None
        except Exception as e:
            print(f"Error searching artist: {e}")
            return None
    
    def get_artist_albums(self, spotify_artist_id):
        """Get all albums for an artist"""
        if not self.sp:
            return []
        
        try:
            albums = []
            results = self.sp.artist_albums(
                spotify_artist_id,
                album_type='album,single',
                limit=50
            )
            
            while results:
                for album in results['items']:
                    # Avoid duplicates (same album in different markets)
                    if not any(a['name'] == album['name'] for a in albums):
                        albums.append({
                            'id': album['id'],
                            'name': album['name'],
                            'type': album['album_type'],
                            'release_date': album.get('release_date', ''),
                            'total_tracks': album.get('total_tracks', 0),
                            'image_url': album['images'][0]['url'] if album.get('images') else None
                        })
                
                # Get next page
                if results['next']:
                    results = self.sp.next(results)
                else:
                    break
            
            # Sort by release date (newest first)
            albums.sort(key=lambda x: x['release_date'], reverse=True)
            return albums
        except Exception as e:
            print(f"Error fetching albums: {e}")
            return []
    
    def get_album_tracks(self, spotify_album_id):
        """Get all tracks for an album"""
        if not self.sp:
            return []
        
        try:
            results = self.sp.album_tracks(spotify_album_id, limit=50)
            tracks = []
            
            for track in results['items']:
                tracks.append({
                    'name': track['name'],
                    'track_number': track['track_number'],
                    'duration_ms': track['duration_ms'],
                    'artists': [artist['name'] for artist in track['artists']]
                })
            
            return tracks
        except Exception as e:
            print(f"Error fetching album tracks: {e}")
            return []
