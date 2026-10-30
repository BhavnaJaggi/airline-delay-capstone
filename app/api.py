"""Programming interface for the flight delay risk model (FastAPI).

Run:   uvicorn app.api:app --reload          (from the project root)
Call:  POST /predict  with a JSON body such as
       {"carrier": "WN", "origin": "DAL", "dest": "HOU", "month": 7, "day_of_week": 5, "dep_time": 1745}
"""
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.delay_model import DelayRiskModel

app = FastAPI(title="Flight delay risk service", version="1.0")
_model = DelayRiskModel()


class Flight(BaseModel):
    carrier: str = Field(..., examples=["WN"])
    origin: str = Field(..., examples=["DAL"])
    dest: str = Field(..., examples=["HOU"])
    month: int = Field(..., ge=1, le=12)
    day_of_week: int = Field(..., ge=1, le=7, description="1 = Monday ... 7 = Sunday")
    dep_time: int = Field(..., ge=0, le=2359, description="scheduled departure as hhmm")
    distance: Optional[float] = Field(None, description="miles; looked up from origin and destination if omitted")
    lf_prev: Optional[float] = Field(None, description="previous month's route load factor (percent), if known")


@app.get("/health")
def health():
    return {"status": "ok", "model": _model.spec["model"], "test_auc": _model.spec["test_auc"]}


@app.post("/predict")
def predict(f: Flight):
    try:
        return _model.predict(**f.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
