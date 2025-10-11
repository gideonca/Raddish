import unittest
import time
from src.expiring_store import ExpiringStore

class TestExpiringStore(unittest.TestCase):
    def setUp(self):
        self.store = ExpiringStore()

    def tearDown(self):
        self.store.stop()

    def test_basic_set_get(self):
        """Test basic set and get operations without expiration"""
        self.store.set('key1', 'value1')
        self.assertEqual(self.store.get('key1'), 'value1')

    def test_missing_key(self):
        """Test getting a non-existent key returns default value"""
        self.assertIsNone(self.store.get('nonexistent'))
        self.assertEqual(self.store.get('nonexistent', 'default'), 'default')

    def test_expiration(self):
        """Test key expiration"""
        self.store.set('key2', 'value2', ttl=0.1)
        self.assertEqual(self.store.get('key2'), 'value2')
        time.sleep(0.2)  # Wait for expiration
        self.assertIsNone(self.store.get('key2'))

    def test_contains(self):
        """Test __contains__ method"""
        self.store.set('key3', 'value3')
        self.assertTrue('key3' in self.store)
        self.assertFalse('nonexistent' in self.store)

    def test_update_expiry(self):
        """Test updating expiry time of existing key"""
        self.store.set('key4', 'value4', ttl=0.2)
        time.sleep(0.1)
        self.store.set('key4', 'value4', ttl=0.3)  # Reset expiry
        time.sleep(0.2)  # Original expiry would have passed
        self.assertEqual(self.store.get('key4'), 'value4')

    def test_cleanup(self):
        """Test manual cleanup of expired keys"""
        self.store.set('key5', 'value5', ttl=0.1)
        self.store.set('key6', 'value6', ttl=0.1)
        time.sleep(0.2)
        self.store.cleanup()
        self.assertIsNone(self.store.get('key5'))
        self.assertIsNone(self.store.get('key6'))

    def test_auto_cleanup(self):
        """Test automatic cleanup of expired keys"""
        self.store = ExpiringStore(cleanup_interval=0.1)
        self.store.set('key7', 'value7', ttl=0.1)
        time.sleep(0.3)  # Wait for auto cleanup
        self.assertIsNone(self.store.get('key7'))

    def test_default_ttl(self):
        """Test default TTL functionality"""
        store = ExpiringStore(default_ttl=0.1)
        store.set('key8', 'value8')  # Use default TTL
        self.assertEqual(store.get('key8'), 'value8')
        time.sleep(0.2)
        self.assertIsNone(store.get('key8'))
        store.stop()

if __name__ == '__main__':
    unittest.main()