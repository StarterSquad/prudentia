import json
import unittest
from src.domain import Environment, Box


class TestEnvironment(unittest.TestCase):
    def setUp(self):
        self.env = Environment('./env')
        box = Box()
        box.set_name('box-name')
        box.set_playbook('dev.yml')
        box.set_ip('0.0.0.0')
        self.test_box = box

    def test_add(self):
        self.env.add(self.test_box)
        box = json.load(open('./env/.boxes', 'r'))[0]
        self.assertEqual(box['name'], self.test_box.name)
        self.assertFalse('pwd' in box)
        self.assertFalse('extra' in box)

    def test_remove(self):
        self.env.remove('box-name')
        self.assertEqual(json.load(open('./env/.boxes', 'r')), [])


if __name__ == '__main__':
    unittest.main()