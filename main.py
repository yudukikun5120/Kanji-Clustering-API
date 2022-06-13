from fastapi import FastAPI
from clustering import get_affinities

app = FastAPI()


@app.get("/affinities")
def affinities(character: str):
    affinities = get_affinities(character)
    affinities = list(affinities)

    return {
        "character": character,
        "affinities": affinities,
    }
