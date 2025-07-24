# AutoDocs

AutoDocs is a Python-based tool for recording your screen and audio, then automatically generating professional documentation (Markdown, HTML) using AI-powered transcription and summarization. It is designed for creating tutorials, guides, and step-by-step documentation with minimal effort.

## Features

- **Screen & Audio Recording**: Capture your screen and microphone with synchronized mouse click visualization.
- **Custom Clip Duration**: Record clips from 10 to 60 seconds, with easy selection in the GUI.
- **Session Management**: Manage, process, and review multiple clips in a session.
- **AI-Powered Processing**:
  - Transcribe audio using Azure OpenAI Whisper
  - Summarize content using Azure OpenAI GPT-4o
- **Output Formats**:
  - Markdown (.md)
  - HTML (.html) with embedded GIFs and audio
- **GUI & CLI Modes**: Use a modern PyQt5 GUI or a command-line interface.
- **Session Details**: View session summaries and detailed clip info.

## Requirements

- Python 3.8+
- Azure OpenAI API access (for transcription and summarization)
- Windows OS recommended (tested)

## Installation

1. **Clone the repository:**
   ```
   git clone https://github.com/yourusername/AutoDocs.git
   cd AutoDocs
   ```

2. **Create and activate a virtual environment (recommended):**
   ```
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies:**
   ```
   pip install -r requirements.txt
   pip install -r audiovisual/requirements.txt
   pip install -r transcribe/requirements.txt
   ```

4. **Configure Azure OpenAI:**
   - Add your Azure OpenAI credentials to the environment (see `transcribe/.env.example`).

## Usage

### GUI Mode (Recommended)

Run the graphical interface:

```
python gui_launcher.py
```

This launches a floating control bar with buttons to:
- **Record**: Start a new screen/audio recording
- **Manage**: View and process recorded clips
- **Generate**: Create documentation (Markdown, HTML)

### Command Line Mode

Run the CLI interface:

```
python main.py
```

Follow the prompts to record, process, and generate documentation.

### Quick Mode

Record a single clip and generate documentation automatically:

```
python main.py --quick
```

## Project Structure

- `main.py` — Main entry point (CLI and GUI launcher)
- `gui_launcher.py` — PyQt5 GUI for recording and documentation
- `autodocs_orchestrator.py` — Core logic for managing clips and sessions
- `audiovisual/` — Screen/audio recording and mouse click tracking
- `transcribe/` — AI-powered transcription and summarization
- `autodocs_output/` — Output files and session data

## Workflow

1. **Record**: Capture screen and audio clips
2. **Process**: Transcribe and summarize clips using Azure OpenAI
3. **Generate**: Create Markdown, or HTML documentation
4. **Review**: Manage sessions and view detailed info

## Azure Integration

AutoDocs uses Azure OpenAI for transcription and summarization. You must provide your Azure API key and endpoint in the environment configuration.

## License

MIT License

Copyright (c) 2025 AutoDocs (Part of Avanade Proprietory Technology)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


MIT License
# AutoDocs

