# 🧠 Activity Sage – Backend

This is the backend service for **Activity Sage**, a personalized activity suggestion app.  
It uses **FastAPI** and integrates with a locally hosted **Ollama LLM** (e.g., `gemma3:1b`) running on an EC2 instance to generate context-aware activity ideas.

---

## 🚀 Features

- Accepts detailed user input via HTTP `POST` form.
- Constructs a dynamic prompt based on:
  - Number of people
  - Budget
  - Mood
  - Environment (indoor/outdoor)
  - Duration
  - Time of day
  - Age group
  - Interests
  - Accessibility needs
  - Current weather
- Sends prompt to a local Ollama LLM (`gemma3:1b`).
- Parses and returns a JSON list of **3 customized activity suggestions**.

---

## 🛠️ Tech Stack

- **Python 3.12**
- **FastAPI**
- **Ollama LLM** (runs locally on EC2)
- **CORS** enabled for `http://activitysage.fursa.click:3000`

---

## 📦 API Endpoint

### `POST /suggest`

#### Request Parameters (Form fields)

| Name                | Type   | Required | Description                             |
|---------------------|--------|----------|-----------------------------------------|
| `people`            | str    | ✅       | Number of people involved               |
| `budget`            | str    | ✅       | Budget in NIS                           |
| `mood`              | str    | ✅       | Current mood                            |
| `environment`       | str    | ✅       | Indoor or Outdoor                       |
| `duration`          | str    | ✅       | Duration of the activity                |
| `time_of_day`       | str    | ✅       | Morning, afternoon, evening, etc.       |
| `age_group`         | str    | ✅       | Age group of participants               |
| `interests`         | str    | ✅       | Interests, hobbies                      |
| `accessibility_needs`| str   | Optional | Any accessibility requirements          |
| `weather`           | str    | Optional | Current weather (e.g., sunny, rainy)    |

#### Response

```json
{
  "suggestions": [
    {
      "title": "Activity Title",
      "description": "Brief explanation of the activity",
      "estimated_cost": "Estimated cost range"
    },
    ...
  ],
  "response_time": "0.76s"
}
