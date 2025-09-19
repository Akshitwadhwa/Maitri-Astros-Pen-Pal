#!/usr/bin/env python3
"""
Real Voice Cloning using Coqui TTS with PyTorch compatibility fix
This actually clones your voice from the sample audio
"""

import os
import tempfile
import subprocess
import torch
from typing import Optional

class CoquiVoiceCloner:
    def __init__(self, reference_audio_path: Optional[str] = None):
        """
        Initialize Coqui voice cloner with reference audio
        
        Args:
            reference_audio_path: Path to reference audio file for voice cloning
        """
        self.reference_audio_path = reference_audio_path
        self.tts = None
        self.initialize_tts()
    
    def initialize_tts(self):
        """Initialize Coqui TTS with XTTS model"""
        try:
            from TTS.api import TTS
            
            # Fix PyTorch loading issue by setting weights_only=False
            original_load = torch.load
            torch.load = lambda *args, **kwargs: original_load(*args, weights_only=False, **kwargs)
            
            print("🎤 Initializing Coqui TTS with XTTS v2 model...")
            self.tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
            print("✅ Coqui TTS initialized successfully!")
            
            # Restore original torch.load
            torch.load = original_load
            
        except Exception as e:
            print(f"❌ Failed to initialize Coqui TTS: {e}")
            self.tts = None
    
    def clone_voice(self, text: str, reference_audio_path: str, output_path: Optional[str] = None) -> str:
        """
        Clone voice from reference audio using Coqui TTS
        
        Args:
            text: Text to synthesize
            reference_audio_path: Path to reference audio file
            output_path: Optional output path for audio file
            
        Returns:
            Path to generated audio file
        """
        if not self.tts:
            print("❌ Coqui TTS not available")
            return self._fallback_tts(text)
        
        if not os.path.exists(reference_audio_path):
            print(f"❌ Reference audio not found: {reference_audio_path}")
            return self._fallback_tts(text)
        
        try:
            if output_path is None:
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                    output_path = temp_file.name
            
            print(f"🎯 Cloning voice for: '{text[:50]}...'")
            
            # Generate speech with cloned voice
            self.tts.tts_to_file(
                text=text,
                speaker_wav=reference_audio_path,
                language="en",
                file_path=output_path
            )
            
            print(f"✅ Voice cloned successfully!")
            
            # Play the generated audio
            self._play_audio(output_path)
            
            return output_path
            
        except Exception as e:
            print(f"❌ Voice cloning error: {e}")
            return self._fallback_tts(text)
    
    def _fallback_tts(self, text: str) -> str:
        """Fallback to macOS say command"""
        try:
            print("⚠️  Using fallback TTS")
            subprocess.run(["say", text], check=True)
            return "fallback_playback"
        except Exception as e:
            print(f"❌ Fallback TTS error: {e}")
            return "error"
    
    def _play_audio(self, audio_path: str):
        """Play audio file"""
        try:
            subprocess.run(["afplay", audio_path], check=True)
        except Exception as e:
            print(f"❌ Audio playback error: {e}")
    
    def test_voice_cloning(self, reference_audio_path: str):
        """Test voice cloning with the reference audio"""
        if not os.path.exists(reference_audio_path):
            print(f"❌ Reference audio not found: {reference_audio_path}")
            return False
        
        test_text = "Hello commander, this is your cloned voice speaking. How are you feeling today?"
        
        print(f"🧪 Testing voice cloning with: {reference_audio_path}")
        result = self.clone_voice(test_text, reference_audio_path)
        
        if result and result != "fallback_playback" and result != "error":
            print("✅ Voice cloning test successful!")
            return True
        else:
            print("❌ Voice cloning test failed")
            return False

def main():
    """Test the Coqui voice cloning system"""
    print("🎤 Coqui Voice Cloning System (Fixed)")
    print("=" * 40)
    
    # Test with sample audio
    sample_audio = "voice_samples/prepared_voice.wav"
    
    if os.path.exists(sample_audio):
        print(f"📁 Using sample audio: {sample_audio}")
        cloner = CoquiVoiceCloner(sample_audio)
        
        # Test voice cloning
        if cloner.tts:
            success = cloner.test_voice_cloning(sample_audio)
            if success:
                print("\n🎯 Voice cloning is working! Your voice will be used for AI responses.")
            else:
                print("\n❌ Voice cloning failed, but fallback TTS is available.")
        else:
            print("\n❌ Coqui TTS not available, using fallback TTS")
    else:
        print(f"❌ Sample audio not found: {sample_audio}")
        print("Run: python3 prepare_voice.py 'sample audio.mp3' first")

if __name__ == "__main__":
    main()
