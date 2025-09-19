# Voice Setup Guide

## How to Add Your Recorded Voice

### Step 1: Prepare Your Audio File

**Requirements for best results:**
- **Duration**: 10-30 seconds of clear speech
- **Format**: MP3, WAV, M4A, or FLAC
- **Quality**: Clear, no background noise
- **Content**: Normal conversational speech (not singing or shouting)
- **Sample Rate**: 22kHz or higher recommended

**What to record:**
- Speak naturally, as if talking to a friend
- Use a variety of words and emotions
- Include some longer sentences
- Example: "Hello, this is my voice. I'm speaking clearly and naturally. How are you doing today? I hope you're having a wonderful time."

### Step 2: Set Up Voice Cloning

1. **Install dependencies:**
```bash
./setup_voice_cloning.sh
```

2. **Place your audio file in the project:**
```bash
# Copy your audio file to the project directory
cp /path/to/your/voice.mp3 voice_samples/my_voice.mp3
```

3. **Test voice cloning:**
```bash
python3 voice_cloning_advanced.py
# Enter the path to your audio file when prompted
```

### Step 3: Use Voice Cloning in Chat

1. **Start the chat with voice cloning:**
```bash
USE_TTS=1 python3 chat_with_voice_cloning.py
```

2. **Set your voice file:**
```
You: /voice voice_samples/my_voice.mp3
Maitre: Voice set to: voice_samples/my_voice.mp3
```

3. **Test the voice:**
```
You: Hello, can you say something in my voice?
Maitre: [Responds using your cloned voice]
```

### Step 4: Commands for Voice Management

- `/voice <path>` - Set voice cloning audio file
- `/voice_info` - Show current voice settings
- `/help` - Show all available commands

### Troubleshooting

**Voice cloning not working:**
- Check if Coqui TTS is installed: `python3 -c "import TTS"`
- Verify audio file exists and is readable
- Try a different audio format (WAV works best)
- Check audio quality (clear, no background noise)

**Audio quality issues:**
- Use a quiet environment for recording
- Speak clearly and at normal pace
- Avoid background music or noise
- Record in a room with good acoustics

**Performance issues:**
- Use shorter audio files (10-20 seconds)
- Lower quality audio if needed
- Close other applications to free up memory

### Advanced Tips

**For better voice cloning:**
1. **Record multiple samples** and use the best one
2. **Include emotional variety** (happy, calm, excited)
3. **Use natural pauses** between sentences
4. **Record in the same environment** for consistency

**Audio file preparation:**
```bash
# Convert to optimal format
ffmpeg -i your_voice.mp3 -ar 22050 -ac 1 -acodec pcm_s16le voice_optimized.wav

# Check audio info
ffprobe -v quiet -print_format json -show_format -show_streams your_voice.mp3
```

### Example Workflow

```bash
# 1. Setup
./setup_voice_cloning.sh

# 2. Test voice cloning
python3 voice_cloning_advanced.py
# Enter: voice_samples/my_voice.mp3

# 3. Start chat with voice cloning
USE_TTS=1 python3 chat_with_voice_cloning.py

# 4. Set your voice
You: /voice voice_samples/my_voice.mp3

# 5. Chat normally - responses will use your voice!
You: Tell me about space
Maitre: [Responds in your cloned voice]
```

### File Structure

```
hackthon/
├── voice_samples/
│   ├── my_voice.mp3          # Your recorded voice
│   ├── current_voice.txt     # Currently active voice
│   └── reference_prepared.wav # Processed voice file
├── chat_with_voice_cloning.py
├── voice_cloning_advanced.py
└── setup_voice_cloning.sh
```

Now you can have the AI respond using your own voice! 🎤✨
