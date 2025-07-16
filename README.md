# AutoDocs

AutoDocs is a Python application that automatically transcribes audio files and generates concise summaries using Azure OpenAI services. It combines Azure OpenAI's Whisper API for audio transcription and GPT-4 for intelligent summarization.

## Features

- **Audio Transcription**: Convert audio files to text using Azure OpenAI Whisper API
- **Intelligent Summarization**: Generate clear, concise summaries from transcribed content using GPT-4
- **Text Cleaning**: Automatically removes formatting artifacts for clean output
- **Environment Configuration**: Secure credential management using environment variables

## Prerequisites

- Python 3.7 or higher
- Azure OpenAI account with access to:
  - Whisper API for transcription
  - GPT-4 deployment for summarization
- Audio files in supported formats (MP3, WAV, M4A, etc.)

## Setup Instructions

### 1. Clone or Download the Project

```bash
# If using Git
git clone <repository-url>
cd AutoDocs

# Or download and extract the ZIP file
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   copy .env.example .env
   ```

2. Edit the `.env` file and add your Azure OpenAI credentials:
   ```bash
   AZURE_OPENAI_API_KEY=your_api_key_here
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT=your_gpt4_deployment_name
   WHISPER_ENDPOINT=https://your-whisper-endpoint/openai/deployments/whisper/audio/transcriptions?api-version=2024-02-15-preview
   WHISPER_KEY=your_whisper_api_key
   ```

### 4. Usage

Import and use the functions in your Python scripts:

```python
from transcribe_summary import transcribe_audio, summarize_transcription

# Transcribe an audio file
transcript = transcribe_audio("path/to/your/audio/file.mp3")

# Generate a summary
summary = summarize_transcription(transcript)

print("Summary:", summary)
```

## Configuration Details

### Required Environment Variables

| Variable | Description |
|----------|-------------|
| `AZURE_OPENAI_API_KEY` | Your Azure OpenAI API key |
| `AZURE_OPENAI_ENDPOINT` | Your Azure OpenAI resource endpoint |
| `AZURE_OPENAI_DEPLOYMENT` | Name of your GPT-4 deployment |
| `WHISPER_ENDPOINT` | Azure OpenAI Whisper API endpoint |
| `WHISPER_KEY` | API key for Whisper service |

### Supported Audio Formats

The Whisper API supports various audio formats including:
- MP3
- WAV
- M4A
- FLAC
- And more

## Example Workflow

1. **Transcription**: The `transcribe_audio()` function sends your audio file to Azure OpenAI Whisper API
2. **Summarization**: The `summarize_transcription()` function processes the transcript through GPT-4
3. **Cleaning**: Text formatting is automatically cleaned for better readability

## Troubleshooting

- **Missing credentials**: Ensure all environment variables are properly set in your `.env` file
- **File format issues**: Make sure your audio file is in a supported format
- **API errors**: Check that your Azure OpenAI deployments are active and have sufficient quota

## Dependencies

- `openai>=1.0.0` - Azure OpenAI Python SDK
- `requests` - HTTP library for API calls
- `python-dotenv` - Environment variable management