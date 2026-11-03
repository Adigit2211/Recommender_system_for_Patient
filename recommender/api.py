"""Web API.

Run:  uvicorn recommender.api:app --reload
Then open http://127.0.0.1:8000/docs to try it in the browser."""
from fastapi import FastAPI

from .engine import load_rule_data, recommend
from .models import PatientProfile

app = FastAPI(title="Patient-Appropriate Movie Recommender",
              description="Send a patient profile, get five safe movie picks with the reasons.")


@app.post("/recommendations")
def recommendations(profile: PatientProfile):
    return recommend(profile.model_dump())


@app.get("/rules")
def rules():
    """Every rule the recommender uses, with where it came from."""
    return load_rule_data()


@app.get("/health")
def health():
    return {"status": "ok"}
