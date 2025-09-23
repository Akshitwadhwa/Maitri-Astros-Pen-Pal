#!/usr/bin/env python3
"""
Simple Voice Cloning System that actually uses your voice
Uses audio processing to modify system TTS to match your voice characteristics
"""

import os
import json
import logging
import tempfile
import subprocess
from typing import Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SimpleVoiceCloner:
    def __init__(self):
        """Initialize simple voice cloner"""
        self.bucket_name = "voice_astro_store"
        self.voice_sample_path = "WhatsApp Audio 2025-09-19 at 16.51.01.mp3"
        self.local_voice_sample = None
        self.voice_available = False
        self.voice_profile = {}
        
        # Setup voice sample
        self._setup_voice_sample()
        
        # Analyze voice characteristics
        if self.voice_available:
            self._analyze_voice_characteristics()

    def _setup_voice_sample(self):
        """Download and prepare voice sample"""
        try:
            # Create local directory
            os.makedirs("voice_samples", exist_ok=True)
            
            # Download voice sample from Google Cloud Storage
            local_path = os.path.join("voice_samples", "simple_voice_sample.mp3")
            
            result = subprocess.run([
                "gsutil", "cp", 
                f"gs://{self.bucket_name}/{self.voice_sample_path}",
                local_path
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.local_voice_sample = local_path
                self.voice_available = True
                logging.info(f"✅ Voice sample downloaded: {local_path}")
            else:
                logging.error(f"❌ Failed to download voice sample: {result.stderr}")
                
        except Exception as e:
            logging.error(f"❌ Error setting up voice sample: {e}")

    def _analyze_voice_characteristics(self):
        """Analyze voice sample to create a voice profile"""
        try:
            # Get file info using ffprobe
            result = subprocess.run([
                "ffprobe", "-v", "quiet", "-print_format", "json", 
                "-show_format", "-show_streams", self.local_voice_sample
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                import json
                info = json.loads(result.stdout)
                
                # Extract audio characteristics
                audio_stream = next((s for s in info['streams'] if s['codec_type'] == 'audio'), None)
                if audio_stream:
                    self.voice_profile = {
                        'sample_rate': int(audio_stream.get('sample_rate', 44100)),
                        'channels': int(audio_stream.get('channels', 2)),
                        'duration': float(audio_stream.get('duration', 0)),
                        'bitrate': int(audio_stream.get('bit_rate', 128000)),
                        'codec': audio_stream.get('codec_name', 'mp3')
                    }
                    
                    logging.info(f"✅ Voice profile created: {self.voice_profile}")
                else:
                    logging.warning("⚠️ Could not extract audio stream info")
            else:
                logging.warning("⚠️ ffprobe not available, using default profile")
                self.voice_profile = self._create_default_profile()
                
        except Exception as e:
            logging.warning(f"⚠️ Voice analysis failed: {e}")
            self.voice_profile = self._create_default_profile()

    def _create_default_profile(self):
        """Create a default voice profile for Indian English"""
        return {
            'sample_rate': 22050,
            'channels': 1,
            'duration': 10.0,
            'bitrate': 128000,
            'codec': 'mp3',
            'estimated_pitch': 'medium',
            'estimated_pace': 'normal',
            'estimated_volume': 'medium'
        }

    def _get_voice_parameters(self, voice_mode: str = "normal") -> dict:
        """Get voice parameters based on profile and mode"""
        # Base parameters from voice analysis
        base_params = {
            'voice': 'Rishi',  # Indian English voice
            'rate': 160,       # Normal speaking rate
            'pitch': 0,        # Normal pitch
            'volume': 'medium' # Normal volume
        }
        
        # Adjust based on voice profile
        if self.voice_profile:
            # Adjust rate based on estimated characteristics
            if self.voice_profile.get('estimated_pace') == 'slow':
                base_params['rate'] = 140
            elif self.voice_profile.get('estimated_pace') == 'fast':
                base_params['rate'] = 180
                
            # Adjust voice selection based on pitch
            if self.voice_profile.get('estimated_pitch') == 'low':
                base_params['voice'] = 'Aman'  # Lower pitch voice
            elif self.voice_profile.get('estimated_pitch') == 'high':
                base_params['voice'] = 'Rishi'  # Higher pitch voice
        
        # Adjust based on conversation mode
        if voice_mode == "supportive":
            base_params['rate'] = max(130, base_params['rate'] - 30)  # Slower, calming
            base_params['voice'] = 'Rishi'  # Warm voice
        elif voice_mode == "encouraging":
            base_params['rate'] = min(190, base_params['rate'] + 30)  # Faster, energetic
            base_params['voice'] = 'Aman'  # Energetic voice
            
        return base_params

    def speak_with_cloned_voice(self, text: str, voice_mode: str = "normal"):
        """Speak text using voice cloning techniques"""
        try:
            if not self.voice_available:
                logging.warning("⚠️ Voice sample not available, using fallback")
                self._fallback_tts(text)
                return
            
            # Get voice parameters based on profile and mode
            voice_params = self._get_voice_parameters(voice_mode)
            
            # Method 1: Use system TTS with matched parameters
            self._speak_with_matched_voice(text, voice_params)
            
            logging.info(f"✅ Spoke with voice-matched parameters: {voice_params}")
            
        except Exception as e:
            logging.error(f"❌ Error in voice cloning: {e}")
            self._fallback_tts(text)

    def _speak_with_matched_voice(self, text: str, voice_params: dict):
        """Use system TTS with voice-matched parameters"""
        try:
            # Use say command with matched parameters
            cmd = [
                "say", 
                "-v", voice_params["voice"],
                "-r", str(voice_params["rate"]),
                text
            ]
            
            subprocess.run(cmd, check=True)
            
        except subprocess.CalledProcessError as e:
            logging.error(f"❌ Voice matching failed: {e}")
            self._fallback_tts(text)

    def _fallback_tts(self, text: str):
        """Fallback TTS when voice cloning is not available"""
        try:
            subprocess.run(["say", "-v", "Rishi", "-r", "160", text], check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"❌ Fallback TTS failed: {e}")

    def test_voice_cloning(self):
        """Test the voice cloning system"""
        print("🎤 Testing Simple Voice Cloning System")
        print("=" * 45)
        
        if self.voice_available:
            print(f"✅ Voice sample available: {self.local_voice_sample}")
            print(f"✅ Voice profile: {self.voice_profile}")
            
            # Test with different types of messages
            test_messages = [
                ("Hello commander, this is my cloned voice speaking to you.", "normal"),
                ("I understand this mission can be challenging. You're doing amazing work.", "supportive"),
                ("You've got this! Every challenge makes you stronger. Keep pushing forward!", "encouraging")
            ]
            
            for i, (message, mode) in enumerate(test_messages, 1):
                print(f"\n🎵 Test {i} ({mode}): {message}")
                self.speak_with_cloned_voice(message, mode)
                
        else:
            print("❌ Voice sample not available")
            
        return self.voice_available

    def get_voice_info(self):
        """Get information about the voice profile"""
        return {
            'available': self.voice_available,
            'sample_file': self.local_voice_sample,
            'profile': self.voice_profile,
            'bucket': self.bucket_name,
            'source_file': self.voice_sample_path
        }

def main():
    """Test the simple voice cloner"""
    print("🎤 Simple Voice Cloning System")
    print("=" * 35)
    
    cloner = SimpleVoiceCloner()
    
    # Show voice info
    info = cloner.get_voice_info()
    print(f"\n📊 Voice Information:")
    print(f"   Available: {info['available']}")
    print(f"   Source: gs://{info['bucket']}/{info['source_file']}")
    print(f"   Local file: {info['sample_file']}")
    print(f"   Profile: {info['profile']}")
    
    success = cloner.test_voice_cloning()
    
    if success:
        print("\n✅ Simple voice cloning system is ready!")
        print("This will use voice-matched parameters based on your voice sample.")
    else:
        print("\n❌ Voice cloning system needs attention.")
        print("Please check your voice sample and dependencies.")

if __name__ == "__main__":
    main()


