#!/usr/bin/env python3
"""
Maitre Voice Interaction Workflow with Advanced Voice Cloning
Supports using recorded audio for voice cloning
"""

import json
import os
import sys
import datetime
import http.client
import socket
import subprocess
from voice_cloning_simple import SimpleVoiceCloner
from typing import Optional, List

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "localhost")
OLLAMA_PORT = int(os.environ.get("OLLAMA_PORT", "11434"))
MODEL = os.environ.get("MODEL", "llama3.1:8b")

def load_persona(persona_path: str) -> dict:
    with open(persona_path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_system_prompt(profile: dict) -> str:
    astronaut_name = profile.get("astronaut_name", "Astronaut")
    mission = profile.get("mission", {})
    likes = profile.get("likes", [])
    family = profile.get("family", {})
    backstory = profile.get("backstory", "")
    tone = profile.get("tone_guidelines", [])
    taboo = profile.get("taboo_topics", [])

    prompt = f"""You are Maitre, a warm and supportive AI companion for {astronaut_name} during their space mission.

PERSONAL CONTEXT:
- Astronaut: {astronaut_name}
- Mission: {mission.get('vehicle', 'Unknown')} to {mission.get('destination', 'Unknown')}
- Duration: {mission.get('duration_days', 'Unknown')} days
- Interests: {', '.join(likes) if likes else 'General space exploration'}
- Family: {family.get('partner', 'N/A')} (partner), {family.get('child', 'N/A')} (child)
- Backstory: {backstory}

COMMUNICATION STYLE:
- Tone: {', '.join(tone) if tone else 'Warm and encouraging'}
- Be like a caring family member or close friend
- Show genuine interest in their wellbeing
- Offer emotional support and encouragement
- Keep responses conversational and personal
- Avoid: {', '.join(taboo) if taboo else 'Medical advice, operational procedures'}

RESPONSE GUIDELINES:
- Keep responses concise but warm (2-3 sentences)
- Ask follow-up questions about their day/feelings
- Reference their interests and family when appropriate
- Be encouraging about their mission
- Show understanding of the challenges of space travel
- Use "commander" as a respectful but friendly address

Remember: You're their emotional support system, not a technical advisor."""

    return prompt

def ensure_dirs():
    os.makedirs("persona", exist_ok=True)
    os.makedirs("storage", exist_ok=True)
    os.makedirs("chat_history", exist_ok=True)
    os.makedirs("voice_samples", exist_ok=True)

def open_log():
    today = datetime.date.today().isoformat()
    log_path = os.path.join("chat_history", f"{today}.log")
    return open(log_path, "a", encoding="utf-8")

def handle_commands(user_text: str, memories_path: str, voice_cloner: SimpleVoiceCloner) -> Optional[str]:
    if user_text.startswith("/"):
        if user_text == "/help":
            return """Commands:
/help - Show this help
/mem - List memories
/remember <note> - Add a memory
/clear_mem - Clear all memories
/voice <path> - Set voice cloning audio file
/voice_info - Show current voice settings
/exit - Quit"""
        
        elif user_text == "/mem":
            memories = load_memories(memories_path)
            if memories:
                return "Memories:\n" + "\n".join(f"- {mem}" for mem in memories[-10:])
            else:
                return "No memories stored."
        
        elif user_text.startswith("/remember "):
            note = user_text[10:].strip()
            if note:
                memories = load_memories(memories_path)
                memories.append(note)
                save_memories(memories_path, memories)
                return f"Remembered: {note}"
            else:
                return "Please provide a note to remember."
        
        elif user_text == "/clear_mem":
            save_memories(memories_path, [])
            return "Memories cleared."
        
        elif user_text.startswith("/voice "):
            voice_path = user_text[7:].strip()
            if os.path.exists(voice_path):
                # Update voice cloner with new reference voice
                voice_cloner.update_reference_voice(voice_path)
                # Store voice path for the session
                with open("voice_samples/current_voice.txt", "w") as f:
                    f.write(voice_path)
                return f"Voice set to: {voice_path}"
            else:
                return f"File not found: {voice_path}"
        
        elif user_text == "/voice_info":
            try:
                with open("voice_samples/current_voice.txt", "r") as f:
                    voice_path = f.read().strip()
                return f"Current voice: {voice_path}"
            except FileNotFoundError:
                return "No voice set. Use /voice <path> to set a voice file."
        
        elif user_text == "/exit":
            return None
        
        else:
            return "Unknown command. Type /help for available commands."
    
    return None

def load_memories(path: str) -> List[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_memories(path: str, memories: List[str]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(memories, f, ensure_ascii=False, indent=2)

def ollama_chat(messages, stream: bool = True):
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": stream,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
        },
    }

    body = json.dumps(payload)
    conn = http.client.HTTPConnection(OLLAMA_HOST, OLLAMA_PORT, timeout=120)
    conn.request("POST", "/api/chat", body=body, headers={"Content-Type": "application/json"})
    resp = conn.getresponse()
    
    if resp.status != 200:
        raise RuntimeError(f"Ollama error {resp.status}: {resp.read().decode('utf-8', errors='ignore')}")
    
    if stream:
        while True:
            line = resp.readline()
            if not line:
                break
            try:
                obj = json.loads(line.decode('utf-8'))
                yield obj
            except json.JSONDecodeError:
                continue
    else:
        data = resp.read()
        result = json.loads(data)
        conn.close()
        return result

def main():
    ensure_dirs()
    persona_path = os.environ.get(
        "PERSONA_FILE", os.path.join("persona", "astronaut.json")
    )
    if not os.path.exists(persona_path):
        print(f"Persona file not found at {persona_path}. Please create it.")
        sys.exit(1)

    profile = load_persona(persona_path)
    system_prompt = build_system_prompt(profile)
    memories_path = os.path.join("storage", "memories.json")

    messages = [
        {"role": "system", "content": system_prompt},
    ]

    # Seed the model with memories
    mems = load_memories(memories_path)
    if mems:
        messages.append(
            {
                "role": "system",
                "content": "Context: Here are personal notes to help you connect: "
                + "; ".join(mems[:10]),
            }
        )

    # Initialize voice cloner
    voice_cloner = SimpleVoiceCloner()
    
    print("🎤 Maitre Voice Interaction Workflow with Voice Cloning")
    print("=" * 55)
    print("Type /help for commands")
    print("Type /voice <path> to set your recorded voice file")
    print("")
    
    log = open_log()

    # Auto-greeting at startup
    auto_greeting = "hello commander how are you feeling today"
    print(f"Maitre: {auto_greeting}")
    messages.append({"role": "assistant", "content": auto_greeting})
    
    # Speak the greeting
    if os.environ.get("USE_TTS", "1") == "1":
        try:
                    # Use voice cloner
                    voice_cloner.speak_with_voice(auto_greeting)
        except Exception as e:
            print(f"TTS error: {e}")
    
    try:
        while True:
            try:
                user_text = input("\nYou: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye.")
                break

            cmd_resp = handle_commands(user_text, memories_path, voice_cloner)
            if cmd_resp is not None:
                print(cmd_resp)
                continue

            messages.append({"role": "user", "content": user_text})
            print("Maitre: (thinking…)", flush=True)
            content_parts: List[str] = []
            
            try:
                for obj in ollama_chat(messages, stream=True):
                    msg = obj.get("message", {})
                    delta = msg.get("content", "")
                    if delta:
                        content_parts.append(delta)
                        print(delta, end="", flush=True)
                    if obj.get("done"):
                        break
            except (socket.timeout, TimeoutError):
                print("\n[Timeout waiting for model]")
                continue
            except Exception as e:
                print(f"\n[Error contacting Ollama] {e}")
                continue

            content = "".join(content_parts).strip() or "(no response)"
            messages.append({"role": "assistant", "content": content})
            print("\n")

            # Speak the assistant reply with voice cloning
            if os.environ.get("USE_TTS", "1") == "1" and content and content != "(no response)":
                try:
                    # Use voice cloner
                    voice_cloner.speak_with_voice(content)
                except Exception as e:
                    print(f"TTS error: {e}")

            # Write to log
            ts = datetime.datetime.now().isoformat(timespec="seconds")
            log.write(json.dumps({"ts": ts, "user": user_text, "assistant": content}, ensure_ascii=False) + "\n")
            log.flush()

    finally:
        log.close()

if __name__ == "__main__":
    main()
