from flask import Flask, request, jsonify, render_template
from transformers import pipeline
from spotify import get_playlists_by_mood  # Your existing function
import google.generativeai as genai
from emotion_gemini import map_to_emotion_fallback  # Fallback function
app = Flask(__name__)

# Load models
emotion_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=1
)

genai.configure(api_key="AIzaSyDa5cqbuSFDXojN5z6ZeC5OSFnzVFiM7UQ")
gemini_model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
GEMINI_DISABLED = False


def detect_emotion(text):
    result = emotion_classifier(text)[0][0]
    return result["label"].lower(), result["score"]


def generate_gemini_response(user_input, mood):
    global GEMINI_DISABLED
    if GEMINI_DISABLED:
        return "I'm here if you want to talk."

    prompt = f"""
You are a warm, supportive chatbot.
The user just said: "{user_input}"
Their current mood is: {mood.upper()}.

Respond empathetically like a human. Be natural, emotionally aware, and conversational. 
If appropriate, offer to suggest music to help with their feelings.
Don't mention mood detection or that you're an AI.
"""
    try:
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        if "quota" in str(e).lower():
            GEMINI_DISABLED = True
        return "I'm here if you want to talk."


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    # Detect emotion
    mood, confidence = detect_emotion(user_message)
    
    # Use Gemini if available, otherwise fallback
    if confidence < 0.5 or mood == "neutral":
        print("[Emotion Detection Fallback] Too neutral or low confidence")
        mood = map_to_emotion_fallback(user_message)

    try:
        reply = generate_gemini_response(user_message, mood)
    except Exception as e:
        print("[Gemini Fallback]", e)
        reply = "I'm here if you want to talk."

    # Fetch playlists if mood is known
    playlists = []
    if mood in ["sadness", "anger", "joy", "love", "fear", "trauma", "disgust", "surprise"]:
        playlists = get_playlists_by_mood(mood)

    # Convert to required format for frontend
    formatted_playlists = []
    for p in playlists:
        formatted_playlists.append({
            "name": p.get("name"),
            "url": p.get("url"),
            "image": p.get("image", "https://via.placeholder.com/64"),  # default fallback image
            "mood": mood
        })

    return jsonify({
        "response": reply,
        "playlists": formatted_playlists
    })


if __name__ == "__main__":
    app.run(debug=True)
