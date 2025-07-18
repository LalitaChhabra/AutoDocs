from openai import AzureOpenAI
import os 
import requests 
import requests.exceptions
from dotenv import load_dotenv
import re

load_dotenv()



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
    try:
        # Validate environment variables first
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        
        if not api_key:
            raise ValueError("Missing AZURE_OPENAI_API_KEY environment variable")
        if not endpoint:
            raise ValueError("Missing AZURE_OPENAI_ENDPOINT environment variable")
        if not deployment:
            raise ValueError("Missing AZURE_OPENAI_DEPLOYMENT environment variable")
        
        print(f"Connecting to Azure OpenAI endpoint: {endpoint}")
        print(f"Using deployment: {deployment}")
        
        client = AzureOpenAI(
            api_key=api_key,
            api_version="2024-02-15-preview",
            azure_endpoint=endpoint,
            timeout=30.0  # Add timeout
        )

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
        
    except requests.exceptions.ConnectionError as e:
        print(f"Network connection error: {str(e)}")
        raise Exception(f"Network connection error. Please check your internet connection and Azure OpenAI endpoint configuration.")
    except requests.exceptions.Timeout as e:
        print(f"Request timeout error: {str(e)}")
        raise Exception(f"Request timed out. The Azure OpenAI service may be slow or unavailable.")
    except Exception as e:
        print(f"Error in summarize_transcription: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        # Check if it's an authentication error
        if "401" in str(e) or "unauthorized" in str(e).lower():
            raise Exception(f"Authentication error. Please check your AZURE_OPENAI_API_KEY.")
        elif "404" in str(e):
            raise Exception(f"Service not found. Please check your AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_DEPLOYMENT.")
        elif "429" in str(e):
            raise Exception(f"Rate limit exceeded. Please wait and try again.")
        else:
            raise Exception(f"Azure OpenAI error: {str(e)}")


def clean_summary(summary: str) -> str:
    summary = re.sub(r"\*\*(.*?)\*\*", r"\1", summary)  # remove bold
    summary = re.sub(r"^#+\s*", "", summary, flags=re.MULTILINE)  # remove heading markers
    return summary.strip()


