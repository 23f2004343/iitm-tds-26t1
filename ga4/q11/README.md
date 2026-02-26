# Q11: FastAPI Batch Sentiment Analysis

## Task

Build a `POST /sentiment` FastAPI endpoint that accepts multiple sentences and returns sentiment labels — `happy`, `sad`, or `neutral` — for each sentence in order.

---

## Requirements

* Accept JSON: `{"sentences": ["...", "..."]}`
* Return JSON: `{"results": [{"sentence": "...", "sentiment": "happy|sad|neutral"}, ...]}`
* Valid sentiments: `happy`, `sad`, `neutral` only
* Preserve input order in output
* Pass ≥ 7/10 grader test cases

---

## Approach

### 1. Sentiment Classifier — VADER
Used **VADER** (Valence Aware Dictionary and sEntiment Reasoner) — a rule-based lexicon tuned for short English sentences. No model downloads or GPU needed.

**Compound score thresholds:**
| Range | Label |
|---|---|
| `≥ 0.05` | `happy` |
| `≤ -0.05` | `sad` |
| between | `neutral` |

### 2. FastAPI Endpoint
Single `POST /sentiment` route with Pydantic request/response models for strict validation and automatic OpenAPI docs.

CORS middleware set to `allow_origins=["*"]` so the grader can call from any origin.

### 3. Tunnel — pyngrok
`start.py` launches uvicorn (port 8000) and pyngrok in a single persistent process and writes the public URL to `tunnel_url.txt`.

---

## Code

| File | Purpose |
|---|---|
| [`main.py`](./main.py) | FastAPI app with `/sentiment` route |
| [`start.py`](./start.py) | Starts uvicorn + ngrok together |
| [`requirements.txt`](./requirements.txt) | `fastapi`, `uvicorn`, `vaderSentiment`, `pyngrok` |

**Key classification logic:**
```python
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def classify(sentence: str) -> str:
    compound = analyzer.polarity_scores(sentence)["compound"]
    if compound >= 0.05:   return "happy"
    elif compound <= -0.05: return "sad"
    else:                   return "neutral"
```

---

## Execution

```bash
# Install dependencies
pip install -r requirements.txt

# Start server + public tunnel (prints the public URL)
python start.py
```

---

## Verification

**Local test:**
```bash
curl -X POST http://localhost:8000/sentiment \
  -H "Content-Type: application/json" \
  -d '{"sentences":["I love this!","Terrible.","Meeting at 3 PM."]}'
```

**Expected response:**
```json
{
  "results": [
    {"sentence": "I love this!", "sentiment": "happy"},
    {"sentence": "Terrible.", "sentiment": "sad"},
    {"sentence": "Meeting at 3 PM.", "sentiment": "neutral"}
  ]
}
```

---

## Submission

**Public API URL:**
```
https://lanate-kareen-photostatically.ngrok-free.dev
```

Submit `https://lanate-kareen-photostatically.ngrok-free.dev` to the grader.
The grader should POST to `/sentiment` on this URL.
