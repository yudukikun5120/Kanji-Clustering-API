import unittest
from clustering import kanji_group
from affinities_detection import *


class TestOutput(unittest.TestCase):
    
    def test_kanji_jis_daiichisuijun(self):
        self.assertEqual(len(kanji_group('jis_level_1')), 2965)


    def test_store_estimator(self):
        store_estimator()


    def test_affinities(self):
        characters = ["蟻", "宕", "曜"]

        for char in characters:
            affinities = get_affinities(char)
            print(char, affinities)


if __name__ == '__main__':
    unittest.main()
