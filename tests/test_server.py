import unittest
import socket
import threading
import time
from server import start_server, handle_client_connection, validate_command
from src.expiration_manager import ExpiringDict

class TestRedisServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start server in a separate thread
        cls.server_thread = threading.Thread(target=start_server)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(0.1)  # Give server time to start

    def setUp(self):
        # Create a new client connection for each test
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(('127.0.0.1', 6379))

    def tearDown(self):
        # Clean up client connection
        self.client.close()

    def send_command(self, command):
        """Helper method to send command and receive response"""
        self.client.sendall(f"{command}\n".encode('utf-8'))
        return self.client.recv(1024).decode('utf-8').strip()

    def test_ping(self):
        """Test PING command"""
        response = self.send_command("PING")
        self.assertEqual(response, "PONG")

    def test_echo(self):
        """Test ECHO command"""
        response = self.send_command("ECHO hello world")
        self.assertEqual(response, "hello world")

    def test_set_get(self):
        """Test SET and GET commands"""
        self.send_command("SET key1 value1")
        response = self.send_command("GET key1")
        self.assertEqual(response, "value1")

    def test_get_nonexistent(self):
        """Test GET on non-existent key"""
        response = self.send_command("GET nonexistent")
        self.assertEqual(response, "NULL")

    def test_del_existing(self):
        """Test DEL command on existing key"""
        self.send_command("SET key2 value2")
        response = self.send_command("DEL key2")
        self.assertEqual(response, "OK")
        response = self.send_command("GET key2")
        self.assertEqual(response, "NULL")

    def test_del_nonexistent(self):
        """Test DEL command on non-existent key"""
        response = self.send_command("DEL nonexistent")
        self.assertEqual(response, "NULL")

    def test_expire(self):
        """Test EXPIRE command"""
        self.send_command("SET key3 value3")
        self.send_command("EXPIRE key3 1")
        self.assertEqual(self.send_command("GET key3"), "value3")
        time.sleep(1.1)  # Wait for expiration
        self.assertEqual(self.send_command("GET key3"), "NULL")

    def test_unknown_command(self):
        """Test unknown command handling"""
        response = self.send_command("UNKNOWN")
        self.assertEqual(response, "ERROR: Unknown command")

    def test_validate_command(self):
        """Test command validation"""
        self.assertTrue(validate_command(['PING']))
        self.assertTrue(validate_command(['SET', 'key', 'value']))
        self.assertTrue(validate_command(['GET', 'key']))
        self.assertFalse(validate_command(['SET']))  # Not enough arguments

if __name__ == '__main__':
    unittest.main()