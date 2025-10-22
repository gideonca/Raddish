import unittest
from src.validation_handler import ValidationHandler

class TestValidationHandler(unittest.TestCase):
    def setUp(self):
        self.handler = ValidationHandler()

    def test_empty_command(self):
        is_valid, error = self.handler.validate_command([])
        self.assertFalse(is_valid)
        self.assertEqual(error, 'Empty command')

    def test_unknown_command(self):
        is_valid, error = self.handler.validate_command(['UNKNOWN'])
        self.assertFalse(is_valid)
        self.assertTrue('Unknown command' in error)

    def test_ping_command(self):
        is_valid, error = self.handler.validate_command(['PING'])
        self.assertTrue(is_valid)
        self.assertEqual(error, '')

    def test_set_command(self):
        # Valid SET
        is_valid, error = self.handler.validate_command(['SET', 'key', 'value'])
        self.assertTrue(is_valid)
        self.assertEqual(error, '')

        # Invalid SET (too few args)
        is_valid, error = self.handler.validate_command(['SET', 'key'])
        self.assertFalse(is_valid)
        self.assertTrue('Too few arguments' in error)

    def test_expire_command(self):
        # Valid EXPIRE
        is_valid, error = self.handler.validate_command(['EXPIRE', 'key', '10'])
        self.assertTrue(is_valid)
        self.assertEqual(error, '')

        # Invalid EXPIRE (non-integer TTL)
        is_valid, error = self.handler.validate_command(['EXPIRE', 'key', 'notanumber'])
        self.assertFalse(is_valid)
        self.assertTrue('must be a number' in error)

    def test_custom_command(self):
        # Add a custom command
        self.handler.register_command(
            'CUSTOM',
            min_args=2,
            max_args=3,
            usage='CUSTOM key [value]',
            types=[str, str, str]
        )

        # Test valid custom command
        is_valid, error = self.handler.validate_command(['CUSTOM', 'key', 'value'])
        self.assertTrue(is_valid)
        self.assertEqual(error, '')

    def test_command_usage(self):
        # Test existing command
        usage = self.handler.get_command_usage('SET')
        self.assertEqual(usage, 'SET key value')

        # Test unknown command
        usage = self.handler.get_command_usage('UNKNOWN')
        self.assertTrue('Unknown command' in usage)

    def test_list_commands(self):
        commands = self.handler.list_commands()
        self.assertIsInstance(commands, list)
        self.assertIn('SET', commands)
        self.assertIn('GET', commands)
        self.assertIn('PING', commands)

if __name__ == '__main__':
    unittest.main()