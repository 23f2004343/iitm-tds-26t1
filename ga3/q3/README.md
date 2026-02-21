# Q3: Code Interpreter with AI Error Analysis

## Task

Create a FastAPI web server endpoint `POST /code-interpreter` that dynamically executes Python code payloads over an HTTP request. Upon successful execution, the endpoint returns the standard output. Upon failure, the endpoint programmatically captures the stack trace and feeds it to an AI Agent (`gemini-2.0-flash-exp`) using strictly typed structured JSON to isolate the precise line number(s) that caused the exception, simulating an intelligent IDE assistant.

---

## Requirements

* Create a FastAPI web server running locally on port 8000.
* Provide an endpoint `POST /code-interpreter` conforming to `application/json`.
* Request format receives a multiline string under the `code` property.
* Response format returns `{"error": [...], "result": "..."}`.
* Python code execution uses `sys.stdout` hijacking and `exec()` to parse text strings into runtime execution.
* Google's `gemini-2.0-flash-exp` model must analyze the `traceback` (if an exception occurs) and return an explicit integer array identifying the crashed line.
* Use `ngrok` to expose the API to the public internet for automated grader testing.

---

## Approach

### 1. Build the REST Interface
Utilize the FastAPI Python library, along with `uvicorn` and `pydantic`, to construct the API footprint. Pydantic handles the `CodeRequest` inbound schema and the `CodeResponse` outbound schema. Cross-Origin Resource Sharing (CORS) is enabled to allow the grading platform to interface with the endpoint. 

### 2. Capture and Exec
The `execute_python_code` function overrides the system's standard output `sys.stdout = StringIO()` and executes the string payload within an isolated dictionary state `exec(code, globals())`.
If the execution is clean, the exact `stdout` is pulled and served. If it crashes, `traceback.format_exc()` is dumped to capture the execution failure exactly as the Python interpreter sees it.

### 3. Connect the AI Agent (Google GenAI)
If `execute_python_code` returns `success: False`, the `analyze_error_with_ai` agent is invoked. The agent uses the `google-genai` Python SDK to submit the code string and the traceback string to `gemini-2.0-flash-exp`. 

Crucially, the request uses the `GenerateContentConfig(response_schema=...)` feature to strictly enforce that the LLM only replies with an `ErrorAnalysis` validation structure (a JSON object carrying an `error_lines` integer Array).

### 4. Create Public Tunnel
Expose the locally hosted instance to the public internet using `ngrok` to facilitate remote webhook integration for the auto-grader platform.

---

## Installation

**Install Dependencies:**
```powershell
pip install fastapi uvicorn pydantic google-genai
```

**Ngrok Setup:**
Ensure `ngrok` is installed on your local machine and your authentication token is configured:
```powershell
ngrok config add-authtoken YOUR_AUTHTOKEN_HERE
```

---

## Execution

### Step 1: Start FastAPI Server (Terminal 1)

**Define Environment Variable:**
Set your Gemini API key so the Python script can communicate with Google's APIs during the traceback analysis.
```powershell
$env:GEMINI_API_KEY="AIzaSy..."
```

**Run Uvicorn Server:**
```powershell
python main.py
```

**Expected Output:**
```
INFO:     Started server process [22592]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Start ngrok Tunnel (Terminal 2)

**Create Public Tunnel:**
```powershell
ngrok http 8000
```

**Expected Output:**
```
Session Status                online
Account                       your-account (Plan: Free)
Forwarding                    https://[random-string].ngrok-free.dev -> http://localhost:8000
```

---

## Verification

To confirm the API fulfills the code evaluation structure, use `curl` or `Invoke-RestMethod` to emulate the grader's tests against valid and invalid code payloads.

### Test 1: Successful Code
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/code-interpreter" -Method POST -Headers @{"Content-Type" = "application/json"} -Body '{"code": "x = 5`ny = 10`nprint(x + y)"}'
```
**Expected Response:**
```json
{
  "error": [],
  "result": "15\n"
}
```

### Test 2: Crashing Code
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/code-interpreter" -Method POST -Headers @{"Content-Type" = "application/json"} -Body '{"code": "x = 10`ny = 0`nresult = x / y"}'
```
**Expected Response:**
```json
{
  "error": [3],
  "result": "Traceback (most recent call last):\n  File \"<string>\", line 3, in <module>\nZeroDivisionError: division by zero"
}
```

---

## Architecture Flow

**Success Flow:**
```
Internet (Grader) → ngrok Tunnel → localhost:8000 (FastAPI) → exec() → Return Result
```

**Exception Flow:**
```
Internet (Grader) → ngrok Tunnel → localhost:8000 (FastAPI) → exec() crashes → Gemini Traceback Structure Agent → Return Result & Error array
```

---

## Submission

**Your Public URL will look like this:**
```
https://[random-string].ngrok-free.dev
```

Copy the HTTPS forwarding URL generated by `ngrok` in terminal and submit it to the assignment platform. Ensure your local `main.py` script remains actively running until grading completes successfully.
