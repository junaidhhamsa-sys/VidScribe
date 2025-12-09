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
├─ config.py
├─ core
│  ├─ audio_processor.py
│  ├─ gemini_processor.py
│  ├─ keyframe_extractor.py
│  └─ __init__.py
├─ docs
│  ├─ API_REFERENCE.md
│  ├─ edu5.pdf
│  ├─ GEMINI_SETUP.md
│  ├─ LOGGING_INFO.md
│  ├─ QUICKSTART.md
│  └─ WORKFLOW.md
├─ generators
│  ├─ pdf_generator.py
│  ├─ ppt_generator.py
│  ├─ ppt_template
│  │  ├─ creative.py
│  │  ├─ educational.py
│  │  ├─ minimalist.py
│  │  ├─ modern_tech.py
│  │  ├─ professional.py
│  │  └─ __init__.py
│  └─ __init__.py
├─ pipeline
│  ├─ video_pipeline.py
│  └─ __init__.py
├─ README.md
├─ requirements.txt
├─ start.sh
├─ static
│  ├─ css
│  │  └─ style.css
│  ├─ images
│  │  ├─ logo.png
│  │  └─ templates
│  │     ├─ creative.png
│  │     ├─ educational.png
│  │     ├─ minimalist.png
│  │     ├─ modern_tech.png
│  │     └─ professional.png
│  └─ js
│     └─ script.js
├─ templates
│  └─ index.html
├─ text_summarizer.txt
└─ utils
   ├─ file_handler.py
   ├─ helpers.py
   ├─ logger.py
   ├─ validators.py
   └─ __init__.py

```


# testing command 

python -m pipeline.video_pipeline "C:\Users\Strix\Downloads\What Is n8n_ The Beginner-Friendly Automation Tool Explained.mp4" ppt professional
```
Vidscribe-main
├─ app.py
├─ config.py
├─ core
│  ├─ audio_processor.py
│  ├─ gemini_processor.py
│  ├─ keyframe_extractor.py
│  └─ __init__.py
├─ docs
│  ├─ API_REFERENCE.md
│  ├─ edu5.pdf
│  ├─ GEMINI_SETUP.md
│  ├─ LOGGING_INFO.md
│  ├─ QUICKSTART.md
│  └─ WORKFLOW.md
├─ generators
│  ├─ pdf_generator.py
│  ├─ ppt_generator.py
│  ├─ ppt_templates
│  │  ├─ creative.py
│  │  ├─ educational.py
│  │  ├─ minimalist.py
│  │  ├─ modern_tech.py
│  │  ├─ professional.py
│  │  └─ __init__.py
│  └─ __init__.py
├─ pipeline
│  ├─ video_pipeline.py
│  └─ __init__.py
├─ README.md
├─ requirements.txt
├─ start.sh
├─ static
│  ├─ css
│  │  └─ style.css
│  ├─ images
│  │  ├─ logo.png
│  │  └─ templates
│  │     ├─ creative.png
│  │     ├─ educational.png
│  │     ├─ minimalist.png
│  │     ├─ modern_tech.png
│  │     └─ professional.png
│  └─ js
│     └─ script.js
├─ templates
│  └─ index.html
├─ test files
└─ utils
   ├─ file_handler.py
   ├─ helpers.py
   ├─ logger.py
   ├─ validators.py
   └─ __init__.py

```