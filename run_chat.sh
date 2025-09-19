#!/bin/bash

echo "🚀 Starting Astronaut Chatbot..."
echo "📋 Make sure Ollama is running (ollama serve)"
echo ""

# Check if Ollama is running
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✅ Ollama is running"
    echo ""
    echo "🛰️  Starting chat..."
    echo "💬 Type your messages to chat with Commander Sarah"
    echo "🔊 She will speak responses using your voice sample"
    echo "📝 Type 'quit' to exit"
    echo ""
    
    # Run the chatbot
    python3 chat_simple.py
else
    echo "❌ Ollama is not running"
    echo "🔧 Please start Ollama first:"
    echo "   ollama serve"
    echo ""
    echo "Then run this script again."
fi
