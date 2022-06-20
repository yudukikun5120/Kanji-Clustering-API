from fastapi import FastAPI
from affinities_detection import get_affinities

app = FastAPI()


@app.get("/affinities")
def affinities(character: str, sets: str = 'jis_level_1'):
    affinities = [
        affinity
        for set in sets.split()
        for affinity in get_affinities(character, set)
        ]

    return {
        "character": character,
        "affinities": affinities,
    }
