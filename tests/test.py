import pytest
from fastapi.testclient import TestClient
from fake_backend import app  # Import your FastAPI app here
import ynab

from ynab import Budget

Budget

# Initialize the TestClient with the FastAPI app
client = TestClient(app)

def test_budgets() -> None:
    budgets = client.get("/budgets")
    print(budgets)


# More test cases can be added here
