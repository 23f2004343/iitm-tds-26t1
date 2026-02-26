"""
start.py — Launches uvicorn + pyngrok in a single persistent process.
Run:  python start.py
The public ngrok URL is printed to stdout and saved to tunnel_url.txt
"""

import subprocess
import sys
import time
import threading
from pyngrok import ngrok, conf

# ---- start uvicorn in a separate thread ----
def run_uvicorn():
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "main:app",
         "--host", "0.0.0.0", "--port", "8000"],
        check=True
    )

t = threading.Thread(target=run_uvicorn, daemon=True)
t.start()
time.sleep(2)   # give uvicorn a moment to bind

# ---- open ngrok tunnel ----
tunnel = ngrok.connect(8000, "http")
public_url = tunnel.public_url

# ngrok gives http:// — prefer https://
if public_url.startswith("http://"):
    public_url = public_url.replace("http://", "https://", 1)

print(f"\n{'='*55}")
print(f"  FastAPI Sentiment API is LIVE")
print(f"  Public URL : {public_url}")
print(f"  Endpoint   : {public_url}/sentiment")
print(f"{'='*55}\n")

with open("tunnel_url.txt", "w") as f:
    f.write(public_url + "\n")

# Keep the process alive
try:
    t.join()
except KeyboardInterrupt:
    print("\nShutting down...")
    ngrok.disconnect(tunnel.public_url)
    ngrok.kill()
