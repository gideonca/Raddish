import unittest
from src.expiring_store import ExpiringStore
from src.command_handler import CommandHandler

class TestCommandHandler(unittest.TestCase):
    def setUp(self):
        self.store = ExpiringStore()
        self.handler = CommandHandler(self.store)
        self.responses = []
        
    def send_response(self, response: bytes):
        self.responses.append(response.decode('utf-8'))
        
    def test_ping(self):
        self.handler.handle_command(['PING'], self.send_response)
        self.assertEqual(self.responses[-1], 'PONG\n')
        
    def test_echo(self):
        self.handler.handle_command(['ECHO', 'hello', 'world'], self.send_response)
        self.assertEqual(self.responses[-1], 'hello world\n')
        
    def test_set_get(self):
        # Test SET
        self.handler.handle_command(['SET', 'mykey', 'myvalue'], self.send_response)
        self.assertEqual(self.responses[-1], 'OK\n')
        
        # Test GET
        self.handler.handle_command(['GET', 'mykey'], self.send_response)
        self.assertEqual(self.responses[-1], 'myvalue\n')
        
    def test_del(self):
        # Set a value first
        self.handler.handle_command(['SET', 'mykey', 'myvalue'], self.send_response)
        
        # Delete it
        self.handler.handle_command(['DEL', 'mykey'], self.send_response)
        self.assertEqual(self.responses[-1], 'OK\n')
        
        # Try to get deleted key
        self.handler.handle_command(['GET', 'mykey'], self.send_response)
        self.assertEqual(self.responses[-1], 'NULL\n')
        
    def test_expire(self):
        # Set a value
        self.handler.handle_command(['SET', 'mykey', 'myvalue'], self.send_response)
        
        # Set expiration
        self.handler.handle_command(['EXPIRE', 'mykey', '1'], self.send_response)
        self.assertEqual(self.responses[-1], 'OK\n')
        
    def test_invalid_command(self):
        self.handler.handle_command(['INVALID'], self.send_response)
        self.assertTrue('ERROR' in self.responses[-1])
        
    def test_exit_command(self):
        result = self.handler.handle_command(['EXIT'], self.send_response)
        self.assertEqual(self.responses[-1], 'Goodbye!\n')
        self.assertFalse(result)  # Should return False to close connection

if __name__ == '__main__':
    unittest.main()
