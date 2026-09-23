Import tkinter as tk
from tkinter import scrolledtext
from threading import Thread
import wikipediaapi
import requests
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import re

# ---------- Predefined Responses ----------

responses = {
    "yo": "What's up 😎",
    "hi": "Hey buddy 😎",
    "namaste": "Namaste! Aap kaise hain?",
    "hello": "Hey! How are you doing?",
    "how are you": "I'm just a program, but I'm feeling great 😄",
    "your name": "People call me AceAI, but you can call me Ace",
    "what is python": "Python is a beginner-friendly programming language.",
    "who made you": "I was created by my developer, Utsav Gulia."
}

# ---------- Wikipedia Setup ----------

wiki = wikipediaapi.Wikipedia(
    user_agent="AceAI-Chatbot/1.0 (https://github.com/UtsavGulia/AceAI-Chatbot)",
    language='en'
)

question_keywords = [
    "who is", "what is", "where is", "when is", "why is", "how is",
    "who was", "where was", "when was", "why was", "how was", "tell me about"
]

def get_wiki_summary(topic, sentences=300):
    page = wiki.page(topic)
    if not page.exists():
        return f"Sorry, I couldn't find info on '{topic}'."
    summary = page.summary
    if "may refer to" in summary[:50].lower():
        options = page.links
        if options:
            first_option = list(options.keys())[0]
            return f"This page may refer to multiple topics. Showing first option: {first_option}\n\n" + \
                   wiki.page(first_option).summary[:sentences]
        return "This page may refer to multiple topics."
    return summary[:sentences]

# ---------- API-Based Fun Features ----------

def get_joke():
    try:
        data = requests.get("https://official-joke-api.appspot.com/random_joke", timeout=5).json()
        return f"{data['setup']} {data['punchline']}"
    except Exception:
        return "Sorry, I couldn't fetch a joke right now."

def get_fun_fact():
    try:
        data = requests.get("https://uselessfacts.jsph.pl/random.json?language=en", timeout=5).json()
        return data.get('text', "No fact found.")
    except Exception:
        return "Sorry, I couldn't fetch a fun fact right now."

def get_quote():
    try:
        data = requests.get("https://zenquotes.io/api/random", timeout=5).json()
        return f'"{data[0]["q"]}" — {data[0]["a"]}'
    except Exception:
        return "Sorry, I couldn't fetch a quote right now."

def get_weather(city):
    try:
        return requests.get(f"https://wttr.in/{city}?format=3", timeout=5).text
    except Exception:
        return "Sorry, I couldn't fetch weather right now."

def get_dictionary(word):
    try:
        data = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}", timeout=5).json()
        if isinstance(data, list):
            d = data[0]['meanings'][0]['definitions'][0]
            result = f"Meaning: {d['definition']}"
            if d.get('example'):
                result += f"\nExample: {d['example']}"
            if d.get('synonyms'):
                result += f"\nSynonyms: {', '.join(d['synonyms'])}"
            if d.get('antonyms'):
                result += f"\nAntonyms: {', '.join(d['antonyms'])}"
            return result
        return "Sorry, I couldn't find that word."
    except Exception:
        return "Sorry, I couldn't fetch the word info."

# ---------- Load AI Models ----------

print("⏳ Loading AI models... this may take a moment...")
dgpt_tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
dgpt_model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-small")
dgpt_history = None

smol_tokenizer = AutoTokenizer.from_pretrained("HuggingFaceTB/SmolLM2-360M-Instruct")
smol_model = AutoModelForCausalLM.from_pretrained("HuggingFaceTB/SmolLM2-360M-Instruct")
device = "cuda" if torch.cuda.is_available() else "cpu"
smol_model.to(device)
smol_history = []

print("✅ AI models loaded!")

# ---------- Helper Functions ----------

def is_senseless(reply):
    if not reply or len(reply.strip()) < 3 or len(reply.split()) < 5:
        return True
    generic_phrases = ["I am a chatbot", "I cannot", "I don't have", "I'm just a program"]
    return any(p.lower() in reply.lower() for p in generic_phrases) or bool(re.search(r"[^a-zA-Z0-9 ,.!?']", reply))

def process_wiki_request(user_input):
    topic = user_input
    for keyword in question_keywords:
        if user_input.lower().startswith(keyword):
            topic = user_input.lower().replace(keyword, "").strip()
            break
    return get_wiki_summary(topic)

# ---------- Tkinter GUI Setup ----------

root = tk.Tk()
root.title("AceAI Chatbot")
root.geometry("650x750")
root.configure(bg="#2E2E2E")

# Chat display
chat_window = scrolledtext.ScrolledText(
    root, wrap=tk.WORD, state='disabled',
    font=("Helvetica", 12), bg="#1C1C1C", fg="white"
)
chat_window.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# User input
user_entry = tk.Entry(root, font=("Helvetica", 14), bg="#333333", fg="white", insertbackground="white")
user_entry.pack(padx=10, pady=(0, 10), fill=tk.X)

current_ai = "dialo"

# ---------- Send Message Logic ----------

def send_message(event=None):
    user_text = user_entry.get().strip()
    if not user_text:
        return
    chat_window.config(state='normal')
    chat_window.insert(tk.END, f"You: {user_text}\n", "user")
    chat_window.config(state='disabled')
    chat_window.yview(tk.END)
    user_entry.delete(0, tk.END)

    # Use a thread for AI/API response
    Thread(target=generate_response, args=(user_text,)).start()

def generate_response(user_text):
    global dgpt_history, smol_history, current_ai
    response = ""

    # Predefined responses & fun commands
    if user_text.lower() in responses:
        response = responses[user_text.lower()]
    elif "joke" in user_text.lower():
        response = get_joke()
    elif "quote" in user_text.lower():
        response = get_quote()
    elif "weather in" in user_text.lower():
        city = user_text.lower().replace("weather in", "").strip()
        response = get_weather(city)
    elif "fun fact" in user_text.lower() or "fact" in user_text.lower():
        response = get_fun_fact()
    elif user_text.lower().startswith("define "):
        word = user_text.lower().replace("define ", "").strip()
        response = get_dictionary(word)
    elif any(user_text.lower().startswith(q) for q in question_keywords):
        response = process_wiki_request(user_text)
    else:
        # AI fallback logic
        if current_ai == "dialo":
            try:
                new_input_ids = dgpt_tokenizer.encode(user_text + dgpt_tokenizer.eos_token, return_tensors='pt')
                bot_input_ids = torch.cat([dgpt_history, new_input_ids], dim=-1) if dgpt_history is not None else new_input_ids
                dgpt_history = dgpt_model.generate(bot_input_ids, max_length=250, pad_token_id=dgpt_tokenizer.eos_token_id)
                response = dgpt_tokenizer.decode(dgpt_history[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
            except Exception:
                response = ""
            if is_senseless(response):
                current_ai = "smol"
                smol_history.append({"role": "user", "content": user_text})

        if current_ai == "smol":
            try:
                smol_history.append({"role": "user", "content": user_text})
                inputs = smol_tokenizer.apply_chat_template(
                    smol_history,
                    add_generation_prompt=True,
                    tokenize=True,
                    return_dict=True,
                    return_tensors="pt",
                ).to(device)
                outputs = smol_model.generate(**inputs, max_new_tokens=150)
                response = smol_tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:], skip_special_tokens=True)
                smol_history.append({"role": "assistant", "content": response})
            except Exception:
                response = "Sorry, SmolLM couldn't generate a response."

    # Insert response into chat window
    chat_window.config(state='normal')
    chat_window.insert(tk.END, f"AceAI: {response}\n\n", "bot")
    chat_window.tag_config("user", foreground="#ADD8E6")
    chat_window.tag_config("bot", foreground="#FFFFFF")
    chat_window.config(state='disabled')
    chat_window.yview(tk.END)

# Bindings & Buttons
user_entry.bind("<Return>", send_message)

send_button = tk.Button(
    root, text="Send", command=send_message,
    font=("Helvetica", 12), bg="#444444", fg="white"
)
send_button.pack(padx=10, pady=(0, 10))

root.mainloop()