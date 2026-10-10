# Copyright (c) 2026 yudukikun5120

"""FastAPI application for Kanji clustering and affinity detection."""

from typing import TYPE_CHECKING, Annotated, cast

import uvicorn
from fastapi import FastAPI, Query

from .affinities_detection import get_affinities

if TYPE_CHECKING:
    from .kanji_types import KanjiSet

app = FastAPI()


@app.get("/affinities")
def affinities(
    character: Annotated[str, Query(min_length=1, max_length=1)],
    sets: str = "jis_level_1",
) -> dict[str, str | list[str]]:
    r"""You can get affinities corresponding to your input character.

    \r<sets\r>::= jis_level_1 | jis_level_2 | \r<sets\r> \r<sets\r>
    """
    # dict.fromkeys deduplicates while preserving order. Without this, a
    # client can repeat the same set name many times in one request and
    # force get_affinities (an uncached pickle load + model inference) to
    # run once per repetition, multiplying the cost of a single request.
    valid_kanji_sets = dict.fromkeys(
        kanji_set_str
        for kanji_set_str in sets.split()
        if kanji_set_str in {"jis_level_1", "jis_level_2"}
    )

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
