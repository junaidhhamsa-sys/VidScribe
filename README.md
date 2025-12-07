# Video Summarizer

AI-powered video summarization tool that converts long videos into concise PowerPoint presentations.

## Features

- **Keyframe Extraction**: Automatically extracts meaningful frames using OpenCV
- **Audio Transcription**: Converts speech to text using OpenAI Whisper
- **Image Captioning**: Generates descriptions for visual content
- **Text Summarization**: Creates concise summaries combining audio and visual information
- **PowerPoint Generation**: Automatically creates professional presentations

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) Set up OpenAI API key for GPT-4 Vision:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Usage

### Web Application

Start the web server:
```bash
cd video_summarizer
python app.py
```

Then open your browser to `http://localhost:5000`

### Command Line

Process a video directly:
```bash
cd video_summarizer
python pipeline.py path/to/your/video.mp4
```

## Configuration

Edit `config.py` to adjust:
- Keyframe extraction sensitivity
- Whisper model size (tiny, base, small, medium, large)
- Maximum number of keyframes
- Summary length
- PowerPoint styling

## Project Structure

```
video_summarizer/
├── app.py                  # Flask web application
├── pipeline.py             # Main orchestration pipeline
├── config.py               # Configuration settings
├── keyframe_extractor.py   # OpenCV keyframe extraction
├── audio_processor.py      # Audio extraction & Whisper transcription
├── caption_generator.py    # Image captioning
├── text_summarizer.py      # Text summarization
├── ppt_generator.py        # PowerPoint generation
├── templates/              # HTML templates
├── static/                 # CSS and JavaScript
├── utils/                  # Helper functions
├── uploads/                # Uploaded videos
├── output/                 # Generated presentations
└── temp/                   # Temporary files
```

## Requirements

- Python 3.8+
- OpenCV
- MoviePy
- Whisper
- python-pptx
- Flask

## License

MIT License

```
Vidscribe-main
├─ app.py
├─ audio_processor.py
├─ caption_generator.py
├─ config.py
├─ content_summarizer.py
├─ GEMINI_SETUP.md
├─ gemini_video_analyzer.py
├─ keyframe_extractor.py
├─ LOGGING_INFO.md
├─ pipeline.py
├─ pipeline_gemini.py
├─ ppt_generator.py
├─ QUICKSTART.md
├─ README.md
├─ requirements.txt
├─ start.sh
├─ static
│  ├─ script.js
│  └─ style.css
├─ templates
│  └─ index.html
├─ text_summarizer.py
├─ utils
│  ├─ helpers.py
│  └─ __init__.py
└─ WORKFLOW.md

```