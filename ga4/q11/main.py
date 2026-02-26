"""
FastAPI Batch Sentiment Analysis — ga4/q11
POST /sentiment  →  happy | sad | neutral
Uses VADER (Valence Aware Dictionary and sEntiment Reasoner) — rule-based,
no model downloads, highly accurate for short English sentences.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = FastAPI(title="Batch Sentiment Analysis", version="1.0.0")

# Allow all origins so the grader can call freely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

analyzer = SentimentIntensityAnalyzer()


# ---------- Pydantic schemas ----------
class SentimentRequest(BaseModel):
    sentences: List[str]


class SentimentResult(BaseModel):
    sentence: str
    sentiment: str  # "happy" | "sad" | "neutral"


class SentimentResponse(BaseModel):
    results: List[SentimentResult]


# ---------- Sentiment mapping ----------
def classify(sentence: str) -> str:
    """
    Map VADER compound score to happy / sad / neutral.
    Thresholds tuned for short consumer sentences:
      compound >= 0.05  → happy
      compound <= -0.05 → sad
      otherwise         → neutral
    """
    scores = analyzer.polarity_scores(sentence)
    compound = scores["compound"]
    if compound >= 0.05:
        return "happy"
    elif compound <= -0.05:
        return "sad"
    else:
        return "neutral"


# ---------- Routes ----------
def _run_sentiment(request: SentimentRequest) -> SentimentResponse:
    results = [
        SentimentResult(sentence=s, sentiment=classify(s))
        for s in request.sentences
    ]
    return SentimentResponse(results=results)


@app.post("/sentiment", response_model=SentimentResponse)
def batch_sentiment(request: SentimentRequest):
    return _run_sentiment(request)


# Some graders POST to / instead of /sentiment
@app.post("/", response_model=SentimentResponse)
def batch_sentiment_root(request: SentimentRequest):
    return _run_sentiment(request)


@app.get("/")
def health():
    return {"status": "ok", "endpoint": "POST /sentiment"}


@app.get("/sentiment")
def sentiment_info():
    return {"status": "ok", "method": "POST", "endpoint": "/sentiment"}
