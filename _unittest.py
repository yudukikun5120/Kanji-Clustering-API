import unittest
from clustering import get_affinities

class TestOutput(unittest.TestCase):

    def test_affinities(self):
        characters = ["蟻", "宕", "曜"]
        
        for char in characters:
            affinities = get_affinities(char)
            print(char, affinities)


if __name__ == '__main__':
    unittest.main()