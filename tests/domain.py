import json
import unittest
from src.domain import Environment, Box

class TestEnvironment(unittest.TestCase):

    def setUp(self):
        self.env = Environment('./env')
        self.testBox = Box('name', 'dev.yml', '0.0.0.0')

    def test_add(self):
        self.env.add(self.testBox)
        self.assertEqual(json.load(open('./env/.boxes', 'r'))[0]['name'], self.testBox.name)

    def test_remove(self):
        self.env.remove(self.testBox)
        self.assertEqual(json.load(open('./env/.boxes', 'r')), [])

if __name__ == '__main__':
    unittest.main()