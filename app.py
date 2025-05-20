from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from ollama import chat
import time
import os
import json

# 🔧 Set Ollama endpoint (your EC2 IP)

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://18.175.90.200").split(",")

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/suggest")
async def suggest(people: str = Form(...), budget: str = Form(...),
            mood: str = Form(...), environment: str = Form(...)):

    prompt = f"""
    We are {people} people, our budget is {budget}, we feel {mood}, and want {environment} activities.

    Suggest exactly 3 fun group activities that match these conditions.

    For each activity, respond in this JSON format:
    [
      {{
        "title": "Name of the activity",
        "description": "Short description",
        "estimated_cost": "Rough price range"
      }},
      ...
    ]

    Only return the JSON list. Do not explain it.
    """

    messages = [
        {"role": "system", "content": "You are a helpful assistant that returns activity suggestions in clean JSON."},
        {"role": "user", "content": prompt}
    ]

    try:
        print("🔄 Sending to Ollama (via Python client)...")
        start = time.time()
        response = chat(model="gemma3:1b", messages=messages)
        answer = response['message']['content']
        print("✅ Ollama responded:", answer)
    except Exception as e:
        print("❌ Ollama client error:", str(e))
        return JSONResponse(
            status_code=500,
            content={"error": f"Error talking to Ollama: {str(e)}"}
        )

    # Try to parse the JSON
    try:
        # Clean answer by stripping ```json ... ``` wrapper if it exists
        cleaned = answer.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned.removeprefix("```json").strip()
        if cleaned.endswith("```"):
            cleaned = cleaned.removesuffix("```").strip()

        try:
            suggestions = json.loads(cleaned)
        except json.JSONDecodeError:
            return JSONResponse(
                status_code=500,
                content={"error": f"Could not parse response: {answer}"}
            )

    except json.JSONDecodeError:
        return JSONResponse(
            status_code=500,
            content={"error": f"Could not parse the model's response as JSON: {answer}"}
        )

    elapsed = time.time() - start
    return JSONResponse(content={
        "suggestions": suggestions,
        "response_time": f"{elapsed:.2f}s"
    })