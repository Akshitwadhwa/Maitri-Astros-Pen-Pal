#!/usr/bin/env python3
"""
Robust Astronaut Chatbot - Fixed Input Handling
No more EOF errors!
"""

import os
import sys
import json
import requests
import logging
from datetime import datetime
from typing import Optional, List
import subprocess
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AstronautChatbot:
    def __init__(self):
        self.persona = self.load_persona()
        self.memory = self.load_memory()
        
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
    
    def get_llama_response(self, user_input: str) -> str:
        """Get response from Llama 3"""
        try:
            # Simple context for faster response
            context = f"""You are {self.persona.get('name', 'Commander Sarah')}, an astronaut. 
            Be supportive and concise. User: {user_input}"""
            
            response = requests.post('http://localhost:11434/api/generate',
                                   json={
                                       'model': 'llama3.1:8b',
                                       'prompt': context,
                                       'stream': False,
                                       'options': {
                                           'num_predict': 80,  # Short responses
                                           'temperature': 0.7
                                       }
                                   },
                                   timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'I cannot process that right now.').strip()
            else:
                return "System error. Please try again."
                
        except Exception as e:
            logger.error(f"Error getting response: {e}")
            return "Connection error. Is Ollama running?"
    
    def speak_response(self, text: str):
        """Speak response using macOS say"""
        try:
            # Use fast, natural voice
            subprocess.run(["say", "-v", "Samantha", "-r", "180", text], 
                         check=True, timeout=5)
        except Exception as e:
            logger.error(f"Speech error: {e}")
    
    def handle_commands(self, user_input: str) -> bool:
        """Handle special commands"""
        if user_input == '/help':
            print("\n🚀 Astronaut Chatbot Commands:")
            print("  /help    - Show this help")
            print("  /quit    - Exit the chat")
            print("  /status  - Show system status")
            return True
        
        elif user_input == '/status':
            print(f"👨‍🚀 Name: {self.persona.get('name', 'Commander Sarah')}")
            print(f"🎯 Mission: {self.persona.get('mission', 'Space Exploration')}")
            print(f"💬 Conversations: {len(self.memory.get('conversations', []))}")
            print("🔊 Voice: macOS Samantha (180 WPM)")
            return True
        
        elif user_input == '/quit':
            print("👋 Safe travels, commander!")
            return False
        
        return False
    
    def safe_input(self, prompt: str) -> str:
        """Safe input function that handles EOF errors"""
        try:
            # Check if stdin is available
            if not sys.stdin.isatty():
                # If not interactive, wait for input differently
                print("⚠️  Interactive mode required. Please run in terminal.")
                return "/quit"
            
            user_input = input(prompt).strip()
            return user_input
            
        except EOFError:
            print("\n⚠️  Input stream closed. Exiting...")
            return "/quit"
        except KeyboardInterrupt:
            print("\n\n👋 Mission terminated by user. Safe travels!")
            return "/quit"
        except Exception as e:
            logger.error(f"Input error: {e}")
            return "/quit"
    
    def chat_loop(self):
        """Robust chat loop with proper error handling"""
        print(f"\n🛰️  Astronaut Chatbot Ready!")
        print(f"👨‍🚀 I'm {self.persona.get('name', 'Commander Sarah')}")
        print(f"🎯 Mission: {self.persona.get('mission', 'Space Exploration')}")
        print("\n💬 Type your message or /help for commands")
        
        # Quick greeting
        greeting = "Hello commander, I'm ready to assist you on this mission."
        print(f"\n👨‍🚀 {self.persona.get('name', 'Commander Sarah')}: {greeting}")
        self.speak_response(greeting)
        
        while True:
            try:
                # Use safe input function
                user_input = self.safe_input("\n👤 You: ")
                
                if not user_input:
                    continue
                
                # Handle commands
                if self.handle_commands(user_input):
                    if user_input == '/quit':
                        break
                    continue
                
                # Get response
                print("🤔 Thinking...")
                start_time = time.time()
                
                response = self.get_llama_response(user_input)
                
                response_time = time.time() - start_time
                print(f"⚡ Response time: {response_time:.1f}s")
                
                # Display and speak response
                print(f"\n👨‍🚀 {self.persona.get('name', 'Commander Sarah')}: {response}")
                self.speak_response(response)
                
                # Save to memory
                self.memory['conversations'].append({
                    'timestamp': datetime.now().isoformat(),
                    'user': user_input,
                    'assistant': response
                })
                
                # Keep only last 10 conversations for speed
                if len(self.memory['conversations']) > 10:
                    self.memory['conversations'] = self.memory['conversations'][-10:]
                
            except Exception as e:
                logger.error(f"Chat loop error: {e}")
                print("❌ An error occurred. Please try again.")
                time.sleep(1)  # Brief pause before continuing
        
        # Save memory and exit
        self.save_memory()
        print("👋 Mission complete. Safe travels, commander!")

def main():
    """Main function with error handling"""
    try:
        print("🚀 Initializing Astronaut Chatbot...")
        
        # Check if Ollama is running
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if response.status_code != 200:
                print("❌ Ollama not running. Please start Ollama first:")
                print("   ollama serve")
                return
        except:
            print("❌ Cannot connect to Ollama. Please start Ollama first:")
            print("   ollama serve")
            return
        
        # Create and run chatbot
        chatbot = AstronautChatbot()
        chatbot.chat_loop()
        
    except KeyboardInterrupt:
        print("\n👋 Mission terminated. Safe travels!")
    except Exception as e:
        logger.error(f"Main error: {e}")
        print("❌ Fatal error. Please check logs.")

if __name__ == "__main__":
    main()
