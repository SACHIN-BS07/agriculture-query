from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import requests
from groq import Groq

app = FastAPI(title="AI Kisan Sati Backend")

# ----------------------
# Allow frontend access
# ----------------------
# Use "*" to allow any frontend (works on phone, other systems, deployed site)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------
# Serve frontend
# ----------------------
@app.get("/")
def home():
    # If you host frontend separately, skip this.
    return FileResponse("index.html")  # Put your index.html here if you want static serving

# ----------------------
# Groq client
# ----------------------
client = Groq(api_key="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")  # Replace with your Groq key

# ----------------------
# OpenWeather API
# ----------------------
OPENWEATHER_API_KEY = "158e2b02917e280e710858a84fc9982f"  # Replace with your OpenWeather key

# ----------------------
# Health Check
# ----------------------
@app.get("/api/health")
def health():
    return {"message": "AI Kisan Sati Backend is healthy"}

# ----------------------
# 1️⃣ AI Chatbot
# ----------------------
@app.post("/api/chat")
async def chat(request: Request):
    data = await request.json()
    user_msg = data.get("message", "").strip()
    language = data.get("language", "English")

    if not user_msg:
        return {"reply": "Please enter a query."}

    prompt = f"""
You are an expert agricultural advisor.
Language: {language}
Farmer Query:
{user_msg}
Provide a clear, practical, and concise response in {language}.
"""
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.4
        )
        return {"reply": response.choices[0].message.content}
    except Exception as e:
        return {"reply": f"Error: {str(e)}"}

# ----------------------
# 2️⃣ Weather
# ----------------------
@app.get("/api/weather")
def weather(city: str):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    try:
        res = requests.get(url)
        data = res.json()
        if data.get("cod") != 200:
            return {"error": data.get("message", "City not found")}

        return {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "description": data["weather"][0]["description"]
        }
    except Exception as e:
        return {"error": str(e)}

# ----------------------
# 3️⃣ Image Analysis
# ----------------------
@app.post("/api/decision")
async def decision(
    location: str = Form(...),
    crop: str = Form(...),
    question: str = Form(...),
    image: UploadFile = File(None)
):
    image_note = "No image uploaded."
    if image:
        image_note = f"Farmer uploaded image '{image.filename}' showing crop symptoms."

    prompt = f"""
You are an expert agricultural advisor.
Location: {location}
Crop: {crop}
Question: {question}
Image Info: {image_note}

Provide response in structured format:
Cause:
Treatment:
Preventive Measures:
Fertilizer Recommendation:
Irrigation Advice:
"""
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.4
        )
        return {"analysis": response.choices[0].message.content}
    except Exception as e:
        return {"error": str(e)}
