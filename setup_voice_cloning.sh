#!/bin/bash
# Setup script for advanced voice cloning

echo "🎤 Setting up Advanced Voice Cloning System"
echo "=========================================="

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script is designed for macOS"
    exit 1
fi

# Install ffmpeg if not present
if ! command -v ffmpeg &> /dev/null; then
    echo "📦 Installing ffmpeg..."
    brew install ffmpeg
else
    echo "✅ ffmpeg already installed"
fi

# Install ffprobe if not present
if ! command -v ffprobe &> /dev/null; then
    echo "📦 Installing ffprobe..."
    brew install ffmpeg
else
    echo "✅ ffprobe already installed"
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "🐍 Python version: $python_version"

# Install Coqui TTS (requires Python 3.10+)
if [[ $(echo "$python_version >= 3.10" | bc -l) -eq 1 ]]; then
    echo "📦 Installing Coqui TTS..."
    pip3 install TTS
    echo "✅ Coqui TTS installed"
else
    echo "⚠️  Python 3.10+ required for Coqui TTS"
    echo "   Current version: $python_version"
    echo "   Voice cloning will use fallback TTS"
fi

# Install additional dependencies
echo "📦 Installing additional dependencies..."
pip3 install pydub soundfile

echo ""
echo "🎯 Setup complete!"
echo ""
echo "To use voice cloning:"
echo "1. Place your reference audio file in the project directory"
echo "2. Run: python3 voice_cloning_advanced.py"
echo "3. Enter the path to your audio file when prompted"
echo ""
echo "Supported audio formats: MP3, WAV, M4A, FLAC, etc."
echo "Recommended: 10-30 seconds of clear speech, 22kHz sample rate"
