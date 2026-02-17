import requests

# Simple connectivity test
try:
    r = requests.get("http://127.0.0.1:8001/docs")
    print("GET /docs:", r.status_code)
except Exception as e:
    print("Connection error:", e)

# Test upload endpoint
try:
    with open("q-fastapi-file-validation.csv", "rb") as f:
        r = requests.post(
            "http://127.0.0.1:8001/upload",
            files={"file": ("q-fastapi-file-validation.csv", f, "text/csv")},
            headers={"X-Upload-Token-7844": "6johsr3kr8z9t3tq"},
        )
    print("POST /upload:", r.status_code, r.text)
except Exception as e:
    print("Upload error:", e)
