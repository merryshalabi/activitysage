from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from ollama import chat
import time
import os
import json

# 🔧 Set Ollama endpoint (your EC2 IP)

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
CORS_ORIGINS = [
    "http://activitysage.fursa.click:3000",
    "http://localhost:3000"
]


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/suggest")
async def suggest(
    people: str = Form(...),
    budget: str = Form(...),
    mood: str = Form(...),
    environment: str = Form(...),
    duration: str = Form(...),
    time_of_day: str = Form(...),
    age_group: str = Form(...),
    interests: str = Form(...),
    accessibility_needs: str = Form(""),
    weather: str = Form("")
):
    prompt = f"""
    We are {people} people, feeling {mood}. Our budget is {budget}₪.
    We prefer {environment} activities during the {time_of_day}, for around {duration}.
    We are in the {age_group} age group and are interested in {interests}.
    Current weather is {weather}. Accessibility needs: {accessibility_needs or 'none'}.

    Suggest exactly 3 personalized activity ideas in JSON format that suit our context.
    Be creative, useful, and do not exceed the budget.

    Respond in this JSON format:
    [
      {{
        "title": "Name of the activity",
        "description": "Short description",
        "estimated_cost": "Rough price range"
      }},
      ...
    ]

    Only return the JSON list. No explanations or extra text.
    """

    messages = [
        {"role": "system", "content": "You are a helpful assistant that returns activity suggestions in clean JSON."},
        {"role": "user", "content": prompt}
    ]

    try:
        start = time.time()
        response = chat(model="gemma3:1b", messages=messages)
        answer = response['message']['content']
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error talking to Ollama: {str(e)}"}
        )

    # Clean and parse JSON
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
            content={"error": f"Could not parse the model's response as JSON: {answer}"}
        )

    elapsed = time.time() - start
    return JSONResponse(content={
        "suggestions": suggestions,
        "response_time": f"{elapsed:.2f}s"
    })
