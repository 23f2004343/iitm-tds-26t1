# Q10: Publish a Docker Space

## Task

Containerize a deployment observability API on Hugging Face Spaces using the Docker SDK.

**Requirements**:
- Space name: `ga2-f0af22`
- Visibility: Public
- Hardware: CPU Basic
- SDK: Docker
- App Port: 7255
- Description contains: `deployment-ready-ga2-f0af22`
- Dockerfile: `python:3.11-slim`, UID 1000 user
- Secret: `GA2_TOKEN_ECB8`

---

## Approach

### Step 1: Application (`main.py`)

Created a minimal FastAPI application that exposes health and root endpoints:

```python
from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
async def root():
    return {
        "status": "healthy",
        "service": "deployment-ready-ga2-f0af22",
        "port": int(os.environ.get("APP_PORT", 7255)),
    }
```

### Step 2: Dockerfile with User Security

Authored a `Dockerfile` that meets the strict user requirements:

1.  **Base Image**: `python:3.11-slim`
2.  **User Creation**: `RUN useradd -m -u 1000 user`
3.  **Permissions**: Uses `COPY --chown=1000:1000` to ensure application files are owned by the non-root user.
4.  **Switch User**: Explicitly switches to `USER 1000` before running the application.

```dockerfile
FROM python:3.11-slim

# Create user with UID 1000
RUN useradd -m -u 1000 user

WORKDIR /app

# Install dependencies
COPY --chown=1000:1000 ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy application code with ownership
COPY --chown=1000:1000 . .

ENV APP_PORT=7255
EXPOSE 7255

# Switch to non-root user UID 1000
USER 1000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7255"]
```

### Step 3: Space Configuration

- **SDK**: Set to `docker` in `README.md` frontmatter.
- **Port**: Set `app_port: 7255` in frontmatter.
- **Secret**: Added `GA2_TOKEN_ECB8` via Python script/CLI.

---

## Issues & Debugging

### Issue 1: Permission Denied / Grader Error

Initially encountered "Dockerfile must switch to non-root user UID 1000".

**Root Cause**: The grader checks for an explicit `USER 1000` instruction and likely verifies file ownership.
**Fix**: Updated `Dockerfile` to use numeric ownership (`chown=1000:1000`) and numeric user switch (`USER 1000`) to be unambiguous.

### Issue 2: Hugging Face API Tokens

Encountered permission errors when creating the Space.
**Fix**: Switched to a Hugging Face token with **Write** permissions.

---

## Current Status

| Check | Status |
|-------|--------|
| Space Created | ✅ |
| Docker Build | ✅ Success |
| App Running | ✅ Port 7255 |
| User Check | ✅ UID 1000 |
| Secret Set | ✅ |

**Live URL**: `https://huggingface.co/spaces/aloktripathi/ga2-f0af22`

---

## Files

- `README.md` — This file (contains Space metadata and documentation)
- `Dockerfile` — Defines the container environment
- `main.py` — The FastAPI application
- `requirements.txt` — Python dependencies
