#!/usr/bin/env python3
import json
import os
import sys
import datetime
import http.client
import socket
import subprocess
from voice_cloning import VoiceCloner
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

    parts = []
    parts.append(
        "You are Maitre, a warm, supportive pen-pal companion for an astronaut."
    )
    parts.append(
        "Your role is to chat casually, listen actively, and keep conversations engaging and empathetic."
    )
    parts.append(
        "Do not provide medical, safety-critical, or operational instructions. If asked, gently defer."
    )
    parts.append(
        f"Astronaut profile: name={astronaut_name}; mission={mission}; likes={likes}; family={family}."
    )
    if backstory:
        parts.append(f"Backstory: {backstory}")
    if tone:
        parts.append(f"Tone: {', '.join(tone)}")
    if taboo:
        parts.append(f"Avoid topics: {', '.join(taboo)}")
    parts.append(
        "Prefer short paragraphs. Ask one thoughtful follow-up question when it helps connection."
    )
    return "\n".join(parts)


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
    conn = http.client.HTTPConnection(OLLAMA_HOST, OLLAMA_PORT, timeout=300)
    conn.request("POST", "/api/chat", body=body, headers={"Content-Type": "application/json"})
    resp = conn.getresponse()
    if resp.status != 200:
        data = resp.read()
        raise RuntimeError(f"Ollama error {resp.status}: {data.decode('utf-8', errors='ignore')}")

    if not stream:
        data = resp.read()
        result = json.loads(data)
        conn.close()
        return result

    # Streaming: yield chunks as they arrive
    buffer = b""
    try:
        while True:
            chunk = resp.read(4096)
            if not chunk:
                break
            buffer += chunk
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                yield obj
    finally:
        conn.close()


def ensure_dirs():
    os.makedirs("persona", exist_ok=True)
    os.makedirs("storage", exist_ok=True)
    os.makedirs("chat_history", exist_ok=True)


def open_log():
    today = datetime.date.today().isoformat()
    path = os.path.join("chat_history", f"{today}.log")
    return open(path, "a", encoding="utf-8")


def handle_commands(user_text: str, memories_path: str) -> Optional[str]:
    text = user_text.strip()
    if text == "/exit":
        print("Goodbye.")
        sys.exit(0)
    if text == "/help":
        return (
            "Commands: /help, /exit, /mem (list), /remember <note>, /clear_mem\n"
            "Chat normally otherwise."
        )
    if text == "/mem":
        mems = load_memories(memories_path)
        if not mems:
            return "No saved memories yet. Use /remember <note> to add one."
        return "Memories:\n- " + "\n- ".join(mems)
    if text.startswith("/remember "):
        note = text[len("/remember ") :].strip()
        if note:
            remember(memories_path, note)
            return "Saved."
        return "Usage: /remember <note>"
    if text == "/clear_mem":
        save_memories(memories_path, [])
        return "Cleared all memories."
    return None


def load_memories(path: str) -> List[str]:
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_memories(path: str, memories: List[str]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(memories, f, ensure_ascii=False, indent=2)


def remember(path: str, note: str) -> None:
    memories = load_memories(path)
    memories.append(note)
    save_memories(path, memories)


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

    # Seed the model with a brief hello including any memories
    mems = load_memories(memories_path)
    if mems:
        messages.append(
            {
                "role": "system",
                "content": "Context: Here are personal notes to help you connect: "
                + "; ".join(mems[:10]),
            }
        )

    # Initialize voice cloner for family member voice
    voice_cloner = VoiceCloner()
    
    print("Maitre Pen-Pal ready. Type /help for commands.\n")
    log = open_log()

    # Auto-greeting at startup
    auto_greeting = "hello commander how are you feeling today"
    print(f"Maitre: {auto_greeting}\n")
    messages.append({"role": "assistant", "content": auto_greeting})
    
    # Speak the greeting with family voice
    if os.environ.get("USE_TTS", "1") == "1":
        try:
            voice_cloner.speak_with_family_voice(auto_greeting)
        except Exception as e:
            print(f"TTS error: {e}")
    try:
        while True:
            try:
                user_text = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye.")
                break

            cmd_resp = handle_commands(user_text, memories_path)
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
                        # print tokens incrementally on same line
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

            # Speak the assistant reply with family voice if TTS is enabled
            if os.environ.get("USE_TTS", "1") == "1" and content and content != "(no response)":
                try:
                    voice_cloner.speak_with_family_voice(content)
                except Exception as e:
                    print(f"TTS error: {e}")
                    # Fallback to simple TTS
                    try:
                        subprocess.run(["say", content], check=False)
                    except Exception:
                        pass

            # Write to log
            ts = datetime.datetime.now().isoformat(timespec="seconds")
            log.write(json.dumps({"ts": ts, "user": user_text, "assistant": content}, ensure_ascii=False) + "\n")
            log.flush()

            # Lightweight memory heuristic: if the user explicitly says "remember" something, store it too
            lower = user_text.lower()
            if "remember that" in lower or "note that" in lower:
                remember(memories_path, user_text)

    finally:
        log.close()


if __name__ == "__main__":
    main()


