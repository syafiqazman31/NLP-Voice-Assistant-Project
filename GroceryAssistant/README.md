# 🛒 Grocery & Pantry Assistant

**Course:** Natural Language Processing (NLP)  
**Project Theme:** AI Voice Assistant  
**Team Members:**
- MUHAMMAD SYAFIQ BIN NOR AZMAN (2213187)
- MUHAMMAD AFIQ BIN MOHD ASRI (2212541)
- MUHAMAD IZZUDIN BIN MUHAMAD (2219735)            
- LUQMAN AZFAR BIN AZMI (2219857)

---

## 📖 Project Overview

The **Grocery & Pantry Assistant** is a local, voice-activated AI system designed to track what you are running out of and build shopping lists automatically .

The system listens to your voice commands to add or remove items from your digital pantry. It uses a local Large Language Model (Llama 3) to understand natural language, categorize items, and even suggest recipes based on the ingredients you currently have in stock .

### ✨ Key Features

- **🗣️ Voice-Activated:** Hands-free operation using a "Push-to-Talk" interface .
- **🛒 Smart Inventory:** Adds and removes multiple items at once (e.g., _"Add chicken, eggs, and milk"_).
- **🧠 Local Intelligence:** Runs completely offline using **Ollama (Llama 3)**, ensuring privacy and zero cloud costs .
- **👨‍🍳 Recipe Suggestions:** Suggests dishes you can cook based _strictly_ on your current inventory.
- **💾 Auto-Categorization:** Uses a local dataset to categorize items (e.g., "Apple" → "Produce") .
- **🔊 Voice Feedback:** Confirms actions and reads recipes aloud using text-to-speech .

---

## 🛠️ System Architecture

1.  **Input:** User speaks into the microphone via the Streamlit interface.
2.  **STT (Speech-to-Text):** Google Speech Recognition converts audio to text .
3.  **Processing (Logic Layer):**
    - Python parses the text.
    - **LLM (Llama 3):** Analyzes intent (Add/Remove/Recipe) and extracts entities.
    - **Database:** Updates `pantry.txt` and queries `grocery_dataset.json` .
4.  **Output:**
    - **TTS (Text-to-Speech):** `pyttsx3` reads the response aloud .
    - **GUI:** Streamlit updates the pantry list visually in real-time.

---

## 🚀 How to Run Locally

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/) installed and running.
- Model downloaded: `ollama run llama3`

### Installation Steps

1.  **Clone the repository:**
   
```bash
git clone https://github.com/syafiqazman31/NLP-Voice-Assistant-Project.git
 ```
2.  **Create a Virtual Environment (Recommended):**

    ```bash
    python -m venv venv
    # Windows:
    .\venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Application:**
    Ensure Ollama is running in the background, then execute:
    ```bash
    streamlit run app.py
    ```

---

## 📂 File Structure

- `app.py`: The main application code (Frontend + Backend).
- `grocery_dataset.json`: A simple knowledge base for item categorization .
- `pantry.txt`: The text file acting as the database for your grocery list.
- `requirements.txt`: List of Python libraries required to run the project .

---

## 🤖 Technologies Used

- **LLM:** Meta Llama 3 (via Ollama)
- **Interface:** Streamlit
- **STT:** SpeechRecognition (Google API)
- **TTS:** pyttsx3
- **Language:** Python

---

## 🎥 Deliverables

This repository contains the source code, requirements, and instructions required for the NLP Course Project .

graph TD
    User([👤 User]) -->|Voice Command| UI[🖥️ Streamlit Interface]
    UI -->|Audio Input| STT[🗣️ Speech-to-Text API]
    STT -->|Transcribed Text| Logic[⚙️ Python Controller]
    
    subgraph "Local Intelligence"
        Logic <-->|Prompt & Response| LLM[🧠 Llama 3 (Ollama)]
        Logic <-->|Read & Update| DB[(📂 Pantry.txt & JSON)]
    end
    
    Logic -->|Response Text| TTS[🔊 Text-to-Speech Engine]
    TTS -->|Audio Output| User
    Logic -->|Visual Update| UI






