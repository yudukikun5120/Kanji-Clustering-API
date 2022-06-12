import unittest
from main import predict_label

class TestOutput(unittest.TestCase):

    def test_affinities(self):
        characters = ["蟻", "宕", "曜"]
        
        for char in characters:
            affinities = predict_label(char)
            print(char, affinities)


if __name__ == '__main__':
    unittest.main()