from flask import Flask, render_template, request
from google.cloud import texttospeech
import os

# Set Google credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "your_google_credentials.json"

app = Flask(__name__)
client = texttospeech.TextToSpeechClient()

@app.route("/", methods=["GET", "POST"])
def index():
    audio_file = None

    if request.method == "POST":
        text = request.form["text"]
        language = request.form["language"]
        gender = request.form["gender"]

        # Language & Voice Mapping
        if language == "English":
            lang_code = "en-US"
            voice_name = "en-US-Wavenet-D" if gender == "Male" else "en-US-Wavenet-F"
        elif language == "Hindi":
            lang_code = "hi-IN"
            voice_name = "hi-IN-Wavenet-B" if gender == "Male" else "hi-IN-Wavenet-A"
        else:  # Hinglish
            lang_code = "en-IN"
            voice_name = "en-IN-Wavenet-C" if gender == "Male" else "en-IN-Wavenet-D"

        # Voice params
        voice = texttospeech.VoiceSelectionParams(
            language_code=lang_code,
            name=voice_name,
            ssml_gender=texttospeech.SsmlVoiceGender.MALE if gender == "Male" else texttospeech.SsmlVoiceGender.FEMALE,
        )

        # Input text
        synthesis_input = texttospeech.SynthesisInput(text=text)

        # Audio config
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

        # Generate speech
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        # Save audio file in static folder
        audio_file = "static/output.mp3"
        with open(audio_file, "wb") as out:
            out.write(response.audio_content)

    return render_template("index.html", audio_file=audio_file)

if __name__ == "__main__":
    app.run(debug=True)
