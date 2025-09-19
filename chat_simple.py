#!/usr/bin/env python3
"""
Simple Astronaut Chatbot - Fast and Reliable
"""

import os
import sys
import json
import requests
import subprocess
from datetime import datetime

class SimpleChatbot:
    def __init__(self):
        self.persona = self.load_persona()
        
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
            context = f"""You are {self.persona.get('name', 'Commander Sarah')}, an astronaut. 
            Be supportive and concise. User: {user_input}"""
            
            response = requests.post('http://localhost:11434/api/generate',
                                   json={
                                       'model': 'llama3.1:8b',
                                       'prompt': context,
                                       'stream': False,
                                       'options': {
                                           'num_predict': 60,
                                           'temperature': 0.7
                                       }
                                   },
                                   timeout=30)  # Longer timeout
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'I cannot process that right now.').strip()
            else:
                return "System error. Please try again."
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    def speak(self, text: str):
        """Speak text using macOS say"""
        try:
            subprocess.run(["say", "-v", "Samantha", "-r", "180", text], 
                         check=True, timeout=10)
        except:
            pass  # Ignore speech errors
    
    def chat(self):
        """Main chat loop"""
        print(f"\n🛰️  Astronaut Chatbot Ready!")
        print(f"👨‍🚀 I'm {self.persona.get('name', 'Commander Sarah')}")
        print(f"🎯 Mission: {self.persona.get('mission', 'Space Exploration')}")
        print("\n💬 Type your message or 'quit' to exit")
        
        # Greeting
        greeting = "Hello commander, I'm ready to assist you."
        print(f"\n👨‍🚀 {self.persona.get('name', 'Commander Sarah')}: {greeting}")
        self.speak(greeting)
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Safe travels, commander!")
                    break
                
                # Get response
                print("🤔 Thinking...")
                response = self.get_response(user_input)
                
                # Display and speak response
                print(f"\n👨‍🚀 {self.persona.get('name', 'Commander Sarah')}: {response}")
                self.speak(response)
                
            except KeyboardInterrupt:
                print("\n👋 Mission terminated. Safe travels!")
                break
            except EOFError:
                print("\n👋 Input closed. Safe travels!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Main function"""
    print("🚀 Starting Simple Astronaut Chatbot...")
    
    # Test Ollama connection
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is running")
        else:
            print("❌ Ollama not responding properly")
            return
    except:
        print("❌ Cannot connect to Ollama. Please start Ollama first:")
        print("   ollama serve")
        return
    
    # Start chatbot
    chatbot = SimpleChatbot()
    chatbot.chat()

if __name__ == "__main__":
    main()
