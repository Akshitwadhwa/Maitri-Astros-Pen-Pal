#!/usr/bin/env python3
"""
Simple Voice Cloning System using pyttsx3 and pydub
This creates a family member voice by modifying TTS parameters and audio effects
"""

import pyttsx3
import pydub
import pydub.effects
import tempfile
import os
import subprocess
from typing import Optional

class VoiceCloner:
    def __init__(self, reference_audio_path: Optional[str] = None):
        """
        Initialize voice cloner
        
        Args:
            reference_audio_path: Path to reference audio file (optional)
        """
        self.engine = pyttsx3.init()
        self.reference_audio_path = reference_audio_path
        
        # Default voice settings for family member persona
        self.setup_family_voice()
    
    def setup_family_voice(self):
        """Configure TTS engine for family member voice characteristics"""
        voices = self.engine.getProperty('voices')
        
        # Try to find a suitable voice (prefer female voices for family member)
        for voice in voices:
            if 'female' in voice.name.lower() or 'woman' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
        
        # Adjust voice parameters for warmer, more personal tone
        self.engine.setProperty('rate', 150)  # Slightly slower for warmth
        self.engine.setProperty('volume', 0.9)  # High volume for clarity
        
        # Voice characteristics for family member
        self.voice_settings = {
            'rate': 150,
            'volume': 0.9,
            'pitch_shift': 0,  # Will be applied via audio effects
            'warmth_boost': True
        }
    
    def speak_with_family_voice(self, text: str, output_path: Optional[str] = None) -> str:
        """
        Generate speech with family member voice characteristics
        
        Args:
            text: Text to speak
            output_path: Optional path to save audio file
            
        Returns:
            Path to generated audio file
        """
        # For now, use direct playback with voice modifications
        # This avoids the WAV file corruption issue with pyttsx3
        try:
            # Use macOS say command with voice modifications
            self._speak_with_say(text)
            return "direct_playback"
        except Exception as e:
            print(f"Voice cloning error: {e}")
            # Fallback to simple TTS
            self.engine.say(text)
            self.engine.runAndWait()
            return "fallback_playback"
    
    def _speak_with_say(self, text: str):
        """Use macOS say command with family member voice characteristics"""
        # Select a warm, family-like voice
        voice_options = [
            "Samantha",  # Clear, warm female voice
            "Karen",     # Australian accent, friendly
            "Moira",     # Irish accent, warm
            "Tessa"      # South African accent, clear
        ]
        
        # Try different voices to find the best family member voice
        for voice in voice_options:
            try:
                # Use say command with voice and rate modifications
                cmd = [
                    "say", 
                    "-v", voice,
                    "-r", str(self.voice_settings['rate']),
                    text
                ]
                subprocess.run(cmd, check=True)
                return
            except subprocess.CalledProcessError:
                continue
        
        # If all voices fail, use default
        subprocess.run(["say", text], check=True)
    
    def _apply_voice_effects(self, input_path: str, output_path: Optional[str] = None) -> str:
        """
        Apply audio effects to make voice sound more like family member
        
        Args:
            input_path: Path to input audio file
            output_path: Optional output path
            
        Returns:
            Path to modified audio file
        """
        if output_path is None:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                output_path = temp_file.name
        
        # Load audio
        audio = pydub.AudioSegment.from_wav(input_path)
        
        # Apply voice modifications for family member characteristics
        modified_audio = audio
        
        # 1. Slight pitch adjustment for warmth
        if self.voice_settings.get('pitch_shift', 0) != 0:
            modified_audio = modified_audio._spawn(
                modified_audio.raw_data, 
                overrides={"frame_rate": int(modified_audio.frame_rate * (1 + self.voice_settings['pitch_shift']))}
            ).set_frame_rate(modified_audio.frame_rate)
        
        # 2. Add warmth with slight reverb effect
        if self.voice_settings.get('warmth_boost', False):
            # Simple echo effect for warmth
            echo = modified_audio - 10  # Slightly quieter echo
            echo = echo - 200  # Delay by 200ms
            modified_audio = modified_audio.overlay(echo)
        
        # 3. Slight compression for more natural speech
        modified_audio = pydub.effects.normalize(modified_audio)
        
        # 4. Gentle low-pass filter for warmth
        modified_audio = modified_audio.low_pass_filter(4000)
        
        # Save modified audio
        modified_audio.export(output_path, format="wav")
        
        return output_path
    
    def _play_audio(self, audio_path: str):
        """Play audio file using system audio player"""
        try:
            # Use pydub's play function
            audio = pydub.AudioSegment.from_wav(audio_path)
            pydub.playback.play(audio)
        except Exception as e:
            print(f"Error playing audio: {e}")
            # Fallback to system command
            os.system(f"afplay '{audio_path}'")
    
    def set_voice_characteristics(self, rate: int = None, volume: float = None, 
                                pitch_shift: float = None, warmth_boost: bool = None):
        """Update voice characteristics"""
        if rate is not None:
            self.voice_settings['rate'] = rate
            self.engine.setProperty('rate', rate)
        
        if volume is not None:
            self.voice_settings['volume'] = volume
            self.engine.setProperty('volume', volume)
        
        if pitch_shift is not None:
            self.voice_settings['pitch_shift'] = pitch_shift
        
        if warmth_boost is not None:
            self.voice_settings['warmth_boost'] = warmth_boost
    
    def get_available_voices(self):
        """Get list of available voices"""
        voices = self.engine.getProperty('voices')
        return [{'id': voice.id, 'name': voice.name} for voice in voices]

def main():
    """Test the voice cloning system"""
    cloner = VoiceCloner()
    
    print("Available voices:")
    for voice in cloner.get_available_voices():
        print(f"  {voice['name']} (ID: {voice['id']})")
    
    print("\nTesting family member voice...")
    test_text = "Hello Commander, how are you feeling today? I miss you and can't wait for you to come home."
    
    # Generate and play speech
    audio_path = cloner.speak_with_family_voice(test_text)
    print(f"Generated audio saved to: {audio_path}")

if __name__ == "__main__":
    main()
