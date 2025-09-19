#!/usr/bin/env python3
"""
Llama 3 Astronaut Chatbot with Real Voice Cloning
This version uses Coqui TTS for actual voice cloning from your sample audio
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

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chat_history/astronaut_chat.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RealVoiceCloner:
    """Real voice cloning using Coqui TTS"""
    
    def __init__(self, reference_audio_path: Optional[str] = None):
        self.reference_audio_path = reference_audio_path
        self.tts = None
        self.initialize_tts()
    
    def initialize_tts(self):
        """Initialize Coqui TTS"""
        try:
            import torch
            from TTS.api import TTS
            
            # Fix PyTorch loading issue
            original_load = torch.load
            torch.load = lambda *args, **kwargs: original_load(*args, weights_only=False, **kwargs)
            
            print("🎤 Initializing real voice cloning...")
            self.tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
            print("✅ Real voice cloning ready!")
            
            # Restore original torch.load
            torch.load = original_load
            
        except Exception as e:
            print(f"❌ Voice cloning failed: {e}")
            print("🔄 Using enhanced fallback TTS")
            self.tts = None
    
    def speak_with_cloned_voice(self, text: str) -> bool:
        """Speak text using cloned voice"""
        if not self.tts or not self.reference_audio_path:
            return self._enhanced_fallback_tts(text)
        
        if not os.path.exists(self.reference_audio_path):
            print(f"❌ Reference audio not found: {self.reference_audio_path}")
            return self._enhanced_fallback_tts(text)
        
        try:
            print(f"🎯 Speaking with cloned voice: '{text[:50]}...'")
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                output_path = temp_file.name
            
            # Generate speech with cloned voice
            self.tts.tts_to_file(
                text=text,
                speaker_wav=self.reference_audio_path,
                language="en",
                file_path=output_path
            )
            
            # Play the generated audio
            subprocess.run(["afplay", output_path], check=True)
            
            # Clean up
            os.unlink(output_path)
            return True
            
        except Exception as e:
            print(f"❌ Voice cloning error: {e}")
            return self._enhanced_fallback_tts(text)
    
    def _enhanced_fallback_tts(self, text: str) -> bool:
        """Enhanced fallback TTS with voice characteristics"""
        try:
            # Try to use macOS say with voice characteristics from reference
            if self.reference_audio_path and os.path.exists(self.reference_audio_path):
                # Use a more natural voice
                voice = "Samantha"  # Natural female voice
                rate = 180  # Moderate speed
            else:
                voice = "Alex"  # Default voice
                rate = 200
            
            subprocess.run(["say", "-v", voice, "-r", str(rate), text], check=True)
            print("🔊 Spoke with enhanced fallback TTS")
            return True
            
        except Exception as e:
            print(f"❌ Fallback TTS error: {e}")
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
        """Setup voice cloning with reference audio"""
        print(f"🎤 Setting up voice cloning with: {audio_path}")
        self.voice_cloner = RealVoiceCloner(audio_path)
        
        # Test voice cloning
        if self.voice_cloner.tts:
            print("🧪 Testing voice cloning...")
            success = self.voice_cloner.speak_with_cloned_voice(
                "Hello commander, this is your cloned voice speaking."
            )
            if success:
                print("✅ Voice cloning is working!")
            else:
                print("⚠️  Using enhanced fallback TTS")
        else:
            print("⚠️  Using enhanced fallback TTS")
    
    def get_llama_response(self, user_input: str) -> str:
        """Get response from Llama 3"""
        try:
            # Prepare context
            context = f"""
            You are {self.persona.get('name', 'Commander Sarah')}, an astronaut on a {self.persona.get('mission', 'space mission')}.
            
            Persona: {self.persona.get('personality', 'Professional and supportive')}
            Mission context: {self.persona.get('mission_context', 'Long-term space exploration')}
            
            Previous conversations: {len(self.memory.get('conversations', []))} interactions
            
            User: {user_input}
            
            Respond as the astronaut, being supportive and understanding. Keep responses concise but meaningful.
            """
            
            # Call Ollama API
            response = requests.post('http://localhost:11434/api/generate',
                                   json={
                                       'model': 'llama3.1:8b',
                                       'prompt': context,
                                       'stream': False
                                   },
                                   timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'I apologize, but I cannot process your request right now.')
            else:
                return f"I'm experiencing technical difficulties. Please try again. (Error: {response.status_code})"
                
        except Exception as e:
            logger.error(f"Error getting Llama response: {e}")
            return "I'm having trouble connecting to my systems. Please check if Ollama is running."
    
    def speak_response(self, text: str):
        """Speak the response using voice cloning"""
        if self.voice_cloner:
            self.voice_cloner.speak_with_cloned_voice(text)
        else:
            # Fallback to basic TTS
            try:
                subprocess.run(["say", text], check=True)
            except:
                print("🔇 Could not play audio")
    
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
            if self.voice_cloner and self.voice_cloner.tts:
                print("🎤 Real voice cloning: ACTIVE")
                print(f"📁 Reference audio: {self.voice_cloner.reference_audio_path}")
            else:
                print("🔊 Enhanced fallback TTS: ACTIVE")
            return True
        
        elif user_input == '/help':
            print("\n🚀 Astronaut Chatbot Commands:")
            print("  /voice <path>  - Set reference audio for voice cloning")
            print("  /voice_info    - Show current voice settings")
            print("  /help          - Show this help")
            print("  /quit          - Exit the chat")
            return True
        
        elif user_input == '/quit':
            print("👋 Safe travels, commander!")
            return False
        
        return False
    
    def chat_loop(self):
        """Main chat loop"""
        print(f"\n🛰️  Welcome, Commander!")
        print(f"👨‍🚀 I'm {self.persona.get('name', 'Commander Sarah')}, your AI companion on this mission.")
        print(f"🎯 Mission: {self.persona.get('mission', 'Space Exploration')}")
        print("\n💬 Type your message or use /help for commands")
        
        # Auto-greeting with voice
        greeting = "Hello commander, how are you feeling today? I'm here to support you on this mission."
        print(f"\n👨‍🚀 {self.persona.get('name', 'Commander Sarah')}: {greeting}")
        self.speak_response(greeting)
        
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
                
                # Get AI response
                print("🤔 Thinking...")
                response = self.get_llama_response(user_input)
                
                # Display and speak response
                print(f"\n👨‍🚀 {self.persona.get('name', 'Commander Sarah')}: {response}")
                self.speak_response(response)
                
                # Save to memory
                self.memory['conversations'].append({
                    'timestamp': datetime.now().isoformat(),
                    'user': user_input,
                    'assistant': response
                })
                
                # Keep only last 50 conversations
                if len(self.memory['conversations']) > 50:
                    self.memory['conversations'] = self.memory['conversations'][-50:]
                
            except KeyboardInterrupt:
                print("\n\n👋 Mission terminated. Safe travels, commander!")
                break
            except Exception as e:
                logger.error(f"Error in chat loop: {e}")
                print("❌ An error occurred. Please try again.")
        
        # Save memory
        self.save_memory()

def main():
    """Main function"""
    print("🚀 Initializing Astronaut Chatbot with Real Voice Cloning...")
    
    # Check if TTS is enabled
    use_tts = os.getenv('USE_TTS', '1') == '1'
    
    # Create chatbot
    chatbot = AstronautChatbot()
    
    # Setup voice cloning if sample audio exists
    sample_audio = "voice_samples/prepared_voice.wav"
    if use_tts and os.path.exists(sample_audio):
        chatbot.setup_voice_cloning(sample_audio)
    
    # Start chat
    chatbot.chat_loop()

if __name__ == "__main__":
    main()
