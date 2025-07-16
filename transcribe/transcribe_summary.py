from openai import AzureOpenAI
import openai 
import os 
import requests 
from dotenv import load_dotenv
import re

load_dotenv()
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_type = "azure"
openai.api_version = "2025-01-01-preview"
api_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")



def transcribe_audio(file_path):
    """
    Transcibe local audio file using Azure OpenAI Whisper API.
    """

    whisper_url = os.getenv("WHISPER_ENDPOINT")
    whisper_key = os.getenv("WHISPER_KEY")

    if not whisper_url or not whisper_key:
        raise ValueError("Missing WHISPER_ENDPOINT or WHISPER_KEY environment variable.")

    headers = {
        "api-key": whisper_key,
    }

    with open(file_path, "rb") as audio_file:
        files = {
            "file": (os.path.basename(file_path), audio_file, "application/octet-stream"),
        }
        data = {
            "response_format": "text",
            "language": "en"
        }

        response = requests.post(whisper_url, headers=headers, files=files, data=data)
        response.raise_for_status()


    if response.status_code == 200:
        transcription = response.text.strip()
        return transcription
    else:
        raise Exception(f"Error transcribing audio: {response.status_code} - {response.text}")
    
def summarize_transcription(transcript):
    """
    Summarize the transcription using Azure OpenAI GPT-4o.
    """

    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2024-02-15-preview",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )

    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that summarizes tutorials into clear instructions."
            },
            {
                "role": "user",
                "content": f"Please summarize the following tutorial into a 1 step short 2-3 sentence summary:\n\n{transcript}"
            }
        ],
        temperature=0.3,
        max_tokens=800
    )
    if not response.choices or not response.choices[0].message:
        raise ValueError("No valid response from the model.")

    result = response.choices[0].message.content

    result = clean_summary(result)  # Clean the summary to remove unwanted formatting

    # Return the summarized content
    return result


def clean_summary(summary: str) -> str:
    summary = re.sub(r"\*\*(.*?)\*\*", r"\1", summary)  # remove bold
    summary = re.sub(r"^#+\s*", "", summary, flags=re.MULTILINE)  # remove heading markers
    return summary.strip()


