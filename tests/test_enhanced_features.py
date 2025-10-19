"""
Tests for the enhanced cache handler features including
pattern matching, events, and compression.
"""
import unittest
import time
import os
import tempfile
import shutil
import gzip
from src.cache_handler import CacheHandler, CacheEvent, CacheEventContext

class TestEnhancedFeatures(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.cache_handler = CacheHandler(
            default_ttl=10,
            persistence_dir=self.temp_dir,
            compress_persistence=True
        )
        self.events_received = []
        
    def tearDown(self):
        self.cache_handler.stop()
        shutil.rmtree(self.temp_dir)
        
    def test_pattern_search(self):
        # Add test data
        self.cache_handler.set("users", "user_1", {"name": "John"})
        self.cache_handler.set("users", "user_2", {"name": "Jane"})
        self.cache_handler.set("users", "admin_1", {"name": "Admin"})
        
        # Test glob pattern
        user_matches = list(self.cache_handler.search_by_pattern("users", "user_*"))
        self.assertEqual(len(user_matches), 2)
        self.assertTrue(all(k.startswith("user_") for k, _ in user_matches))
        
        # Test regex pattern
        admin_matches = list(self.cache_handler.search_by_pattern(
            "users", "^admin_\\d+$", regex=True))
        self.assertEqual(len(admin_matches), 1)
        self.assertEqual(admin_matches[0][0], "admin_1")
        
    def test_json_path_search(self):
        # Add nested test data
        self.cache_handler.set("users", "user1", {
            "profile": {
                "name": "John",
                "settings": {"theme": "dark"}
            }
        })
        self.cache_handler.set("users", "user2", {
            "profile": {
                "name": "Jane",
                "settings": {"theme": "light"}
            }
        })
        
        # Search by JSON path
        dark_theme = list(self.cache_handler.search_json_path(
            "users", "profile.settings.theme"))
        self.assertEqual(len(dark_theme), 2)
        
        # Search with wildcard
        names = list(self.cache_handler.search_json_path(
            "users", "profile.*.theme"))
        self.assertEqual(len(names), 2)
        
    def test_event_handlers(self):
        def on_set(ctx: CacheEventContext):
            self.events_received.append(("set", ctx.cache_name, ctx.key, ctx.value))
            
        def on_get(ctx: CacheEventContext):
            self.events_received.append(("get", ctx.cache_name, ctx.key))
            
        # Register handlers
        self.cache_handler.on(CacheEvent.SET, on_set)
        self.cache_handler.on(CacheEvent.GET, on_get)
        
        # Perform operations
        self.cache_handler.set("test", "key1", "value1")
        self.cache_handler.get("test", "key1")
        
        # Verify events
        self.assertEqual(len(self.events_received), 2)
        self.assertEqual(self.events_received[0], ("set", "test", "key1", "value1"))
        self.assertEqual(self.events_received[1], ("get", "test", "key1"))
        
    def test_compression(self):
        # Add large data to test compression
        large_data = {
            "numbers": list(range(1000)),
            "text": "test" * 1000
        }
        self.cache_handler.set("large_cache", "key1", large_data)
        
        # Force persist
        self.cache_handler.persist("large_cache")
        
        # Check that compressed file exists
        gz_path = os.path.join(self.temp_dir, "large_cache.json.gz")
        self.assertTrue(os.path.exists(gz_path))
        
        # Verify it's actually compressed
        with gzip.open(gz_path, 'rb') as f:
            content = f.read()
            self.assertTrue(len(content) < len(str(large_data)))
            
        # Load in new handler and verify data
        new_handler = CacheHandler(
            persistence_dir=self.temp_dir,
            compress_persistence=True
        )
        loaded_data = new_handler.get("large_cache", "key1")
        self.assertEqual(loaded_data["numbers"], list(range(1000)))
        new_handler.stop()

if __name__ == '__main__':
    unittest.main()