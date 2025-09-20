# Custom Voice TTS Setup Guide

## Overview
This guide helps you integrate your custom voice samples from Google Cloud Storage with the astronaut chatbot using Google Cloud Text-to-Speech.

## Prerequisites

### 1. Google Cloud Setup
1. **Create/Select Project**: Go to [Google Cloud Console](https://console.cloud.google.com/)
2. **Enable APIs**:
   - Cloud Text-to-Speech API
   - Cloud Storage API
3. **Create Service Account**:
   - Go to "IAM & Admin" > "Service Accounts"
   - Create new service account: `astronaut-tts-service`
   - Grant roles:
     - `Cloud Text-to-Speech API User`
     - `Storage Object Viewer`
   - Download JSON key file

### 2. Upload Voice Samples
1. **Create Storage Bucket**:
   ```bash
   gsutil mb gs://your-voice-bucket-name
   ```
2. **Upload Voice Files**:
   ```bash
   gsutil cp your_voice_sample.wav gs://your-voice-bucket-name/voice_samples/
   ```

### 3. Environment Configuration
Set these environment variables:
```bash
# Required
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account.json"
export GCS_BUCKET_NAME="your-voice-bucket-name"
export GCS_VOICE_SAMPLE_PATH="voice_samples/your_voice_sample.wav"

# Optional: For specific voice sample
export VOICE_SAMPLE_FILE="your_voice_sample.wav"
```

## Installation

### 1. Install Dependencies
```bash
pip3 install -r requirements_gcp.txt
```

### 2. Run Setup Script
```bash
./setup_custom_voice.sh
```

## Usage

### 1. Test Custom Voice TTS
```bash
python3 custom_voice_tts.py
```

### 2. Run Chatbot with Custom Voice
```bash
python3 chat_custom_voice.py
```

### 3. Available Voice Modes
The system automatically selects voice characteristics based on content:
- **Supportive**: Calming, slower speech for emotional support
- **Encouraging**: Faster, higher pitch for motivation
- **Normal**: Standard settings for regular conversation

## Voice Sample Requirements

### Supported Formats
- WAV (recommended)
- MP3
- M4A
- FLAC

### Quality Guidelines
- **Duration**: 10-60 seconds of clear speech
- **Quality**: 16kHz or higher sample rate
- **Content**: Natural speech without background noise
- **Language**: English (preferably with your accent)

### Upload Examples
```bash
# Upload single file
gsutil cp voice_sample.wav gs://my-voice-bucket/samples/

# Upload multiple files
gsutil -m cp voice_samples/* gs://my-voice-bucket/samples/

# List uploaded files
gsutil ls gs://my-voice-bucket/samples/
```

## Configuration Options

### Voice Parameters
You can customize voice characteristics in `custom_voice_tts.py`:

```python
# Supportive voice (calming)
speaking_rate = 0.9    # Slower speech
pitch = -2.0          # Lower pitch
volume_gain_db = 2.0  # Slightly louder

# Encouraging voice (motivational)
speaking_rate = 1.1    # Faster speech
pitch = 1.5           # Higher pitch
volume_gain_db = 1.0  # Normal volume
```

### Language Options
Supported languages for custom voice:
- `en-IN`: Indian English (recommended)
- `en-US`: US English
- `en-GB`: British English
- `en-AU`: Australian English

## Troubleshooting

### Common Issues

1. **Authentication Error**:
   ```
   Error: Could not automatically determine credentials
   ```
   - Solution: Set `GOOGLE_APPLICATION_CREDENTIALS` environment variable

2. **API Not Enabled**:
   ```
   Error: API [texttospeech.googleapis.com] not enabled
   ```
   - Solution: Enable Text-to-Speech API in Google Cloud Console

3. **Bucket Not Found**:
   ```
   Error: 404 Not Found
   ```
   - Solution: Check bucket name and ensure it exists

4. **Voice Sample Not Found**:
   ```
   Error: 404 Not Found for voice sample
   ```
   - Solution: Check file path in bucket and ensure file exists

### Testing Steps

1. **Test Google Cloud Connection**:
   ```bash
   python3 -c "from google.cloud import texttospeech; print('✅ Google Cloud TTS available')"
   ```

2. **Test Storage Access**:
   ```bash
   gsutil ls gs://your-bucket-name/
   ```

3. **Test Voice Synthesis**:
   ```bash
   python3 custom_voice_tts.py
   ```

## Integration with Existing Chatbot

The custom voice system integrates seamlessly with your existing astronaut chatbot:

```python
from custom_voice_tts import CustomVoiceTTS
from chat_custom_voice import AstronautChatbot

# Initialize custom voice TTS
custom_voice_tts = CustomVoiceTTS(
    bucket_name="your-voice-bucket",
    voice_sample_path="voice_samples/your_voice.wav"
)

# Initialize chatbot
chatbot = AstronautChatbot("persona/astronaut.json", custom_voice_tts)

# Start chatting
chatbot.chat()
```

## Advanced Features

### Multiple Voice Samples
You can use different voice samples for different contexts:

```python
# Supportive voice sample
supportive_voice = "voice_samples/calm_voice.wav"

# Encouraging voice sample  
encouraging_voice = "voice_samples/energetic_voice.wav"
```

### Voice Characteristics Analysis
The system can analyze your voice samples and apply similar characteristics to synthesized speech (basic implementation provided).

## Support

For issues or questions:
1. Check the logs in `chat_history/` directory
2. Verify Google Cloud configuration
3. Test individual components separately
4. Check network connectivity to Google Cloud services
