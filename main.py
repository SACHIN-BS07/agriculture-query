from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import requests
from groq import Groq  # Make sure "groq" is in requirements.txt

app = FastAPI(title="AI Kisan Sati Backend")

# ----------------------
# Allow frontend access
# ----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Can restrict to your frontend domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------
# Serve static frontend
# ----------------------
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home():
    # Serves your index.html from the static folder
    return FileResponse("static/index.html")

# ----------------------
# Groq Client
# ----------------------
client = Groq(api_key="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")  # Replace with your Groq API key

# ----------------------
# OpenWeather API
# ----------------------
OPENWEATHER_API_KEY = "158e2b02917e280e710858a84fc9982f"  # Replace with your OpenWeather API key

# ----------------------
# Health check
# ----------------------
@app.get("/api/health")
def health():
    return {"message": "AI Kisan Sati Backend Running"}

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
        reply = response.choices[0].message.content
        return {"reply": reply}
    except Exception as e:
        return {"reply": f"Error: {str(e)}"}

# ----------------------
# 2️⃣ Real-Time Weather
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
# 3️⃣ Image Analysis + Crop Advice
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

# ----------------------
# 4️⃣ District Advisory
# ----------------------
@app.post("/api/advisory")
async def advisory(
    district: str = Form(...),
    crop: str = Form(...)
):
    prompt = f"""
You are an agricultural district advisor.

District: {district}
Crop: {crop}

Provide:
- Current seasonal risks
- Disease alerts
- Recommended action
- Suggested pesticide
"""

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.4
        )
        return {"advisory": response.choices[0].message.content}
    except Exception as e:
        return {"error": str(e)}

# ----------------------
# 5️⃣ Farmer Personalization
# ----------------------
@app.post("/api/personalization")
async def personalization(
    soil: str = Form(...),
    crop: str = Form(...),
    land: str = Form(...)
):
    prompt = f"""
You are an agricultural planning expert.

Soil Type: {soil}
Crop: {crop}
Land Size: {land} acres

Provide:
- Fertilizer plan
- Expected yield estimate
- Irrigation advice
- Cost estimate overview
"""

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.4
        )
        return {"plan": response.choices[0].message.content}
    except Exception as e:
        return {"error": str(e)}
