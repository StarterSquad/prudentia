import json
import unittest
from src.domain import Environment, Box

class TestEnvironment(unittest.TestCase):

    def setUp(self):
        self.env = Environment('./env', NoExtra)
        box = Box()
        box.set_name('box-name')
        box.set_playbook('dev.yml')
        box.set_ip('0.0.0.0')
        box.set_extra(NoExtra())
        self.testBox = box

    def test_add(self):
        self.env.add(self.testBox)
        self.assertEqual(json.load(open('./env/.boxes', 'r'))[0]['name'], self.testBox.name)

    def test_remove(self):
        self.env.remove('box-name')
        self.assertEqual(json.load(open('./env/.boxes', 'r')), [])

class NoExtra:
    def toJson(self):
        return ''

    @staticmethod
    def fromJson(json):
        return NoExtra()


if __name__ == '__main__':
    unittest.main()