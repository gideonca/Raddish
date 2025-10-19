"""
Tests for the enhanced cache handler implementation.
"""
import unittest
import time
import os
import tempfile
import shutil
from src.cache_handler import CacheHandler

class TestEnhancedCacheHandler(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.cache_handler = CacheHandler(
            default_ttl=10,
            persistence_dir=self.temp_dir,
            auto_persist_interval=0.1
        )
        
    def tearDown(self):
        self.cache_handler.stop()
        shutil.rmtree(self.temp_dir)
        
    def test_search_and_filter(self):
        # Add test data
        self.cache_handler.set("users", "user1", {
            "name": "John",
            "age": 30,
            "preferences": {"theme": "dark"}
        })
        self.cache_handler.set("users", "user2", {
            "name": "Jane",
            "age": 25,
            "preferences": {"theme": "light"}
        })
        
        # Test value pattern matching
        dark_theme_users = self.cache_handler.find_by_value("users", 
            {"preferences": {"theme": "dark"}})
        self.assertEqual(len(dark_theme_users), 1)
        self.assertEqual(dark_theme_users[0], "user1")
        
        # Test predicate search
        young_users = list(self.cache_handler.search("users",
            lambda _, v: v.get("age", 0) < 30))
        self.assertEqual(len(young_users), 1)
        self.assertEqual(young_users[0][1]["name"], "Jane")
        
    def test_statistics(self):
        # Create cache and perform operations
        self.cache_handler.create_cache("test_stats")
        self.cache_handler.set("test_stats", "key1", "value1")
        
        # Test hits and misses
        self.cache_handler.get("test_stats", "key1")  # Hit
        self.cache_handler.get("test_stats", "missing")  # Miss
        
        stats = self.cache_handler.get_stats("test_stats")
        self.assertEqual(stats.hits, 1)
        self.assertEqual(stats.misses, 1)
        self.assertEqual(stats.items, 1)
        
        # Test stat reset
        self.cache_handler.reset_stats("test_stats")
        stats = self.cache_handler.get_stats("test_stats")
        self.assertEqual(stats.hits, 0)
        self.assertEqual(stats.misses, 0)
        
    def test_persistence(self):
        # Add data and persist
        self.cache_handler.set("persist_test", "key1", {"data": "value1"})
        self.cache_handler.set("persist_test", "key2", {"data": "value2"})
        
        # Force persist
        self.assertTrue(self.cache_handler.persist("persist_test"))
        
        # Create new handler and load data
        new_handler = CacheHandler(persistence_dir=self.temp_dir)
        self.assertTrue(new_handler.load_persistent("persist_test"))
        
        # Verify data
        self.assertEqual(
            new_handler.get("persist_test", "key1")["data"],
            "value1"
        )
        
        # Clean up
        new_handler.stop()
        
    def test_complex_data_persistence(self):
        # Create complex nested structure
        data = {
            "users": [
                {"id": 1, "name": "John", "scores": [10, 20, 30]},
                {"id": 2, "name": "Jane", "scores": [15, 25, 35]}
            ],
            "metadata": {
                "version": "1.0",
                "timestamp": time.time()
            }
        }
        
        # Store and persist
        self.cache_handler.set("complex_data", "test_key", data)
        self.cache_handler.persist("complex_data")
        
        # Load in new handler
        new_handler = CacheHandler(persistence_dir=self.temp_dir)
        new_handler.load_persistent("complex_data")
        
        # Verify complex data
        loaded_data = new_handler.get("complex_data", "test_key")
        self.assertEqual(loaded_data["users"][0]["name"], "John")
        self.assertEqual(loaded_data["users"][1]["scores"], [15, 25, 35])
        self.assertEqual(loaded_data["metadata"]["version"], "1.0")
        
        # Clean up
        new_handler.stop()
        
    def test_auto_persistence(self):
        # Add data
        self.cache_handler.set("auto_persist", "key1", "value1")
        
        # Wait for auto-persist
        time.sleep(0.2)
        
        # Create new handler and verify data was saved
        new_handler = CacheHandler(persistence_dir=self.temp_dir)
        self.assertEqual(
            new_handler.get("auto_persist", "key1"),
            "value1"
        )
        
        # Clean up
        new_handler.stop()

if __name__ == '__main__':
    unittest.main()