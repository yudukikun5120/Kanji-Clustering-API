import uvicorn
from fastapi import FastAPI
from affinities_detection import get_affinities

app = FastAPI()


@app.get("/affinities")
def affinities(character: str, sets: str = 'jis_level_1'):
    """
    You can get affinities corresponding to your input character.
    
    \<sets\>::= jis_level_1 | jis_level_2 | \<sets\> \<sets\>
    """

    affinities = [
        affinity
        for set in sets.split()
        for affinity in get_affinities(character, set)
        ]

    return {
        "character": character,
        "affinities": affinities,
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)