import os
import json
from typing import Optional
from pathlib import Path

class SessionManager:
    """Manages session state and caching for topic-based runs."""
    
    def __init__(self, topic: str, base_dir: str = "sessions"):
        self.topic = topic
        # Sanitize topic name for folder
        self.session_name = "".join(c if c.isalnum() or c in (' ', '_') else '_' for c in topic)
        self.session_name = self.session_name.replace(' ', '_').lower()
        
        self.session_dir = Path(base_dir) / self.session_name
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        self.cache_file = self.session_dir / "cache.json"
        self.cache = self._load_cache()
    
    def _load_cache(self) -> dict:
        """Load existing cache if available."""
        if self.cache_file.exists():
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_cache(self):
        """Save cache to disk."""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, indent=2, ensure_ascii=False)
    
    def get_cached(self, key: str) -> Optional[dict]:
        """Get cached data for a key."""
        return self.cache.get(key)
    
    def set_cached(self, key: str, value: dict):
        """Cache data for a key."""
        self.cache[key] = value
        self._save_cache()
    
    def has_cached(self, key: str) -> bool:
        """Check if key exists in cache."""
        return key in self.cache
    
    def get_path(self, *parts) -> Path:
        """Get a path within the session directory."""
        return self.session_dir / Path(*parts)
    
    def clear_cache(self):
        """Clear all cached data."""
        self.cache = {}
        self._save_cache()
