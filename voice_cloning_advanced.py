#!/usr/bin/env python3
"""
Advanced Voice Cloning System using Coqui TTS
This can clone voices from recorded audio samples
"""

import os
import tempfile
import subprocess
from typing import Optional
import json

class AdvancedVoiceCloner:
    def __init__(self, reference_audio_path: Optional[str] = None):
        """
        Initialize advanced voice cloner with reference audio
        
        Args:
            reference_audio_path: Path to reference audio file for voice cloning
        """
        self.reference_audio_path = reference_audio_path
        self.tts_available = self._check_tts_availability()
        
        if self.tts_available:
            print("✅ Coqui TTS available - Voice cloning enabled")
        else:
            print("⚠️  Coqui TTS not available - Using fallback TTS")
    
    def _check_tts_availability(self) -> bool:
        """Check if Coqui TTS is available"""
        try:
            from TTS.api import TTS
            return True
        except ImportError:
            return False
    
    def clone_voice_from_audio(self, text: str, reference_audio_path: str, output_path: Optional[str] = None) -> str:
        """
        Clone voice from reference audio using Coqui TTS
        
        Args:
            text: Text to synthesize
            reference_audio_path: Path to reference audio file
            output_path: Optional output path for audio file
            
        Returns:
            Path to generated audio file
        """
        if not self.tts_available:
            print("Coqui TTS not available, using fallback")
            return self._fallback_tts(text)
        
        try:
            from TTS.api import TTS
            
            # Use XTTS v2 for voice cloning
            tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
            
            if output_path is None:
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                    output_path = temp_file.name
            
            # Generate speech with cloned voice
            tts.tts_to_file(
                text=text,
                speaker_wav=reference_audio_path,
                language="en",
                file_path=output_path
            )
            
            # Play the generated audio
            self._play_audio(output_path)
            
            return output_path
            
        except Exception as e:
            print(f"Voice cloning error: {e}")
            return self._fallback_tts(text)
    
    def _fallback_tts(self, text: str) -> str:
        """Fallback to macOS say command"""
        try:
            subprocess.run(["say", text], check=True)
            return "fallback_playback"
        except Exception as e:
            print(f"Fallback TTS error: {e}")
            return "error"
    
    def _play_audio(self, audio_path: str):
        """Play audio file"""
        try:
            subprocess.run(["afplay", audio_path], check=True)
        except Exception as e:
            print(f"Audio playback error: {e}")
    
    def prepare_reference_audio(self, input_path: str, output_path: str) -> bool:
        """
        Prepare reference audio for voice cloning
        
        Args:
            input_path: Path to input audio file
            output_path: Path to save prepared audio
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert to WAV format with proper settings for voice cloning
            cmd = [
                "ffmpeg", "-i", input_path,
                "-ar", "22050",  # Sample rate
                "-ac", "1",      # Mono
                "-acodec", "pcm_s16le",  # 16-bit PCM
                "-y",            # Overwrite output
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Reference audio prepared: {output_path}")
                return True
            else:
                print(f"❌ Error preparing audio: {result.stderr}")
                return False
                
        except FileNotFoundError:
            print("❌ ffmpeg not found. Please install ffmpeg:")
            print("brew install ffmpeg")
            return False
        except Exception as e:
            print(f"❌ Error preparing audio: {e}")
            return False
    
    def get_voice_info(self, audio_path: str) -> dict:
        """Get information about the audio file"""
        try:
            cmd = [
                "ffprobe", "-v", "quiet",
                "-print_format", "json",
                "-show_format", "-show_streams",
                audio_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                info = json.loads(result.stdout)
                return {
                    "duration": float(info["format"]["duration"]),
                    "sample_rate": int(info["streams"][0]["sample_rate"]),
                    "channels": int(info["streams"][0]["channels"]),
                    "format": info["format"]["format_name"]
                }
            else:
                return {"error": "Could not analyze audio file"}
                
        except Exception as e:
            return {"error": str(e)}

def main():
    """Test the advanced voice cloning system"""
    print("🎤 Advanced Voice Cloning System")
    print("=" * 40)
    
    # Check if reference audio is provided
    reference_audio = input("Enter path to reference audio file (or press Enter to skip): ").strip()
    
    if reference_audio and os.path.exists(reference_audio):
        cloner = AdvancedVoiceCloner(reference_audio)
        
        # Prepare reference audio
        prepared_audio = "reference_prepared.wav"
        if cloner.prepare_reference_audio(reference_audio, prepared_audio):
            # Get audio info
            info = cloner.get_voice_info(prepared_audio)
            print(f"📊 Audio info: {info}")
            
            # Test voice cloning
            test_text = "Hello commander, how are you feeling today? I miss you and can't wait for you to come home."
            print(f"🎯 Testing voice cloning with: '{test_text}'")
            
            output_path = cloner.clone_voice_from_audio(test_text, prepared_audio)
            print(f"✅ Generated audio: {output_path}")
        else:
            print("❌ Failed to prepare reference audio")
    else:
        print("⚠️  No reference audio provided, testing fallback TTS")
        cloner = AdvancedVoiceCloner()
        test_text = "Hello commander, this is the fallback voice system."
        cloner._fallback_tts(test_text)

if __name__ == "__main__":
    main()
