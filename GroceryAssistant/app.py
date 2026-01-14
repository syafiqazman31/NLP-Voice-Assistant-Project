# copy this line to terminal to run the AI : streamlit run app.py

import streamlit as st
import speech_recognition as sr
import pyttsx3
import requests
import json
import os
import time
from streamlit_mic_recorder import mic_recorder

# --- CONFIGURATION ---
DATA_FILE = "pantry.txt"
DATASET_FILE = "grocery_dataset.json" 
MODEL_NAME = "llama3" 

# --- INITIALIZATION ---
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
    
if 'last_audio_id' not in st.session_state:
    st.session_state.last_audio_id = None

# --- LOAD DATASET ---
GROCERY_DB = {}
if os.path.exists(DATASET_FILE):
    try:
        with open(DATASET_FILE, 'r') as f:
            content = f.read()
            if content.strip():
                GROCERY_DB = json.loads(content)
    except json.JSONDecodeError:
        pass

# --- FUNCTIONS ---

def speak(text):
    """Converts text to speech."""
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 170)
        engine.say(text)
        engine.runAndWait()
        if engine._inLoop:
            engine.endLoop()
    except Exception as e:
        print(f"Voice Error: {e}")

def transcribe_audio(file_path):
    r = sr.Recognizer()
    try:
        with sr.AudioFile(file_path) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data)
            return text.lower()
    except ValueError:
        st.error("Audio format error. Please try recording again.")
        return None
    except sr.UnknownValueError:
        st.warning("I didn't catch that. Could you say it again?")
        return None
    except sr.RequestError:
        st.error("Speech service down.")
        return None

def read_pantry():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        content = f.read()
    return [i.strip() for i in content.split(',')] if content else []

def update_pantry(item_name, action="add"):
    current_items = read_pantry()
    clean_name = item_name.lower().strip()

    if action == "add":
        if clean_name in GROCERY_DB:
            category = GROCERY_DB[clean_name]['category']
            entry = f"{clean_name} ({category})"
        else:
            entry = clean_name
        current_items.append(entry)
        
    elif action == "remove":
        current_items = [i for i in current_items if clean_name not in i.lower()]
    
    with open(DATA_FILE, "w") as f:
        f.write(", ".join(current_items))

def query_llm(user_input, pantry_context):
    # --- UPDATED PROMPT FOR RECIPE SUGGESTIONS ---
    system_instruction = f"""
    You are a smart Grocery & Chef Assistant. 
    The user's current pantry list is: [{pantry_context}].
    
    INSTRUCTIONS:
    1. ADDING ITEMS: If user wants to ADD, reply strictly: "ACTION: ADD item1, item2, item3".
    2. REMOVING ITEMS: If user wants to REMOVE, reply strictly: "ACTION: REMOVE item1, item2".
    3. RECIPES: If the user asks what to cook, suggest a dish using MAINLY the items in the current list. 
       - Mention which items they already have.
       - Mention 1 or 2 missing items they might need to buy.
       - Keep the recipe suggestion short (2-3 sentences max).
    4. GENERAL: Otherwise, answer the question normally.
    """
    
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": MODEL_NAME,
        "prompt": f"{system_instruction}\nUser: {user_input}\nAssistant:",
        "stream": False
    }

    try:
        response = requests.post(url, json=payload)
        return response.json()['response']
    except:
        return "I'm having trouble connecting to my brain."

# --- FRONTEND LAYOUT ---
st.set_page_config(page_title="Smart Grocery Assistant", layout="wide")

st.title("🛒 Smart Grocery & Pantry Assistant")
st.markdown("---")

col1, col2 = st.columns([2, 1])

# --- RIGHT COLUMN: LIST ---
with col2:
    st.header("📋 Current List")
    items = read_pantry()
    if items:
        for item in items:
            st.success(f"• {item.title()}")
    else:
        st.info("Your list is empty.")
        
    if st.button("Clear List"):
        with open(DATA_FILE, "w") as f: f.write("")
        st.rerun()

# --- LEFT COLUMN: CHAT ---
with col1:
    st.header("💬 Voice Command")
    st.info("Click 'Start Recording' to talk. Click 'Stop' when done.")
    
    audio = mic_recorder(
        start_prompt="⏺️ Start Recording",
        stop_prompt="⏹️ Stop Recording",
        key='recorder',
        format="wav"
    )

    if audio:
        current_audio_id = audio['bytes']
        
        # Check against last audio to prevent loops
        if current_audio_id == st.session_state.last_audio_id:
            pass 
        else:
            st.session_state.last_audio_id = current_audio_id
            
            with st.status("Processing Voice Command...", expanded=True) as status:
                
                status.write("💾 Saving audio file...")
                temp_filename = "temp_input.wav"
                with open(temp_filename, "wb") as f:
                    f.write(audio['bytes'])
                
                status.write("🎧 Transcribing audio...")
                user_text = transcribe_audio(temp_filename)

                if user_text:
                    st.write(f"**Recognized:** '{user_text}'")
                    st.session_state.chat_history.append({"role": "user", "content": user_text})
                    
                    status.write("🧠 Consulting AI Brain...")
                    current_list = ", ".join(read_pantry())
                    response = query_llm(user_text, current_list)
                    response_upper = response.upper()
                    
                    final_reply = response 
                    
                    # --- ACTION LOGIC ---
                    if "ACTION: ADD" in response_upper:
                        try:
                            raw_text = response_upper.split("ADD")[1]
                            raw_text = raw_text.replace(" AND ", ",")
                            items_to_add = [x.strip().replace(".", "") for x in raw_text.split(",") if x.strip()]
                            
                            status.write(f"📝 Adding: {items_to_add}")
                            for item in items_to_add:
                                update_pantry(item, "add")
                            
                            final_reply = f"I have added {', '.join(items_to_add)} to your list."
                        except:
                            final_reply = "I tried to add those items, but I got confused."
                        
                    elif "ACTION: REMOVE" in response_upper:
                        try:
                            raw_text = response_upper.split("REMOVE")[1]
                            raw_text = raw_text.replace(" AND ", ",")
                            items_to_remove = [x.strip().replace(".", "") for x in raw_text.split(",") if x.strip()]
                            
                            status.write(f"🗑️ Removing: {items_to_remove}")
                            for item in items_to_remove:
                                update_pantry(item, "remove")
                                
                            final_reply = f"I have removed {', '.join(items_to_remove)} from your list."
                        except:
                            final_reply = "I tried to remove those items, but I got confused."

                    st.session_state.chat_history.append({"role": "assistant", "content": final_reply})
                    
                    status.update(label="✅ Processing Complete!", state="complete", expanded=False)

                    st.success(f"🔊 AI Says: {final_reply}")
                    speak(final_reply)
                    
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)

                    time.sleep(1) 
                    st.rerun()
                else:
                    status.update(label="❌ No speech detected", state="error")

    st.markdown("### Conversation History")
    for chat in reversed(st.session_state.chat_history):
        if chat["role"] == "user":
            st.info(f"👤 **You:** {chat['content']}")
        else:
            st.warning(f"🤖 **Assistant:** {chat['content']}")