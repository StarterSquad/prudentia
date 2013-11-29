import json
import unittest
from src.base import Environment, Box

class TestEnvironment(unittest.TestCase):

    def setUp(self):
        self.env = Environment('.', 'test1')

    def test_add(self):
        b = Box('name', 'dev.yml', '0.0.0.0', None)
        self.env.addBox(b)
        self.assertEqual(json.load(open('./test1', 'r'))[0]['name'], b.name)

    def test_remove(self):
        self.env.remBox('name')
        self.assertEqual(json.load(open('./test1', 'r')), [])

if __name__ == '__main__':
    unittest.main()