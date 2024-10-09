import unittest
from clustering import store_estimator, kanji_group
from affinities_detection import get_affinities


class TestOutput(unittest.TestCase):
    def test_kanji_jis_daiichisuijun(self):
        self.assertEqual(len(kanji_group("jis_level_1")), 2965)

    def test_store_estimator(self):
        store_estimator("jis_level_1")
        store_estimator("jis_level_2")

    def test_affinities(self):
        characters = ["蟻", "宕", "曜", "鮎"]

        for char in characters:
            jis_1_affinities = get_affinities(char, "jis_level_1")
            jis_2_affinities = get_affinities(char, "jis_level_2")
            print(
                char,
                "JIS第１水準：",
                jis_1_affinities,
                "JIS第２水準：",
                jis_2_affinities,
                sep="\n",
            )


if __name__ == "__main__":
    unittest.main()
