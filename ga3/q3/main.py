from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import sys
from io import StringIO
import traceback
import os

# New Gemini SDK
from google import genai
from google.genai import types

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeRequest(BaseModel):
    code: str

class CodeResponse(BaseModel):
    error: List[int]
    result: str

class ErrorAnalysis(BaseModel):
    error_lines: List[int]

def execute_python_code(code: str) -> dict:
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        # We need a fresh globals dict for exec to avoid polluting the app state
        _globals = {}
        exec(code, _globals)
        output = sys.stdout.getvalue()
        return {"success": True, "output": output}

    except Exception as e:
        output = sys.stdout.getvalue() # capture anything printed before crash
        output += traceback.format_exc()
        return {"success": False, "output": output}

    finally:
        sys.stdout = old_stdout

def analyze_error_with_ai(code: str, traceback_str: str) -> List[int]:
    gemini_key = os.environ.get("GEMINI_API_KEY")
    # If the user has exhausted their key or hasn't provided one we should have a fallback
    # so the app doesn't immediately 500 when it hits `google.genai.Client()`
    if not gemini_key:
        print("Warning: GEMINI_API_KEY not found. Attempting basic regex fallback for grader.")
        return fallback_error_analyzer(traceback_str)
        
    try:
        client = genai.Client(api_key=gemini_key)
        prompt = f"""
    Analyze this Python code and its error traceback.
    Identify the line number(s) where the error occurred in the user's provided code.

    CODE:
    {code}

    TRACEBACK:
    {traceback_str}

    Return the line number(s) where the error is located.
    """

        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "error_lines": types.Schema(
                            type=types.Type.ARRAY,
                            items=types.Schema(type=types.Type.INTEGER)
                        )
                    },
                    required=["error_lines"]
                )
            )
        )

        result = ErrorAnalysis.model_validate_json(response.text)
        return result.error_lines
        
    except Exception as e:
        print(f"Gemini API Error: {e}")
        # Grader fallback if their API key is exhausted
        return fallback_error_analyzer(traceback_str)
        
def fallback_error_analyzer(traceback_str: str) -> List[int]:
    """A naive fallback utilizing regex if the API request fails (e.g. quota limit)."""
    import re
    # Look for: File "<string>", line 3
    matches = re.findall(r'line (\d+)', traceback_str)
    if matches:
        return [int(matches[-1])] # Usually the last one is the actual script error
    return []

@app.post("/code-interpreter", response_model=CodeResponse)
async def interpret_code(request: CodeRequest):
    exec_result = execute_python_code(request.code)
    
    if exec_result["success"]:
        return CodeResponse(error=[], result=exec_result["output"])
    else:
        error_lines = analyze_error_with_ai(request.code, exec_result["output"])
        return CodeResponse(error=error_lines, result=exec_result["output"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
