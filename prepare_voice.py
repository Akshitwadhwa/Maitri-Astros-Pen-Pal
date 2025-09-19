#!/usr/bin/env python3
"""
Voice Preparation Script
Helps prepare your recorded audio for voice cloning
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_audio_file(audio_path: str) -> dict:
    """Check if audio file is suitable for voice cloning"""
    if not os.path.exists(audio_path):
        return {"valid": False, "error": "File not found"}
    
    try:
        # Get audio info using ffprobe
        cmd = [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_format", "-show_streams",
            audio_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return {"valid": False, "error": "Could not analyze audio file"}
        
        info = json.loads(result.stdout)
        format_info = info["format"]
        stream_info = info["streams"][0]
        
        duration = float(format_info["duration"])
        sample_rate = int(stream_info["sample_rate"])
        channels = int(stream_info["channels"])
        bit_rate = int(format_info.get("bit_rate", 0))
        
        # Check if suitable for voice cloning
        issues = []
        recommendations = []
        
        if duration < 5:
            issues.append("Audio too short (less than 5 seconds)")
            recommendations.append("Record at least 10-30 seconds of speech")
        elif duration > 60:
            issues.append("Audio too long (more than 60 seconds)")
            recommendations.append("Use 10-30 seconds for best results")
        
        if sample_rate < 16000:
            issues.append("Low sample rate (less than 16kHz)")
            recommendations.append("Record at 22kHz or higher")
        
        if channels > 1:
            issues.append("Stereo audio detected")
            recommendations.append("Mono audio works better for voice cloning")
        
        if bit_rate < 64000:
            issues.append("Low bit rate")
            recommendations.append("Use higher quality recording")
        
        return {
            "valid": len(issues) == 0,
            "duration": duration,
            "sample_rate": sample_rate,
            "channels": channels,
            "bit_rate": bit_rate,
            "issues": issues,
            "recommendations": recommendations
        }
        
    except Exception as e:
        return {"valid": False, "error": str(e)}

def prepare_audio(input_path: str, output_path: str) -> bool:
    """Prepare audio file for voice cloning"""
    try:
        cmd = [
            "ffmpeg", "-i", input_path,
            "-ar", "22050",  # Sample rate
            "-ac", "1",      # Mono
            "-acodec", "pcm_s16le",  # 16-bit PCM
            "-y",            # Overwrite output
            output_path
        ]
        
        print(f"🔄 Preparing audio: {input_path} -> {output_path}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Audio prepared successfully")
            return True
        else:
            print(f"❌ Error preparing audio: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ ffmpeg not found. Please install it:")
        print("   brew install ffmpeg")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🎤 Voice Preparation Tool")
    print("=" * 30)
    
    if len(sys.argv) != 2:
        print("Usage: python3 prepare_voice.py <audio_file>")
        print("Example: python3 prepare_voice.py my_voice.mp3")
        sys.exit(1)
    
    input_path = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(input_path):
        print(f"❌ File not found: {input_path}")
        sys.exit(1)
    
    # Check audio file
    print(f"🔍 Analyzing: {input_path}")
    audio_info = check_audio_file(input_path)
    
    if not audio_info["valid"]:
        print(f"❌ Audio file issues:")
        for issue in audio_info.get("issues", []):
            print(f"   - {issue}")
        print("\n💡 Recommendations:")
        for rec in audio_info.get("recommendations", []):
            print(f"   - {rec}")
        
        if "error" in audio_info:
            print(f"\n❌ Error: {audio_info['error']}")
            sys.exit(1)
        
        print("\n⚠️  Audio may not work well for voice cloning")
        proceed = input("Continue anyway? (y/N): ").strip().lower()
        if proceed != 'y':
            sys.exit(1)
    else:
        print("✅ Audio file looks good for voice cloning")
    
    # Show audio info
    print(f"\n📊 Audio Information:")
    print(f"   Duration: {audio_info.get('duration', 0):.1f} seconds")
    print(f"   Sample Rate: {audio_info.get('sample_rate', 0)} Hz")
    print(f"   Channels: {audio_info.get('channels', 0)}")
    print(f"   Bit Rate: {audio_info.get('bit_rate', 0)} bps")
    
    # Prepare audio
    output_path = "voice_samples/prepared_voice.wav"
    os.makedirs("voice_samples", exist_ok=True)
    
    if prepare_audio(input_path, output_path):
        print(f"\n✅ Voice prepared successfully!")
        print(f"   Output: {output_path}")
        print(f"\n🎯 Next steps:")
        print(f"   1. Test voice cloning: python3 voice_cloning_advanced.py")
        print(f"   2. Use in chat: /voice {output_path}")
    else:
        print("\n❌ Failed to prepare audio")
        sys.exit(1)

if __name__ == "__main__":
    main()
