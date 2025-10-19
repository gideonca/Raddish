"""
Tests for the cache handler implementation.
"""
import unittest
import time
from src.cache_handler import CacheHandler

class TestCacheHandler(unittest.TestCase):
    def setUp(self):
        self.cache_handler = CacheHandler(default_ttl=10)  # 10 second default TTL
        
    def test_create_and_delete_cache(self):
        # Test cache creation
        self.assertTrue(self.cache_handler.create_cache("users"))
        self.assertFalse(self.cache_handler.create_cache("users"))  # Already exists
        
        # Test cache deletion
        self.assertTrue(self.cache_handler.delete_cache("users"))
        self.assertFalse(self.cache_handler.delete_cache("users"))  # Already deleted
        
    def test_set_and_get_simple_values(self):
        # Test setting and getting string values
        self.cache_handler.set("users", "user1", "John Doe")
        self.assertEqual(self.cache_handler.get("users", "user1"), "John Doe")
        
        # Test default value for missing key
        self.assertEqual(self.cache_handler.get("users", "missing", "default"), "default")
        
    def test_nested_dictionary_storage(self):
        # Test storing nested dictionary structures
        user_data = {
            "name": "John Doe",
            "age": 30,
            "preferences": {
                "theme": "dark",
                "notifications": True
            }
        }
        
        self.cache_handler.set("users", "user1", user_data)
        retrieved = self.cache_handler.get("users", "user1")
        
        self.assertEqual(retrieved, user_data)
        self.assertEqual(retrieved["preferences"]["theme"], "dark")
        
    def test_json_like_structures(self):
        # Test storing complex nested structures
        data = {
            "users": [
                {
                    "id": 1,
                    "name": "John",
                    "active": True,
                    "scores": [10, 20, 30]
                },
                {
                    "id": 2,
                    "name": "Jane",
                    "active": False,
                    "scores": [15, 25, 35]
                }
            ],
            "metadata": {
                "version": "1.0",
                "updated": "2025-10-19"
            }
        }
        
        # Store in cache named "app_data"
        self.cache_handler.set("app_data", "current_state", data)
        
        # Retrieve and verify
        retrieved = self.cache_handler.get("app_data", "current_state")
        self.assertEqual(retrieved["users"][0]["name"], "John")
        self.assertEqual(retrieved["users"][1]["scores"], [15, 25, 35])
        self.assertEqual(retrieved["metadata"]["version"], "1.0")
        
    def test_cache_expiration(self):
        # Create cache with 1 second TTL
        self.cache_handler.set("temp", "key1", "value1", ttl=1)
        
        # Verify value exists
        self.assertEqual(self.cache_handler.get("temp", "key1"), "value1")
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Value should be gone
        self.assertIsNone(self.cache_handler.get("temp", "key1"))
        
    def test_cache_operations(self):
        # Test various cache operations
        self.cache_handler.set("cache1", "key1", "value1")
        self.cache_handler.set("cache1", "key2", "value2")
        
        # Test cache size
        self.assertEqual(self.cache_handler.get_cache_size("cache1"), 2)
        
        # Test key deletion
        self.assertTrue(self.cache_handler.delete("cache1", "key1"))
        self.assertEqual(self.cache_handler.get_cache_size("cache1"), 1)
        
        # Test cache clearing
        self.assertTrue(self.cache_handler.clear_cache("cache1"))
        self.assertEqual(self.cache_handler.get_cache_size("cache1"), 0)
        
    def test_multiple_caches(self):
        # Test managing multiple caches
        self.cache_handler.set("users", "u1", {"name": "John"})
        self.cache_handler.set("products", "p1", {"name": "Widget"})
        
        caches = self.cache_handler.list_caches()
        self.assertIn("users", caches)
        self.assertIn("products", caches)
        
        # Verify isolation between caches
        self.assertIsNotNone(self.cache_handler.get("users", "u1"))
        self.assertIsNone(self.cache_handler.get("users", "p1"))
        
if __name__ == '__main__':
    unittest.main()