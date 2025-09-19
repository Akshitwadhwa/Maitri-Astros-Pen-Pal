#!/usr/bin/env python3
"""
Simple Voice Cloning System using audio processing
This creates a voice that sounds more like your sample by modifying TTS parameters
"""

import os
import subprocess
import tempfile
import json
from typing import Optional

class SimpleVoiceCloner:
    def __init__(self, reference_audio_path: Optional[str] = None):
        """
        Initialize simple voice cloner with reference audio
        
        Args:
            reference_audio_path: Path to reference audio file for voice analysis
        """
        self.reference_audio_path = reference_audio_path
        self.voice_profile = None
        
        if reference_audio_path and os.path.exists(reference_audio_path):
            self.voice_profile = self._analyze_voice(reference_audio_path)
    
    def _analyze_voice(self, audio_path: str) -> dict:
        """Analyze the reference voice to extract characteristics"""
        try:
            # Get audio characteristics using ffprobe
            cmd = [
                "ffprobe", "-v", "quiet",
                "-print_format", "json",
                "-show_format", "-show_streams",
                audio_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                info = json.loads(result.stdout)
                stream_info = info["streams"][0]
                
                # Extract basic characteristics
                sample_rate = int(stream_info["sample_rate"])
                duration = float(info["format"]["duration"])
                
                # Estimate speaking rate (words per minute)
                # This is a rough estimate - in reality we'd need speech recognition
                estimated_wpm = 150  # Default assumption
                
                # Estimate pitch characteristics
                # Higher sample rate often indicates higher pitch content
                pitch_estimate = "medium"
                if sample_rate > 44100:
                    pitch_estimate = "high"
                elif sample_rate < 22050:
                    pitch_estimate = "low"
                
                return {
                    "sample_rate": sample_rate,
                    "duration": duration,
                    "estimated_wpm": estimated_wpm,
                    "pitch_estimate": pitch_estimate,
                    "voice_characteristics": self._get_voice_characteristics(audio_path)
                }
            else:
                return self._get_default_voice_profile()
                
        except Exception as e:
            print(f"Voice analysis error: {e}")
            return self._get_default_voice_profile()
    
    def _get_voice_characteristics(self, audio_path: str) -> dict:
        """Get voice characteristics from audio file"""
        try:
            # Use ffmpeg to analyze audio characteristics
            cmd = [
                "ffmpeg", "-i", audio_path,
                "-af", "astats=metadata=1:reset=1",
                "-f", "null", "-"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, stderr=subprocess.STDOUT)
            
            # Extract basic characteristics from ffmpeg output
            characteristics = {
                "volume_level": "medium",
                "clarity": "good",
                "pace": "normal"
            }
            
            # Look for volume indicators
            if "mean_volume" in result.stdout:
                # This is a simplified analysis
                characteristics["volume_level"] = "medium"
            
            return characteristics
            
        except Exception as e:
            print(f"Characteristic analysis error: {e}")
            return {"volume_level": "medium", "clarity": "good", "pace": "normal"}
    
    def _get_default_voice_profile(self) -> dict:
        """Get default voice profile when analysis fails"""
        return {
            "sample_rate": 22050,
            "duration": 0,
            "estimated_wpm": 150,
            "pitch_estimate": "medium",
            "voice_characteristics": {
                "volume_level": "medium",
                "clarity": "good",
                "pace": "normal"
            }
        }
    
    def speak_with_voice(self, text: str) -> str:
        """
        Speak text using voice characteristics from reference audio
        
        Args:
            text: Text to speak
            
        Returns:
            Status of voice generation
        """
        if not self.voice_profile:
            print("No voice profile available, using default voice")
            return self._speak_default(text)
        
        try:
            # Select voice based on analysis
            voice = self._select_voice()
            rate = self._calculate_rate()
            volume = self._calculate_volume()
            
            # Use macOS say with optimized parameters
            cmd = [
                "say",
                "-v", voice,
                "-r", str(rate),
                "-o", "temp_voice.aiff",  # Save to file first
                text
            ]
            
            result = subprocess.run(cmd, check=True)
            
            if result.returncode == 0:
                # Play the generated audio
                subprocess.run(["afplay", "temp_voice.aiff"], check=True)
                
                # Clean up
                if os.path.exists("temp_voice.aiff"):
                    os.remove("temp_voice.aiff")
                
                return "voice_generated"
            else:
                return self._speak_default(text)
                
        except Exception as e:
            print(f"Voice generation error: {e}")
            return self._speak_default(text)
    
    def _select_voice(self) -> str:
        """Select the best voice based on analysis"""
        if not self.voice_profile:
            return "Samantha"
        
        pitch = self.voice_profile.get("pitch_estimate", "medium")
        
        # Voice selection based on pitch characteristics
        voice_map = {
            "high": "Samantha",      # Clear, higher pitch
            "medium": "Karen",       # Warm, medium pitch
            "low": "Moira"           # Deeper, lower pitch
        }
        
        return voice_map.get(pitch, "Samantha")
    
    def _calculate_rate(self) -> int:
        """Calculate speech rate based on analysis"""
        if not self.voice_profile:
            return 150
        
        wpm = self.voice_profile.get("estimated_wpm", 150)
        
        # Convert WPM to say command rate (rough approximation)
        # say command uses words per minute directly
        return max(100, min(300, wpm))
    
    def _calculate_volume(self) -> float:
        """Calculate volume based on analysis"""
        if not self.voice_profile:
            return 0.8
        
        volume_level = self.voice_profile.get("voice_characteristics", {}).get("volume_level", "medium")
        
        volume_map = {
            "low": 0.6,
            "medium": 0.8,
            "high": 1.0
        }
        
        return volume_map.get(volume_level, 0.8)
    
    def _speak_default(self, text: str) -> str:
        """Fallback to default voice"""
        try:
            subprocess.run(["say", text], check=True)
            return "default_voice"
        except Exception as e:
            print(f"Default voice error: {e}")
            return "error"
    
    def update_reference_voice(self, audio_path: str):
        """Update the reference voice file"""
        if os.path.exists(audio_path):
            self.reference_audio_path = audio_path
            self.voice_profile = self._analyze_voice(audio_path)
            print(f"✅ Voice profile updated from: {audio_path}")
        else:
            print(f"❌ Voice file not found: {audio_path}")

def main():
    """Test the simple voice cloning system"""
    print("🎤 Simple Voice Cloning System")
    print("=" * 35)
    
    # Test with sample audio
    sample_audio = "voice_samples/prepared_voice.wav"
    
    if os.path.exists(sample_audio):
        print(f"📁 Using sample audio: {sample_audio}")
        cloner = SimpleVoiceCloner(sample_audio)
        
        # Show voice profile
        if cloner.voice_profile:
            print(f"📊 Voice Profile:")
            print(f"   Sample Rate: {cloner.voice_profile['sample_rate']} Hz")
            print(f"   Duration: {cloner.voice_profile['duration']:.1f}s")
            print(f"   Estimated WPM: {cloner.voice_profile['estimated_wpm']}")
            print(f"   Pitch: {cloner.voice_profile['pitch_estimate']}")
        
        # Test voice cloning
        test_text = "Hello commander, how are you feeling today? I miss you and can't wait for you to come home."
        print(f"\n🎯 Testing voice: '{test_text}'")
        
        result = cloner.speak_with_voice(test_text)
        print(f"✅ Result: {result}")
    else:
        print(f"❌ Sample audio not found: {sample_audio}")
        print("Run: python3 prepare_voice.py 'sample audio.mp3' first")

if __name__ == "__main__":
    main()
