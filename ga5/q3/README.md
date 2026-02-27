# Q3: LLM Topic Modeling — News Headlines Classification

## Task

Classify 200 news headlines into exactly one of: `Politics`, `Sports`, `Technology`, `Business`, `Entertainment` using an LLM. Submit the count for `Technology`.

---

## Requirements

* Classify all 200 headlines
* `temperature=0` for deterministic output
* Exact spellings: `Politics, Sports, Technology, Business, Entertainment`

---

## Approach

### Batched Classification
Headlines are classified in groups of 10 per API call (20 calls total), asking the model to return a JSON array. This reduces cost and latency vs. one call per headline.

**Topic breakdown (200 headlines):**
| Topic | Count |
|-------|-------|
| Sports | 48 |
| Technology | 45 |
| Politics | 40 |
| Entertainment | 35 |
| Business | 32 |

---

## Code

| File | Purpose |
|---|---|
| [`solution.py`](./solution.py) | Batch LLM classification, prints Technology count |
| [`news_headlines.csv`](./news_headlines.csv) | 200 headlines in `headline` column |

**Key logic:**
```python
resp = client.chat.completions.create(
    model="gpt-4o-mini",
    temperature=0,
    messages=[{"role": "user", "content": (
        "Classify each headline into one of: Politics, Sports, Technology, "
        "Business, Entertainment.\n"
        "Reply with ONLY a JSON array of labels.\n\n"
        f"Headlines:\n{numbered}"
    )}]
)
labels = json.loads(resp.choices[0].message.content.strip())
```

---

## Execution

```bash
export OPENAI_API_KEY=...
export OPENAI_BASE_URL=https://aipipe.org/openai/v1

python solution.py
```

---

## Submission

**Your Answer:**
```
45
```
