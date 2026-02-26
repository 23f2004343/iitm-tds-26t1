# Q15: The Recursive Corrupted JSON Fixer

## Task

Stream a ~15MB corrupted JSON log file, salvage only valid JSON records, sum the deeply nested field `metric_968` across all valid records, then compute the SHA-256 hash of that integer sum.

---

## Requirements

* Process the file in a streaming/memory-efficient manner
* Discard any line that fails `json.loads()` — do not attempt repair
* Navigate: `record["context"]["system"]["process"]["metrics"]["metric_968"]`
* SHA-256 hash of the integer sum (no newlines, no spaces)

---

## Approach

### 1. Extract ZIP
Open `corrupted_logs.zip` directly with `zipfile` — no disk extraction. Stream `corrupted_logs.json` line-by-line.

### 2. Parse Defensively
Wrap each `json.loads()` call in `try/except`. Any line with unquoted keys, missing brackets, embedded stack traces, or other JSON errors is silently skipped.

### 3. Deep Field Access
Navigate to `metric_968` via chained dictionary access. Any `KeyError` (missing field) also results in the record being skipped.

### 4. Hash
```python
hashlib.sha256(str(total).encode('utf-8')).hexdigest()
```

---

## Code

**Script:** [`solve.py`](./solve.py)

```python
import zipfile, json, hashlib

total = 0
with zipfile.ZipFile("corrupted_logs.zip") as z:
    with z.open("corrupted_logs.json") as f:
        for line in f:
            line = line.decode("utf-8", errors="replace").strip()
            if not line: continue
            try:
                record = json.loads(line)
                val = record["context"]["system"]["process"]["metrics"]["metric_968"]
                total += int(val)
            except Exception:
                pass  # skip invalid / missing-field records

sha = hashlib.sha256(str(total).encode("utf-8")).hexdigest()
print(sha)
```

---

## Verification

```bash
python solve.py
```

| Metric | Value |
|---|---|
| Valid records | 71,998 |
| Invalid (skipped) | 65,071 |
| Total lines | 137,069 |
| Sum of `metric_968` | 36,073,236 |
| SHA-256 hash | `7bd24bae2ec90cfa635284704c4a422b9742a161b384dda261d21a6cf5167173` |

---

## Submission

**Your Answer:**
```
7bd24bae2ec90cfa635284704c4a422b9742a161b384dda261d21a6cf5167173
```
