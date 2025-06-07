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

    # Store last 5 conversations
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
    
# Function for getting chat history
def get_chat_history(user_input, filepath='memory.json'):
    messages = []

    memory = load_memory(filepath)

    for item in memory:
        messages.append({"role": "user", "content": item['prompt']})
        messages.append({"role": "assistant", "content": item['response']})

    messages.append({"role": "user", "content": user_input})

    return messages

# Function for analyzing user intent
def get_intent_from_prompt(user_input):
    prompt = f"""
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

    If doesn't fit any category just print none.

    User Command: "{user_input}"
    """

    # Format the prompt as a message in the required format
    messages = [
        {"role": "system", "content": "You are an intent classification assistant."},
        {"role": "user", "content": prompt}
    ]

    response = get_gpt_response(messages)
    return response.lower().strip()

# Function for handling intent
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
    
# Load the memory
memory = load_memory()

# Listening with microphone and loop
recognizer = sr.Recognizer()

while True:
    try:
        with sr.Microphone() as source:
            # Listen the user
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            audio = recognizer.listen(source)

            # Take user input
            user_input = recognizer.recognize_google(audio)
            print(f"User: {user_input}")

            # Take the intent of the user
            intent = get_intent_from_prompt(user_input)
            handled = handle_intent(intent)
            
            if not handled:
                # Get conversation history as prompt
                prompt = get_chat_history(user_input)
                gpt_reply = get_gpt_response(prompt)
                print(f"GPT: {gpt_reply}")

                # Save to memory
                save_to_memory(user_input, gpt_reply)
                
                # Speak out the reply
                speak_text(gpt_reply)
            else:
                # If intent was handled, we don't need to generate a new response
                continue

    except sr.UnknownValueError:
        print("Couldn't understood. Can you try again?")
    except sr.RequestError:
        print("Couldn't connect the API.")
    except KeyboardInterrupt:
        print("Exiting...")
        break
    except Exception as e:
        print(f"Unexpected error: {str(e)}")