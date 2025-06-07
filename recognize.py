import speech_recognition as sr
import pyttsx3
from openai import OpenAI
import os
from dotenv import load_dotenv
from memory import save_to_memory, get_chat_history_as_messages, init_db

# === Setup ===
load_dotenv()
init_db()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("API_KEY"),
)

engine = pyttsx3.init()

def speak_text(text):
    engine.say(text)
    engine.runAndWait()

def get_gpt_response(messages):
    completion = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": "https://your-site.com",
            "X-Title": "AI-Agent",
        },
        model="meta-llama/llama-3.3-8b-instruct:free",
        messages=messages
    )
    return completion.choices[0].message.content

def get_intent_from_prompt(user_input):
    system_msg = "You are an intent classification assistant."
    user_msg = f"""
Analyze the purpose of the user. Decide which category is related and return your response as a **single word**:

Categories:
- music
- note
- joke
- weather
- none

Examples:
- Can you play music for me? ==> music
- What is the weather like in Istanbul? ==> weather
- Note this sentence for me? ==> note
- Tell me a joke. I had a bad day ==> joke
- How can I be better at programming? ==> none

If it doesn't fit any category, just return "none".

User Command: "{user_input}"
    """
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg}
    ]
    response = get_gpt_response(messages)
    return response.lower().strip()

def handle_intent(intent):
    if intent == "music":
        speak_text("Şu an müzik çalamam ama modülü eklemen yeterli!")
    elif intent == "note":
        speak_text("Not alındı! Ama not modülünü de geliştirmeliyiz.")
    elif intent == "joke":
        speak_text("Bir espri geliyor: Neden bilgisayar soğuk? Çünkü cache’i var!")
    elif intent == "weather":
        speak_text("Hava durumu modülümüz hazır değil.")
    else:
        return False
    return True

# === Main loop ===
recognizer = sr.Recognizer()

while True:
    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            audio = recognizer.listen(source)

            user_input = recognizer.recognize_google(audio)
            print(f"User: {user_input}")

            intent = get_intent_from_prompt(user_input)
            handled = handle_intent(intent)

            if not handled:
                messages = get_chat_history_as_messages(user_input)
                gpt_reply = get_gpt_response(messages)
                print(f"GPT: {gpt_reply}")

                save_to_memory(user_input, gpt_reply)
                speak_text(gpt_reply)

    except sr.UnknownValueError:
        print("Couldn't understand. Can you try again?")
    except sr.RequestError:
        print("Couldn't connect to the API.")
    except KeyboardInterrupt:
        print("Exiting...")
        break
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
