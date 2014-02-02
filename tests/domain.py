import json
import unittest

from src.domain import Environment, Box


class TestEnvironment(unittest.TestCase):
    def setUp(self):
        self.env = Environment('./env')
        self.test_box = Box('box-name', 'dev.yml', '0.0.0.0')

    def test_add(self):
        self.env.add(self.test_box)
        box = json.load(open('./env/.boxes', 'r'))[0]
        self.assertEqual(box['name'], self.test_box.name)
        self.assertFalse('remote_user' in box)
        self.assertFalse('remote_pwd' in box)
        self.assertFalse('extra' in box)

    def test_add_existing_name(self):
        b2 = Box('box-name', 'dev2', '1.2.3.4')
        self.assertRaises(ValueError, self.env.add, b2)

    def test_get_valid_box(self):
        b = self.env.get('box-name')
        self.assertEqual(b.playbook, 'dev.yml')

    def test_get_not_valid_box(self):
        b = self.env.get('whatever')
        self.assertEqual(b, None)

    def test_remove(self):
        self.env.remove('box-name')
        self.assertEqual(json.load(open('./env/.boxes', 'r')), [])


if __name__ == '__main__':
    unittest.main()