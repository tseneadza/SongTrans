import os
import requests
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv

load_dotenv()


class LyricsService:
    def __init__(self):
        api_token = os.getenv('GENIUS_API_TOKEN')
        if not api_token:
            raise ValueError("GENIUS_API_TOKEN not found in environment variables")
        
        self.api_token = api_token
        self.headers = {'Authorization': f'Bearer {api_token}'}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def fetch_lyrics(self, song_name, artist_name=None):
        """
        Fetch lyrics for a given song and optional artist.
        
        Returns:
            dict: {'title': str, 'artist': str, 'lyrics': str} or None if not found
        """
        try:
            # Step 1: Search for the song using Genius API
            search_query = f"{song_name} {artist_name}" if artist_name else song_name
            search_url = f"https://api.genius.com/search?q={search_query}"
            
            response = requests.get(search_url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            hits = data.get('response', {}).get('hits', [])
            
            if not hits:
                print(f"No results found for: {search_query}")
                return None
            
            # Get the first result
            song_info = hits[0]['result']
            song_url = song_info['url']
            title = song_info['title']
            artist = song_info['primary_artist']['name']
            
            # Step 2: Scrape lyrics from the song page
            lyrics = self._scrape_lyrics(song_url)
            
            if lyrics:
                return {
                    'title': title,
                    'artist': artist,
                    'lyrics': lyrics
                }
            
            return None
            
        except Exception as e:
            print(f"Error fetching lyrics: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _scrape_lyrics(self, url):
        """
        Scrape lyrics from a Genius song page.
        
        Args:
            url: Genius song URL
            
        Returns:
            str: Lyrics text or None
        """
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find lyrics containers (Genius uses different div structures)
            lyrics_divs = soup.find_all('div', attrs={'data-lyrics-container': 'true'})
            
            if not lyrics_divs:
                # Try alternative selectors
                lyrics_divs = soup.find_all('div', class_=re.compile(r'Lyrics__Container'))
            
            if not lyrics_divs:
                print(f"Could not find lyrics on page: {url}")
                return None
            
            # Extract text from all lyrics divs
            lyrics_parts = []
            for div in lyrics_divs:
                # Get text while preserving line breaks
                for br in div.find_all('br'):
                    br.replace_with('\n')
                lyrics_parts.append(div.get_text())
            
            lyrics = '\n'.join(lyrics_parts).strip()
            
            # Clean up the lyrics
            lyrics = self._clean_lyrics(lyrics)
            
            return lyrics if lyrics else None
            
        except Exception as e:
            print(f"Error scraping lyrics from {url}: {e}")
            return None
    
    def _clean_lyrics(self, lyrics):
        """
        Clean up scraped lyrics text.
        
        Args:
            lyrics: Raw lyrics text
            
        Returns:
            str: Cleaned lyrics
        """
        # Remove Genius header junk (Contributors, Translations, etc.)
        lyrics = re.sub(r'^.*?Lyrics', '', lyrics, flags=re.DOTALL)
        
        # Remove description text that appears before actual lyrics
        lyrics = re.sub(r'^".*?".*?(?=\n[A-Z])', '', lyrics, flags=re.DOTALL)
        
        # Remove [Verse 1], [Chorus], etc. annotations
        lyrics = re.sub(r'\[.*?\]', '', lyrics)
        
        # Remove "You might also like" text that sometimes appears
        lyrics = re.sub(r'You might also like.*?\n', '', lyrics, flags=re.IGNORECASE)
        
        # Remove embed text
        lyrics = re.sub(r'\d+Embed$', '', lyrics, flags=re.MULTILINE)
        
        # Remove "See [Artist] Live" text
        lyrics = re.sub(r'See.*?Live.*?\n', '', lyrics, flags=re.IGNORECASE)
        
        # Remove extra whitespace while preserving intentional line breaks
        lines = [line.strip() for line in lyrics.split('\n')]
        lyrics = '\n'.join(lines)
        
        # Remove multiple consecutive blank lines
        lyrics = re.sub(r'\n{3,}', '\n\n', lyrics)
        
        return lyrics.strip()
