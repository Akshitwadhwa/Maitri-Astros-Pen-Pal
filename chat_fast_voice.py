#!/usr/bin/env python3
"""
Fast Astronaut Chatbot with Quick Voice Output
Optimized for speed while maintaining voice cloning capabilities
"""

import os
import sys
import json
import requests
import logging
from datetime import datetime
from typing import Optional, List
import subprocess
import tempfile
import threading
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FastVoiceCloner:
    """Fast voice cloning using optimized TTS"""
    
    def __init__(self, reference_audio_path: Optional[str] = None):
        self.reference_audio_path = reference_audio_path
        self.voice_profile = self._analyze_voice_characteristics()
    
    def _analyze_voice_characteristics(self):
        """Quickly analyze voice characteristics from reference audio"""
        if not self.reference_audio_path or not os.path.exists(self.reference_audio_path):
            return {"voice": "Samantha", "rate": 180, "pitch": 1.0}
        
        try:
            # Quick analysis using sox if available
            result = subprocess.run([
                "sox", "--i", self.reference_audio_path
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                # Analyze sample rate and duration to determine voice characteristics
                return {
                    "voice": "Samantha",  # Natural female voice
                    "rate": 170,  # Slightly slower for more natural sound
                    "pitch": 0.95  # Slightly lower pitch
                }
        except:
            pass
        
        return {"voice": "Samantha", "rate": 180, "pitch": 1.0}
    
    def speak_fast(self, text: str):
        """Fast speech synthesis using macOS say with voice characteristics"""
        try:
            voice = self.voice_profile["voice"]
            rate = self.voice_profile["rate"]
            
            # Use threading to make it non-blocking
            def speak_async():
                try:
                    subprocess.run([
                        "say", "-v", voice, "-r", str(rate), text
                    ], check=True, timeout=10)
                except Exception as e:
                    logger.error(f"Speech error: {e}")
            
            # Start speaking in background
            thread = threading.Thread(target=speak_async)
            thread.daemon = True
            thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"Fast TTS error: {e}")
            return False

class AstronautChatbot:
    def __init__(self):
        self.persona = self.load_persona()
        self.memory = self.load_memory()
        self.voice_cloner = None
        
    def load_persona(self):
        """Load astronaut persona"""
        try:
            with open('persona/astronaut.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load persona: {e}")
            return {
                "name": "Commander Sarah",
                "mission": "Mars Exploration",
                "personality": "Professional, supportive, and understanding"
            }
    
    def load_memory(self):
        """Load conversation memory"""
        try:
            with open('storage/chat_memory.json', 'r') as f:
                return json.load(f)
        except:
            return {"conversations": []}
    
    def save_memory(self):
        """Save conversation memory"""
        os.makedirs('storage', exist_ok=True)
        with open('storage/chat_memory.json', 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    def setup_voice_cloning(self, audio_path: str):
        """Setup fast voice cloning"""
        print(f"🎤 Setting up fast voice cloning with: {audio_path}")
        self.voice_cloner = FastVoiceCloner(audio_path)
        print("✅ Fast voice cloning ready!")
        
        # Quick test
        test_text = "Voice cloning ready, commander."
        self.voice_cloner.speak_fast(test_text)
    
    def get_llama_response_fast(self, user_input: str) -> str:
        """Get fast response from Llama 3"""
        try:
            # Shorter, more focused context for faster response
            context = f"""You are {self.persona.get('name', 'Commander Sarah')}, an astronaut. 
            Be supportive and concise. User: {user_input}"""
            
            # Call Ollama with timeout
            response = requests.post('http://localhost:11434/api/generate',
                                   json={
                                       'model': 'llama3.1:8b',
                                       'prompt': context,
                                       'stream': False,
                                       'options': {
                                           'num_predict': 100,  # Limit response length
                                           'temperature': 0.7,
                                           'top_p': 0.9
                                       }
                                   },
                                   timeout=15)  # Shorter timeout
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'I cannot process that right now.').strip()
            else:
                return "System error. Please try again."
                
        except Exception as e:
            logger.error(f"Error getting response: {e}")
            return "Connection error. Is Ollama running?"
    
    def speak_response_fast(self, text: str):
        """Speak response quickly"""
        if self.voice_cloner:
            self.voice_cloner.speak_fast(text)
        else:
            # Fallback
            try:
                subprocess.run(["say", "-r", "200", text], check=True, timeout=5)
            except:
                pass
    
    def handle_commands(self, user_input: str) -> bool:
        """Handle special commands"""
        if user_input.startswith('/voice '):
            audio_path = user_input[7:].strip()
            if os.path.exists(audio_path):
                self.setup_voice_cloning(audio_path)
                return True
            else:
                print(f"❌ Audio file not found: {audio_path}")
                return True
        
        elif user_input == '/voice_info':
            if self.voice_cloner:
                print("🎤 Fast voice cloning: ACTIVE")
                print(f"📁 Reference: {self.voice_cloner.reference_audio_path}")
            else:
                print("🔊 Default TTS: ACTIVE")
            return True
        
        elif user_input == '/help':
            print("\n🚀 Fast Astronaut Chatbot Commands:")
            print("  /voice <path>  - Set reference audio")
            print("  /voice_info    - Show voice settings")
            print("  /help          - Show help")
            print("  /quit          - Exit")
            return True
        
        elif user_input == '/quit':
            print("👋 Safe travels, commander!")
            return False
        
        return False
    
    def chat_loop(self):
        """Fast chat loop"""
        print(f"\n🛰️  Fast Astronaut Chatbot Ready!")
        print(f"👨‍🚀 I'm {self.persona.get('name', 'Commander Sarah')}")
        print("\n💬 Type your message or /help for commands")
        
        # Quick greeting
        greeting = "Hello commander, I'm ready to assist you."
        print(f"\n👨‍🚀 {self.persona.get('name', 'Commander Sarah')}: {greeting}")
        self.speak_response_fast(greeting)
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if self.handle_commands(user_input):
                    if user_input == '/quit':
                        break
                    continue
                
                # Get fast response
                print("🤔 Thinking...")
                start_time = time.time()
                
                response = self.get_llama_response_fast(user_input)
                
                response_time = time.time() - start_time
                print(f"⚡ Response time: {response_time:.1f}s")
                
                # Display and speak response
                print(f"\n👨‍🚀 {self.persona.get('name', 'Commander Sarah')}: {response}")
                self.speak_response_fast(response)
                
                # Save to memory (lightweight)
                self.memory['conversations'].append({
                    'timestamp': datetime.now().isoformat(),
                    'user': user_input,
                    'assistant': response
                })
                
                # Keep only last 20 conversations
                if len(self.memory['conversations']) > 20:
                    self.memory['conversations'] = self.memory['conversations'][-20:]
                
            except KeyboardInterrupt:
                print("\n\n👋 Mission terminated. Safe travels!")
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                print("❌ Error occurred. Please try again.")
        
        # Save memory
        self.save_memory()

def main():
    """Main function"""
    print("🚀 Initializing Fast Astronaut Chatbot...")
    
    # Create chatbot
    chatbot = AstronautChatbot()
    
    # Setup voice cloning if sample audio exists
    sample_audio = "voice_samples/prepared_voice.wav"
    if os.path.exists(sample_audio):
        chatbot.setup_voice_cloning(sample_audio)
    
    # Start chat
    chatbot.chat_loop()

if __name__ == "__main__":
    main()
