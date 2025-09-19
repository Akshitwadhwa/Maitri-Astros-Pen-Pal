#!/usr/bin/env python3
"""
Accept Coqui TTS license and initialize the model
"""

from TTS.api import TTS

print("🎤 Initializing Coqui TTS with XTTS v2 model...")
print("📝 Accepting license for non-commercial use...")

# Initialize TTS - this will prompt for license acceptance
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")

print("✅ Coqui TTS initialized successfully!")
print("🎯 Ready for voice cloning!")
