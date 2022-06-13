import unittest
from clustering import *


class TestOutput(unittest.TestCase):

    def test_store_estimator(self):
        store_estimator()

    def test_affinities(self):
        characters = ["蟻", "宕", "曜"]

        for char in characters:
            affinities = get_affinities(char)
            print(char, affinities)


if __name__ == '__main__':
    unittest.main()
