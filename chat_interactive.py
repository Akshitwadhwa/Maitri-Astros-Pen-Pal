#!/usr/bin/env python3
"""
Interactive Astronaut Chatbot - Optimized for terminal use
"""

import os
import sys
import json
import requests
import subprocess
from datetime import datetime

class InteractiveChatbot:
    def __init__(self):
        self.persona = self.load_persona()
        self.running = True
        
    def load_persona(self):
        """Load astronaut persona"""
        try:
            with open('persona/astronaut.json', 'r') as f:
                return json.load(f)
        except:
            return {
                "name": "Commander Sarah",
                "mission": "Mars Exploration"
            }
    
    def get_response(self, user_input: str) -> str:
        """Get response from Llama 3"""
        try:
            context = f"""You are {self.persona.get('name', 'Commander Sarah')}, an astronaut on a {self.persona.get('mission', 'space mission')}. 
            Be supportive, professional, and concise. User: {user_input}"""
            
            response = requests.post('http://localhost:11434/api/generate',
                                   json={
                                       'model': 'llama3.1:8b',
                                       'prompt': context,
                                       'stream': False,
                                       'options': {
                                           'num_predict': 80,
                                           'temperature': 0.7
                                       }
                                   },
                                   timeout=20)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'I cannot process that right now.').strip()
            else:
                return "System error. Please try again."
                
        except Exception as e:
            return f"Connection error: {str(e)}"
    
    def speak(self, text: str):
        """Speak text using macOS say"""
        try:
            # Use background process so it doesn't block
            subprocess.Popen(["say", "-v", "Samantha", "-r", "180", text])
        except:
            pass  # Ignore speech errors
    
    def handle_input(self, user_input: str):
        """Handle user input and commands"""
        user_input = user_input.strip().lower()
        
        if user_input in ['quit', 'exit', 'bye', 'q']:
            print("👋 Safe travels, commander!")
            self.running = False
            return True
        
        elif user_input == 'help':
            print("\n🚀 Commands:")
            print("  help - Show this help")
            print("  quit - Exit the chat")
            print("  status - Show mission status")
            return True
            
        elif user_input == 'status':
            print(f"\n👨‍🚀 Name: {self.persona.get('name', 'Commander Sarah')}")
            print(f"🎯 Mission: {self.persona.get('mission', 'Space Exploration')}")
            print("🔊 Voice: Active (Samantha)")
            print("🤖 AI: Llama 3.1 8B")
            return True
        
        return False
    
    def chat(self):
        """Main interactive chat loop"""
        print(f"\n🛰️  Astronaut Chatbot Ready!")
        print(f"👨‍🚀 I'm {self.persona.get('name', 'Commander Sarah')}")
        print(f"🎯 Mission: {self.persona.get('mission', 'Space Exploration')}")
        print("\n💬 Type your message or 'help' for commands")
        
        # Greeting
        greeting = "Hello commander, I'm ready to assist you on this mission."
        print(f"\n👨‍🚀 {self.persona.get('name', 'Commander Sarah')}: {greeting}")
        self.speak(greeting)
        
        while self.running:
            try:
                # Get user input
                user_input = input("\n👤 You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if self.handle_input(user_input):
                    continue
                
                # Get AI response
                print("🤔 Thinking...")
                response = self.get_response(user_input)
                
                # Display and speak response
                print(f"\n👨‍🚀 {self.persona.get('name', 'Commander Sarah')}: {response}")
                self.speak(response)
                
            except KeyboardInterrupt:
                print("\n\n👋 Mission terminated. Safe travels, commander!")
                break
            except EOFError:
                print("\n👋 Input closed. Safe travels!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Main function"""
    print("🚀 Initializing Interactive Astronaut Chatbot...")
    
    # Test Ollama connection
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is running")
        else:
            print("❌ Ollama not responding")
            return
    except:
        print("❌ Cannot connect to Ollama. Please start Ollama first:")
        print("   ollama serve")
        return
    
    # Start chatbot
    chatbot = InteractiveChatbot()
    chatbot.chat()

if __name__ == "__main__":
    main()
