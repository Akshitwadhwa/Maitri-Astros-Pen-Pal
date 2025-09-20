# Custom Voice TTS Setup Instructions

## Quick Setup Guide

Since you've already uploaded your voice samples to Google Cloud Storage, follow these steps to configure your system:

### 1. Set Environment Variables

Replace the values below with your actual Google Cloud details:

```bash
# Your Google Cloud Storage bucket name
export GCS_BUCKET_NAME="your-bucket-name"

# Path to your voice sample in the bucket
export GCS_VOICE_SAMPLE_PATH="voice_samples/your_voice_file.wav"

# Path to your Google Cloud service account JSON file
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account.json"
```

### 2. Example Configuration

If your setup looks like this:
- Bucket name: `my-voice-samples`
- Voice file: `voice_samples/family_voice.wav`
- Service account: `/Users/username/Downloads/service-account.json`

Then run:
```bash
export GCS_BUCKET_NAME="my-voice-samples"
export GCS_VOICE_SAMPLE_PATH="voice_samples/family_voice.wav"
export GOOGLE_APPLICATION_CREDENTIALS="/Users/username/Downloads/service-account.json"
```

### 3. Make Variables Permanent

Add these lines to your shell configuration file:

```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'export GCS_BUCKET_NAME="your-bucket-name"' >> ~/.bashrc
echo 'export GCS_VOICE_SAMPLE_PATH="voice_samples/your_voice_file.wav"' >> ~/.bashrc
echo 'export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account.json"' >> ~/.bashrc
```

### 4. Test Your Setup

```bash
python3 test_gcp_setup.py
```

### 5. Run the Custom Voice Chatbot

```bash
python3 chat_custom_voice.py
```

## What You Need to Provide

Please tell me:

1. **Bucket Name**: What's the name of your Google Cloud Storage bucket?
2. **Voice File Path**: What's the exact path to your voice sample in the bucket?
3. **Service Account**: Do you have a Google Cloud service account JSON file?

## Troubleshooting

### If you don't have a service account JSON file:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to "IAM & Admin" > "Service Accounts"
3. Create a new service account
4. Download the JSON key file
5. Enable Text-to-Speech and Storage APIs

### If you're not sure about your bucket details:
```bash
# List your buckets
gsutil ls

# List files in a specific bucket
gsutil ls gs://your-bucket-name/
```

## Ready to Test?

Once you provide the bucket details, I can help you:
1. Test the voice synthesis
2. Run the chatbot with your custom voice
3. Troubleshoot any issues

Just let me know your Google Cloud Storage details!
