"""FastAPI application for Kanji clustering and affinity detection."""

from typing import TYPE_CHECKING, cast

import uvicorn
from fastapi import FastAPI

from affinities_detection import get_affinities

if TYPE_CHECKING:
    from kanji_types import KanjiSet

app = FastAPI()


@app.get("/affinities")
def affinities(
    character: str,
    sets: str = "jis_level_1",
) -> dict[str, str | list[float]]:
    r"""You can get affinities corresponding to your input character.

    \r<sets\r>::= jis_level_1 | jis_level_2 | \r<sets\r> \r<sets\r>
    """
    valid_kanji_sets = [
        kanji_set_str
        for kanji_set_str in sets.split()
        if kanji_set_str in {"jis_level_1", "jis_level_2"}
    ]

    affinities_ = [
        affinity
        for kanji_set_str in valid_kanji_sets
        for affinity in get_affinities(character, cast("KanjiSet", kanji_set_str))
    ]

    return {
        "character": character,
        "affinities": affinities_,
    }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
