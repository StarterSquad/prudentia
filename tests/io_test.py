import unittest

from prudentia.utils import io


class TestIO(unittest.TestCase):
    def test_xstr(self):
        self.assertEqual(io.xstr(None), '')

    def test_yes(self):
        self.assertTrue(io.input_yes_no('test topic', prompt_fn=lambda (m): 'y'))
        self.assertTrue(io.input_yes_no('test topic', prompt_fn=lambda (m): 'yes'))

    def test_no(self):
        self.assertFalse(io.input_yes_no('test topic', prompt_fn=lambda (m): 'whatever'))
        self.assertFalse(io.input_yes_no('test topic', prompt_fn=lambda (m): 'no'))
        self.assertFalse(io.input_yes_no('test topic', prompt_fn=lambda (m): ''))

    def test_mandatory_input(self):
        self.assertRaises(ValueError, io.input_value, 'mandatory topic', prompt_fn=lambda (m): '')

    def test_int_input(self):
        self.assertEqual(io.input_value('int topic', default_value=1, prompt_fn=lambda (m): '123'), 123)
        self.assertRaises(ValueError, io.input_value, 'int topic', default_value=1, prompt_fn=lambda (m): 'aaa')

    def test_value_hidden(self):
        pwd = 'this is a strong pwd'
        self.assertEqual(io.input_value('pwd', hidden=True, hidden_prompt_fn=lambda (m): pwd), pwd)

    def test_path_file(self):
        f = "./dev.yml"
        self.assertIsNotNone(io.input_path('cwd file', prompt_fn=lambda (m): f))
