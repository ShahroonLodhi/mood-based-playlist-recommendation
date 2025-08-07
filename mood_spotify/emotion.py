from transformers import pipeline
import random

# Load the model
emotion_classifier = pipeline(
    "text-classification", 
    model="j-hartmann/emotion-english-distilroberta-base", 
    top_k=1  
)


# gather emotion from text
def detect_emotion(text):
    result = emotion_classifier(text)[0][0]  
    return result["label"].lower(), result["score"]

def generate_response(user_input, mood):
    user_input = user_input.lower()

    # Custom logic based on both emotion and words
    if "bye" in user_input or "goodbye" in user_input:
        return "👋 Take care. I'm here if you want to chat or need some music later."

    if "no" in user_input:
        return "Okay, no problem. Let me know if you ever want a playlist or just to talk."

    # Emotion-based responses with some variation
    responses = {
        "sadness": [
            "I'm really sorry you're feeling down. Want me to find a playlist to help?",
            "That sounds rough... music can be soothing — want a recommendation?",
            "You're not alone. Would you like a playlist to ease the sadness?"
        ],
        "joy": [
            "That’s awesome! Want a playlist to match your happy vibes?",
            "Great to hear! Should I queue up something upbeat?",
            "Nice! Let’s keep that energy going — music?"
        ],
        "anger": [
            "That sounds really frustrating. Want something calming?",
            "Tough situation. I can find a chill playlist if you’d like.",
            "Let’s cool off with some relaxing music — want that?"
        ],
        "fear": [
            "It's okay to feel that way. I’m here — want something calming?",
            "That sounds stressful. Would a soft playlist help you breathe?",
            "You’re not alone. Music can sometimes help — want a suggestion?"
        ],
        "disgust": [
            "Ugh, that doesn’t sound pleasant. Want a distraction with music?",
            "Yikes. I can find you something light or funny to shift gears?",
            "Let’s shake that off — music might help. Interested?"
        ],
        "surprise": [
            "Whoa, unexpected! Want a playlist to match the moment?",
            "Sounds exciting — should I bring in some celebratory music?",
            "Well that’s a surprise — want a vibe to go with it?"
        ],
        "neutral": [
            "Thanks for sharing. Want me to find a playlist for your day?",
            "Let me know if you'd like music — I can suggest something fitting.",
            "I’m here whenever you feel like talking or listening."
        ]
    }

    return random.choice(responses.get(mood, responses["neutral"]))

def chatbot_reply(user_input):
    mood, confidence = detect_emotion(user_input)
    response = generate_response(user_input, mood)
    return mood, response


"""if __name__ == "__main__":
    while True:
        user_input = input("👤 Enter how you're feeling: ")
        if user_input.lower() in ["exit", "quit", "stop", "bye", "goodbye", "q"]:
            print("👋 Goodbye!")
            break
        emotion, confidence = detect_emotion(user_input)
        print(f"🧠 Detected Emotion: {emotion} (Confidence: {confidence:.2f})")"""
while True:
    user_input = input("👤 You: ")
    if user_input.lower() in ["exit", "quit", "bye"]:
        print("🤖 👋 Take care. See you soon!")
        break

    mood, confidence = detect_emotion(user_input)
    reply = generate_response(user_input, mood)
    print(f"🤖 [{mood.upper()}] {reply}")