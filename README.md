# 🤖 AceAI — Intelligent Multi-Model Desktop Assistant

AceAI is a multi-threaded desktop chatbot built in Python. It features a hybrid AI architecture that dynamically falls back between lightweight conversational LLMs (DialoGPT-small and SmolLM2-360M-Instruct) while providing real-time data integration through external REST APIs and Wikipedia scraping.

---

## ✨ Key Features

- Hybrid Model Fallback Logic: Uses DialoGPT for fast dialog processing and automatically switches to SmolLM2-360M-Instruct if responses become incoherent or repetitive.
- Asynchronous GUI Execution: Multi-threaded request processing via threading.Thread prevents Tkinter UI freezes during LLM generation or API calls.
- Real-Time Data Integration:
  - Live weather forecasts (wttr.in)
  - Dictionary lookup and definitions (Dictionary API)
  - Wikipedia summary extraction with disambiguation handling
  - Random jokes, quotes, and fun facts via public APIs
- Dark-Themed GUI: Modern Tkinter user interface with distinct user/bot message color coding.

---

## 🛠️ Tech Stack

- GUI Framework: Python tkinter
- Machine Learning: PyTorch, HuggingFace Transformers
- Models: microsoft/DialoGPT-small, HuggingFaceTB/SmolLM2-360M-Instruct
- APIs & Scraping: requests, wikipedia-api

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- CUDA-capable GPU (Optional, recommended for faster inference)

### Installation

1. Clone the repository:
   '''bash
   git clone [https://github.com/YOUR_GITHUB_USERNAME/AceAI-Chatbot.git](https://github.com/utsavgulia/AceAI-Chatbot.git)
   cd AceAI-Chatbot