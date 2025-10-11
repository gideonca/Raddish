import unittest
from src.validator import CommandValidator, COMMAND_SPECS

class TestCommandValidator(unittest.TestCase):
    def setUp(self):
        self.validator = CommandValidator()

    def test_empty_command(self):
        is_valid, error = self.validator.validate([])
        self.assertFalse(is_valid)
        self.assertEqual(error, 'Empty command')

    def test_unknown_command(self):
        is_valid, error = self.validator.validate(['UNKNOWN'])
        self.assertFalse(is_valid)
        self.assertTrue('Unknown command' in error)

    def test_ping_command(self):
        is_valid, error = self.validator.validate(['PING'])
        self.assertTrue(is_valid)
        self.assertEqual(error, '')

    def test_set_command(self):
        # Valid SET
        is_valid, error = self.validator.validate(['SET', 'key', 'value'])
        self.assertTrue(is_valid)
        self.assertEqual(error, '')

        # Invalid SET (too few args)
        is_valid, error = self.validator.validate(['SET', 'key'])
        self.assertFalse(is_valid)
        self.assertTrue('Too few arguments' in error)

    def test_expire_command(self):
        # Valid EXPIRE
        is_valid, error = self.validator.validate(['EXPIRE', 'key', '10'])
        self.assertTrue(is_valid)
        self.assertEqual(error, '')

        # Invalid EXPIRE (non-integer TTL)
        is_valid, error = self.validator.validate(['EXPIRE', 'key', 'notanumber'])
        self.assertFalse(is_valid)
        self.assertTrue('must be a number' in error)

    def test_custom_command(self):
        # Add a custom command
        self.validator.register_command(
            'CUSTOM',
            min_args=2,
            max_args=3,
            usage='CUSTOM key [value]',
            types=[str, str, str]
        )

        # Test valid custom command
        is_valid, error = self.validator.validate(['CUSTOM', 'key', 'value'])
        self.assertTrue(is_valid)
        self.assertEqual(error, '')

if __name__ == '__main__':
    unittest.main()
