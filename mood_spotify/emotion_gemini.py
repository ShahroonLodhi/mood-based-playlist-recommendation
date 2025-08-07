import random
import google.generativeai as genai
from transformers import pipeline
from spotify import get_playlists_by_mood
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


# if gemini quota is exceeded, use fallback emotion detection
def map_to_emotion_fallback(text):
    text = text.lower()

    keyword_map = {
        "joy": ["happy", "excited", "joyful", "glad", "pleased", "awesome", "jolly", "cheerful"],
        "sadness": ["sad", "down", "unhappy", "depressed", "upset", "miserable", "cry"],
        "anger": ["angry", "mad", "furious", "irritated", "frustrated", "rage"],
        "fear": ["scared", "afraid", "fearful", "nervous", "anxious", "terrified"],
        "love": ["love", "loving", "romantic", "sweet", "affection"],
        "disgust": ["disgusted", "gross", "repulsed", "nasty"],
        "surprise": ["surprised", "shocked", "amazed", "unexpected", "whoa"],
        "trauma": ["trauma", "abuse", "hurt", "pain", "broken", "haunted"]
    }

    for emotion, keywords in keyword_map.items():
        for word in keywords:
            if word in text:
                return emotion

    return "neutral"


# Replace this with your actual Gemini API Key
GEMINI_API_KEY = "AIzaSyDa5cqbuSFDXojN5z6ZeC5OSFnzVFiM7UQ"
genai.configure(api_key=GEMINI_API_KEY)

gemini_model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

# Global flag to disable Gemini once quota is hit
GEMINI_DISABLED = False

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
            print(f"[Gemini Error] Quota exceeded. Disabling Gemini for this session.\n")
            GEMINI_DISABLED = True
        else:
            print(f"[Gemini Error] {e}")
        return "I'm here if you want to talk."

def detect_emotion(text):
    result = emotion_classifier(text)[0][0]  # Top result
    return result["label"].lower(), result["score"]


def run_chat():
    print("🤖 Hi there! How are you feeling today?")

    exit_keywords = ["bye", "exit", "quit", "see you", "goodbye", "later", "cya", "talk to you later", "take care", "peace", "adios", 
                     "farewell", "catch you later", "until next time"]

    while True:
        user_input = input("👤 You: ").strip().lower()

        if any(kw in user_input for kw in exit_keywords):
            print("🤖 👋 Take care. I'm here if you ever want to talk or need music.")
            break

        try:
            mood, confidence = detect_emotion(user_input)
            if mood == "neutral" or confidence < 0.4:
                raise ValueError("Too neutral or low confidence")
        except Exception as e:
            print(f"[Emotion Detection Fallback] {e}")
            mood = map_to_emotion_fallback(user_input)
            confidence = 1.0  # assume high confidence for fallback

        print(f"🔍 Detected Mood: {mood} (Confidence: {confidence:.2f})")

        reply = generate_gemini_response(user_input, mood)
        print(f"🤖 {reply}\n")

        if mood in ["sadness", "anger", "joy", "love", "fear", "trauma", "disgust", "surprise"]:  
            ans = input("🎵 Want a playlist to match your mood? (yes/no): ").strip().lower()
            if ans in ["yes", "y", "sure"]:
                playlists = get_playlists_by_mood(mood)
                if playlists:
                    print("\n🎧 Here are some playlists for you:")
                    for name, url in playlists:
                        print(f"- {name}\n  {url}")
                else:
                    print("😕 Couldn't find any playlists right now.")



if __name__ == "__main__":
    run_chat()
