from fastapi import FastAPI
from affinities_detection import get_affinities

app = FastAPI()


@app.get("/affinities/{set}")
def affinities(character: str, set: str):
    affinities = get_affinities(character, set)
    affinities = list(affinities)

    return {
        "character": character,
        "affinities": affinities,
    }
