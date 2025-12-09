import json
import os
import hashlib
from datetime import datetime, timedelta
from pathlib import Path


class CacheService:
    """Simple file-based caching service for API responses and translations."""
    
    def __init__(self, cache_dir='cache'):
        """Initialize cache service with a directory for cache files."""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for different cache types
        self.lyrics_cache = self.cache_dir / 'lyrics'
        self.translations_cache = self.cache_dir / 'translations'
        self.words_cache = self.cache_dir / 'words'
        self.spotify_cache = self.cache_dir / 'spotify'
        
        for subdir in [self.lyrics_cache, self.translations_cache, self.words_cache, self.spotify_cache]:
            subdir.mkdir(exist_ok=True)
    
    def _get_cache_key(self, *args):
        """Generate a cache key from arguments."""
        key_string = '|'.join(str(arg) for arg in args)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cache_file(self, cache_type, cache_key):
        """Get the path to a cache file."""
        if cache_type == 'lyrics':
            return self.lyrics_cache / f'{cache_key}.json'
        elif cache_type == 'translation':
            return self.translations_cache / f'{cache_key}.json'
        elif cache_type == 'word':
            return self.words_cache / f'{cache_key}.json'
        elif cache_type == 'spotify':
            return self.spotify_cache / f'{cache_key}.json'
        else:
            return self.cache_dir / f'{cache_key}.json'
    
    def get(self, cache_type, *key_parts, ttl_hours=None):
        """
        Get cached data.
        
        Args:
            cache_type: Type of cache (lyrics, translation, word, spotify)
            key_parts: Parts to form the cache key
            ttl_hours: Time-to-live in hours (None = never expire)
            
        Returns:
            Cached data or None if not found/expired
        """
        cache_key = self._get_cache_key(*key_parts)
        cache_file = self._get_cache_file(cache_type, cache_key)
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check expiration if TTL is set
            if ttl_hours is not None:
                cached_time = datetime.fromisoformat(cache_data['timestamp'])
                expiration_time = cached_time + timedelta(hours=ttl_hours)
                
                if datetime.now() > expiration_time:
                    # Cache expired
                    cache_file.unlink()
                    return None
            
            return cache_data['data']
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error reading cache: {e}")
            # Delete corrupted cache file
            cache_file.unlink()
            return None
    
    def set(self, cache_type, data, *key_parts):
        """
        Set cached data.
        
        Args:
            cache_type: Type of cache (lyrics, translation, word, spotify)
            data: Data to cache
            key_parts: Parts to form the cache key
        """
        cache_key = self._get_cache_key(*key_parts)
        cache_file = self._get_cache_file(cache_type, cache_key)
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error writing cache: {e}")
    
    def clear(self, cache_type=None):
        """
        Clear cache files.
        
        Args:
            cache_type: Type of cache to clear (None = clear all)
        """
        if cache_type is None:
            # Clear all cache
            for subdir in [self.lyrics_cache, self.translations_cache, self.words_cache, self.spotify_cache]:
                for cache_file in subdir.glob('*.json'):
                    cache_file.unlink()
        else:
            # Clear specific cache type
            cache_dir = self._get_cache_file(cache_type, '').parent
            for cache_file in cache_dir.glob('*.json'):
                cache_file.unlink()
    
    def get_cache_stats(self):
        """Get statistics about cache usage."""
        stats = {}
        for cache_type, cache_dir in [
            ('lyrics', self.lyrics_cache),
            ('translations', self.translations_cache),
            ('words', self.words_cache),
            ('spotify', self.spotify_cache)
        ]:
            files = list(cache_dir.glob('*.json'))
            total_size = sum(f.stat().st_size for f in files)
            stats[cache_type] = {
                'count': len(files),
                'size_mb': round(total_size / (1024 * 1024), 2)
            }
        
        return stats
