#!/usr/bin/env python3
"""
Working Astronaut Chatbot - Fixed timeout issues
"""

import os
import sys
import json
import requests
import subprocess
from datetime import datetime

class WorkingChatbot:
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
        """Get response from Llama 3 with better timeout handling"""
        try:
            # Simpler context for faster response
            context = f"You are Commander Sarah, an astronaut. Be supportive and brief. User: {user_input}"
            
            response = requests.post('http://localhost:11434/api/generate',
                                   json={
                                       'model': 'llama3.1:8b',
                                       'prompt': context,
                                       'stream': False,
                                       'options': {
                                           'num_predict': 50,  # Shorter responses
                                           'temperature': 0.7,
                                           'top_p': 0.9,
                                           'repeat_penalty': 1.1
                                       }
                                   },
                                   timeout=60)  # Longer timeout
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', 'I cannot process that right now.').strip()
                # Clean up the response
                if response_text.startswith('You are Commander Sarah'):
                    response_text = response_text.split('\n')[1] if '\n' in response_text else "I understand, commander."
                return response_text
            else:
                return f"System error (status {response.status_code}). Please try again."
                
        except requests.exceptions.Timeout:
            return "I'm taking a bit longer to process that. Could you rephrase your question?"
        except requests.exceptions.ConnectionError:
            return "I'm having trouble connecting to my systems. Please check if Ollama is running."
        except Exception as e:
            return f"Technical difficulty: {str(e)[:50]}..."
    
    def speak(self, text: str):
        """Speak text using macOS say"""
        try:
            # Use background process so it doesn't block
            subprocess.Popen(["say", "-v", "Samantha", "-r", "170", text])
        except:
            pass  # Ignore speech errors
    
    def handle_input(self, user_input: str):
        """Handle user input and commands"""
        user_input = user_input.strip().lower()
        
        if user_input in ['quit', 'exit', 'bye', 'q']:
            print("👋 Safe travels, commander!")
            self.speak("Safe travels, commander!")
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
            print("📡 Connection: Active")
            return True
        
        return False
    
    def chat(self):
        """Main interactive chat loop"""
        print(f"\n🛰️  Astronaut Chatbot Ready!")
        print(f"👨‍🚀 I'm {self.persona.get('name', 'Commander Sarah')}")
        print(f"🎯 Mission: {self.persona.get('mission', 'Space Exploration')}")
        print("\n💬 Type your message or 'help' for commands")
        print("⏱️  Responses may take 10-30 seconds...")
        
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
                print("🤔 Thinking... (this may take a moment)")
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
    print("🚀 Initializing Working Astronaut Chatbot...")
    
    # Test Ollama connection with longer timeout
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=10)
        if response.status_code == 200:
            print("✅ Ollama is running")
            models = response.json().get('models', [])
            if models:
                print(f"📦 Available models: {[m['name'] for m in models]}")
        else:
            print("❌ Ollama not responding properly")
            return
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("🔧 Please start Ollama first:")
        print("   ollama serve")
        return
    
    # Start chatbot
    chatbot = WorkingChatbot()
    chatbot.chat()

if __name__ == "__main__":
    main()
