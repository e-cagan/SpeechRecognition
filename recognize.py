import speech_recognition as sr
import pyttsx3
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("API_KEY"),
)

# Start speaking engine
engine = pyttsx3.init()

def speak_text(text):
    engine.say(text)
    engine.runAndWait()

# Function to get response from GPT
def get_gpt_response(prompt):
    completion = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": "https://your-site.com",
            "X-Title": "AI-Agent",
        },
        model="meta-llama/llama-3.3-8b-instruct:free",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return completion.choices[0].message.content

# Listening with microphone and loop
recognizer = sr.Recognizer()

while True:
    try:
        with sr.Microphone() as source:
            # Listen part
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            audio = recognizer.listen(source)

            # Displaying prompt said by user
            user_input = recognizer.recognize_google(audio)
            print(f"User: {user_input}")
            
            # Get reply from GPT
            gpt_reply = get_gpt_response(user_input)
            print(f"GPT: {gpt_reply}")

            # Give the audio for response
            speak_text(gpt_reply)

    except sr.UnknownValueError:
        print("Couldn't understood. Can you try again?")
    except sr.RequestError:
        print("Couldn't connect the API.")
    except KeyboardInterrupt:
        print("Exiting...")
        break
