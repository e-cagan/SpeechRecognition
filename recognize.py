import speech_recognition as sr
import pyttsx3
from openai import OpenAI
import os
from dotenv import load_dotenv
import json

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

# Function for getting response from GPT
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

# Function for saving prompt to memory
def save_to_memory(user_input, gpt_response, filepath='memory.json'):
    memory = []

    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            memory = json.load(f)

    # Append the new entry
    memory.append({
        'prompt': user_input,
        'response': gpt_response
    })

    # Sadece son 5 geçmişi tutalım
    memory = memory[-5:]

    with open(filepath, 'w') as f:
        json.dump(memory, f, indent=2)

# Function for loading memory
def load_memory(filepath='memory.json'):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    else:
        return {"prompt": "", "response": ""}
    
# Function for getting prompt from memory
def get_prompt_from_memory(user_input, filepath='memory.json'):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            memory = json.load(f)
    else:
        memory = []

    history_prompt = ""
    for item in memory:
        history_prompt += f"Prompt: {item['prompt']}\nResponse: {item['response']}\n"

    # Add last message
    history_prompt += f"User: {user_input}\n"
    return history_prompt
    
# Load the memory
memory = load_memory()

# Listening with microphone and loop
recognizer = sr.Recognizer()

while True:
    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            audio = recognizer.listen(source)

            user_input = recognizer.recognize_google(audio)
            print(f"User: {user_input}")
            
            # Get conversation history as prompt
            prompt = get_prompt_from_memory(user_input)
            gpt_reply = get_gpt_response(prompt)
            print(f"GPT: {gpt_reply}")

            # Save to memory
            save_to_memory(user_input, gpt_reply)

            # Speak out the reply
            speak_text(gpt_reply)

    except sr.UnknownValueError:
        print("Couldn't understood. Can you try again?")
    except sr.RequestError:
        print("Couldn't connect the API.")
    except KeyboardInterrupt:
        print("Exiting...")
        break
