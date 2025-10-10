import unittest
from unittest.mock import Mock, patch, MagicMock
import socket
import time
from server import validate_command, handle_client_connection, store
from src.expiration_manager import ExpiringDict

class TestRPushCommand(unittest.TestCase):
    """Test suite for RPUSH command implementation"""

    def setUp(self):
        """Initialize test environment before each test"""
        self.store = ExpiringDict()
        # Create a MagicMock instead of Mock for the socket
        self.mock_socket = MagicMock(spec=socket.socket)
        # Configure the context manager methods
        self.mock_socket.__enter__.return_value = self.mock_socket
        self.mock_socket.__exit__.return_value = None
        
        self.store_patcher = patch('server.store', self.store)
        self.store_patcher.start()

    def tearDown(self):
        """Clean up test environment after each test"""
        self.store_patcher.stop()
        self.store.clear()

    def test_rpush_basic(self):
        """
        Test basic RPUSH functionality:
        - Should add key-value pair to store
        - Should return OK
        - Value should be retrievable
        """
        self.mock_socket.recv.side_effect = [b'RPUSH mykey myvalue\n', b'EXIT\n']
        handle_client_connection(self.mock_socket)
        
        self.mock_socket.sendall.assert_any_call(b'OK\n')
        self.assertEqual(self.store.get('mykey'), 'myvalue')

    def test_rpush_ordering(self):
        """
        Test RPUSH maintains correct ordering:
        - Most recent items should be at the front
        - Order should be preserved across multiple operations
        """
        commands = [
            b'RPUSH key1 value1\n',
            b'RPUSH key2 value2\n',
            b'RPUSH key3 value3\n',
            b'EXIT\n'
        ]
        self.mock_socket.recv.side_effect = commands
        handle_client_connection(self.mock_socket)

        keys = list(self.store.keys())
        self.assertEqual(len(keys), 3)
        self.assertEqual(keys[0], 'key3')  # Most recent first
        self.assertEqual(keys[1], 'key2')
        self.assertEqual(keys[2], 'key1')

    def test_rpush_ttl(self):
        """
        Test RPUSH with TTL:
        - Item should expire after TTL
        - Item should be accessible before expiry
        - Item should not be accessible after expiry
        """
        self.mock_socket.recv.side_effect = [b'RPUSH testkey testval\n', b'EXIT\n']
        handle_client_connection(self.mock_socket)

        self.assertTrue('testkey' in self.store)
        self.assertEqual(self.store.get('testkey'), 'testval')
        
        time.sleep(1.1)  # Wait for expiration
        self.assertFalse('testkey' in self.store)

    def test_rpush_zero_ttl(self):
        """
        Test RPUSH with zero TTL:
        - Should accept zero as valid TTL
        - Item should persist indefinitely
        """
        self.mock_socket.recv.side_effect = [b'RPUSH mykey myvalue 0\n', b'EXIT\n']
        handle_client_connection(self.mock_socket)

        self.assertTrue('mykey' in self.store)
        time.sleep(0.1)  # Small delay
        self.assertTrue('mykey' in self.store)

    def test_rpush_validation(self):
        """
        Test RPUSH command validation:
        - Should accept valid commands
        - Should reject invalid commands
        - Should validate number of arguments
        """
        valid_cases = [
            ['RPUSH', 'key', 'value', '100'],
            ['RPUSH', 'test-key', 'test-value', '0'],
        ]
        invalid_cases = [
            ['RPUSH'],
            ['RPUSH', 'key'],
            ['RPUSH', 'key', 'value'],
            ['RPUSH', 'key', 'value', 'invalid'],
        ]

        for case in valid_cases:
            self.assertTrue(validate_command(case))

        for case in invalid_cases:
            self.assertFalse(validate_command(case))

    def test_rpush_overwrite(self):
        """
        Test RPUSH overwrite behavior:
        - Should update existing keys
        - Should maintain order after update
        """
        commands = [
            b'RPUSH key1 value1 100\n',
            b'RPUSH key1 newvalue 100\n',
            b'EXIT\n'
        ]
        self.mock_socket.recv.side_effect = commands
        handle_client_connection(self.mock_socket)

        self.assertEqual(self.store.get('key1'), 'newvalue')
        self.assertEqual(len(list(self.store.keys())), 1)

if __name__ == '__main__':
    unittest.main()