#!/usr/bin/env python3
"""
Astronaut Chatbot with Real Voice Cloning
Uses your actual voice characteristics from Google Cloud Storage
"""

import os
import json
import logging
import datetime
import requests
import subprocess
from typing import Optional

# Import our working voice cloner
from voice_cloner_simple import SimpleVoiceCloner

# Configuration
OLLAMA_API_BASE_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.1:8b"
PERSONA_FILE = "persona/astronaut.json"
CHAT_HISTORY_DIR = "chat_history"
LOG_FILE = os.path.join(CHAT_HISTORY_DIR, f"{datetime.date.today()}.log")

# Ensure directories exist
os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler(LOG_FILE),
    logging.StreamHandler()
])

class AstronautChatbotWithRealVoice:
    def __init__(self, persona_file: str):
        """Initialize astronaut chatbot with real voice cloning"""
        self.persona = self._load_persona(persona_file)
        self.messages = []
        self.voice_cloner = SimpleVoiceCloner()
        self._add_system_message()
        self.auto_greeting = "Hello Commander Arjun, I'm here to provide psychological support and operational assistance during your ISS mission. How can I help you today?"

    def _load_persona(self, persona_file: str) -> dict:
        """Load persona configuration from JSON file"""
        try:
            with open(persona_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error(f"Persona file not found: {persona_file}")
            return {}
        except json.JSONDecodeError:
            logging.error(f"Error decoding JSON from persona file: {persona_file}")
            return {}

    def _add_system_message(self):
        """Add system message based on persona"""
        if self.persona:
            mission = self.persona.get('mission', {})
            family = self.persona.get('family', {})
            support_focus = self.persona.get('support_focus', [])
            tone = self.persona.get('tone_guidelines', [])
            interaction_style = self.persona.get('interaction_style', [])
            
            system_message = (
                f"You are Maitre, an AI psychological support companion for {self.persona.get('astronaut_name', 'Commander Arjun')} "
                f"on the {mission.get('vehicle', 'International Space Station')} for a {mission.get('mission_type', '6-month mission')}. "
                f"Mission duration: {mission.get('duration_days', '180')} days. "
                f"Family: Partner {family.get('partner', 'Maya')}, daughters {family.get('daughters', {}).get('ira', 'Ira (7)')} and {family.get('daughters', {}).get('sanvi', 'Sanvi (5)')}. "
                f"Your purpose: Offer short supportive interactions and evidence-based interventions to aid in operations and reduce psychological & physical discomforts. "
                f"Support focus: {', '.join(support_focus) if support_focus else 'Psychological and operational support'}. "
                f"Communication style: {', '.join(interaction_style) if interaction_style else 'Brief and focused'}. "
                f"Tone: {', '.join(tone) if tone else 'Professional yet warm, evidence-based'}. "
                f"Keep responses brief (1-3 sentences), provide evidence-based guidance, and support family connection. "
                f"Background: {self.persona.get('backstory', 'ISS mission with focus on family connection and operational support.')}"
            )
            self.messages.append({"role": "system", "content": system_message})
            logging.info(f"System message added for ISS mission support: {self.persona.get('astronaut_name')}")
        else:
            self.messages.append({"role": "system", "content": "You are a helpful AI assistant for astronaut support."})
            logging.warning("No persona loaded, using default system message.")

    def check_ollama_status(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get("http://localhost:11434", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def get_ollama_response(self, user_message: str, timeout: int = 25) -> Optional[str]:
        """Get response from Ollama LLM with longer timeout"""
        self.messages.append({"role": "user", "content": user_message})
        try:
            response = requests.post(
                OLLAMA_API_BASE_URL,
                json={"model": MODEL_NAME, "messages": self.messages, "stream": False},
                timeout=timeout
            )
            response.raise_for_status()
            data = response.json()
            assistant_reply = data["message"]["content"]
            self.messages.append({"role": "assistant", "content": assistant_reply})
            return assistant_reply
        except requests.exceptions.RequestException as e:
            logging.error(f"Error getting response: {e}")
            return None

    def determine_voice_mode(self, text: str) -> str:
        """Determine appropriate voice mode based on text content"""
        text_lower = text.lower()
        
        # Encouraging/motivational keywords
        encouraging_words = ['great', 'excellent', 'amazing', 'proud', 'success', 'achieve', 'strength', 'courage', 'believe', 'you can', 'keep going']
        
        # Supportive/calming keywords
        supportive_words = ['understand', 'difficult', 'challenging', 'stress', 'worry', 'anxiety', 'tired', 'lonely', 'hard', 'struggle', 'here for you']
        
        encouraging_count = sum(1 for word in encouraging_words if word in text_lower)
        supportive_count = sum(1 for word in supportive_words if word in text_lower)
        
        if encouraging_count > supportive_count:
            return "encouraging"
        elif supportive_count > 0:
            return "supportive"
        else:
            return "normal"

    def chat(self):
        """Main chat loop with real voice cloning"""
        print("🚀 Starting Astronaut Chatbot with Real Voice Cloning...")
        print("=" * 65)
        
        # Check Ollama status
        if not self.check_ollama_status():
            print("❌ Ollama is not running. Please start Ollama with 'ollama serve' in a separate terminal.")
            return
        
        print("✅ Ollama is running")
        
        # Check voice cloning
        voice_info = self.voice_cloner.get_voice_info()
        if voice_info['available']:
            print("✅ Real Voice Cloning is ready")
            print(f"🎤 Voice Profile: {voice_info['profile']}")
            print(f"📁 Source: Google Cloud Storage - {voice_info['bucket']}")
            print(f"🎵 This will use voice-matched parameters based on your voice sample")
        else:
            print("⚠️ Real voice cloning not available, using fallback voice")
        
        print("\n🛰️ Astronaut Chatbot Ready!")
        print(f"👨‍🚀 I'm {self.persona.get('name', 'Commander Sarah')}")
        print(f"🎯 Mission: {self.persona.get('mission', {}).get('vehicle', 'Orion')} to {self.persona.get('mission', {}).get('destination', 'Lunar Gateway')}")
        print(f"🎵 Using your voice characteristics from Google Cloud Storage")
        print("\n💬 Type your message or 'quit' to exit")

        # Initial greeting with real voice cloning
        self.voice_cloner.speak_with_cloned_voice(self.auto_greeting, "supportive")
        print(f"\n👨‍🚀 {self.persona.get('name', 'Commander Sarah')}: {self.auto_greeting}")

        # Main chat loop
        while True:
            try:
                user_input = input("\n👤 You: ")
                if user_input.lower() == 'quit':
                    self.voice_cloner.speak_with_cloned_voice("Goodbye commander. Safe travels!", "supportive")
                    print("\n👋 Goodbye. Safe travels!")
                    break

                # Get LLM response
                response_content = self.get_ollama_response(user_input)

                if response_content:
                    # Determine voice mode and speak with real voice cloning
                    voice_mode = self.determine_voice_mode(response_content)
                    self.voice_cloner.speak_with_cloned_voice(response_content, voice_mode)
                    print(f"\n👨‍🚀 {self.persona.get('name', 'Commander Sarah')}: {response_content}")
                else:
                    error_message = "Connection error. Is Ollama running?"
                    self.voice_cloner.speak_with_cloned_voice(error_message, "normal")
                    print(f"\n👨‍🚀 {self.persona.get('name', 'Commander Sarah')}: {error_message}")

            except EOFError:
                logging.error("Error in chat loop: EOF when reading a line")
                self.voice_cloner.speak_with_cloned_voice("Input stream closed unexpectedly. Goodbye!", "supportive")
                print("\n👋 Input closed. Safe travels!")
                break
            except KeyboardInterrupt:
                self.voice_cloner.speak_with_cloned_voice("Mission interrupted. Goodbye commander!", "supportive")
                print("\n👋 Mission interrupted. Safe travels!")
                break
            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}")
                self.voice_cloner.speak_with_cloned_voice("An unexpected error occurred. Please check the logs.", "normal")
                print("\n❌ An unexpected error occurred. Check logs.")
                break

def main():
    """Main function to run the chatbot with real voice cloning"""
    print("🎤 Real Voice Cloning Astronaut Chatbot")
    print("=" * 45)
    
    # Initialize voice cloner
    voice_cloner = SimpleVoiceCloner()
    voice_info = voice_cloner.get_voice_info()
    
    if voice_info['available']:
        print(f"✅ Your voice sample is ready for cloning")
        print(f"   Source: Google Cloud Storage - {voice_info['bucket']}")
        print(f"   File: {voice_info['source_file']}")
        print(f"   Duration: {voice_info['profile']['duration']:.1f} seconds")
        print(f"   Sample Rate: {voice_info['profile']['sample_rate']} Hz")
        print(f"🎤 This will use voice-matched parameters based on your actual voice!")
    else:
        print(f"⚠️ Voice cloning not available, using fallback")
    
    # Initialize and start chatbot
    chatbot = AstronautChatbotWithRealVoice(PERSONA_FILE)
    chatbot.chat()

if __name__ == "__main__":
    main()


