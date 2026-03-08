from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
import base64
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use environment variable in real project
client = Groq(api_key="YOUR_GROQ_API_KEY")

@app.get("/")
def home():
    return {"message": "KrishiSahay AI Backend Running"}

@app.post("/analyze")
async def analyze(
    location: str = Form(...),
    crop: str = Form(...),
    question: str = Form(...),
    image: UploadFile = File(None)
):

    image_analysis = ""

    # If image uploaded → analyze
    if image:
        contents = await image.read()
        encoded_image = base64.b64encode(contents).decode("utf-8")

        vision_prompt = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Identify crop disease or visible issues in this image."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded_image}"
                        },
                    },
                ],
            }
        ]

        vision_response = client.chat.completions.create(
            messages=vision_prompt,
            model="llama-3.1-8b-instant"
        )

        image_analysis = vision_response.choices[0].message.content

    # Final advisory prompt
    final_prompt = f"""
    You are an agricultural expert.

    Farmer Location: {location}
    Crop: {crop}
    Question: {question}

    Image Analysis (if provided): {image_analysis}

    Provide response in structured format:

    Cause:
    Treatment:
    Preventive Measures:
    Fertilizer Recommendation:
    Irrigation Advice:
    """

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": final_prompt}],
        model="llama-3.1-8b-instant",
        temperature=0.4
    )

    ai_text = response.choices[0].message.content

    return {"analysis": ai_text}