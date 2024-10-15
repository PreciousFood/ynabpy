from fastapi import FastAPI
import json

from typing import Any

app = FastAPI()

def open_json(path: str) -> Any:
    with open(path, "r") as file:
        return json.load(file)

# Sample route for testing
@app.get("/budgets")
def get_budgets() -> Any:
    return open_json("budgets.json")

