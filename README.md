# 🎧 PDF to Audiobook Converter

A comprehensive, enterprise-grade web application that converts PDF documents into high-quality audio files with advanced features including OCR, AI summarization, batch processing, and multiple TTS engines. Built with Streamlit and FastAPI, this tool transforms your PDFs into listenable audiobooks with professional-grade capabilities.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

### 🔍 OCR for Scanned PDFs
- Extract text from image-based and scanned PDFs using Tesseract OCR
- Automatic fallback to standard extraction if OCR fails
- Configurable DPI for optimal text recognition
- Handles complex layouts and multi-page documents

### 🤖 AI-Powered Summarization
- Generate intelligent summaries before conversion
- Three summarization methods:
  - **Simple Extractive**: Fast, rule-based summarization
  - **OpenAI GPT**: Advanced AI summarization (requires API key)
  - **HuggingFace**: Local ML-based summarization (requires PyTorch)
- Configurable summary length
- Preview summary before audio conversion

### 📦 Batch Processing
- Convert multiple PDFs simultaneously
- Parallel processing with configurable worker count
- Real-time progress tracking
- Comprehensive batch results summary
- Individual file status reporting

### � Multiple TTS Engines
- **gTTS**: Google Text-to-Speech (online, high quality)
- **pyttsx3**: Offline TTS (no internet required)
- **edge-tts**: Microsoft Edge TTS (premium voices)
- Engine selection based on requirements
- Automatic fallback on engine failure

### � Multi-Language Support
Convert PDFs to audio in 13+ languages including:
- English, Spanish, French, German
- Hindi, Japanese, Italian, Portuguese
- Russian, Chinese (Simplified), Korean, Dutch, Arabic

### 📄 Smart Page Selection
- Convert entire PDFs or specific page ranges
- Custom page selection (e.g., "1-5, 8, 10-12")
- Perfect for extracting specific chapters or sections

### 📝 Text Editing & Preview
- Preview extracted text before conversion
- Edit content directly in the browser
- Clean formatting options for better audio output

### 🧹 Text Preprocessing
- Remove extra spaces and newlines
- Filter special characters
- Optimize text for natural speech synthesis

### 📊 Statistics Dashboard
- Real-time word count
- Character count tracking
- Estimated audio duration
- Pages processed indicator

### 📜 Conversion History
- Track recent conversions with detailed metadata
- View language, duration, word count, and engine used
- Clear history option

### 🎨 Modern UI
- Beautiful gradient design
- Dark mode support
- Responsive layout
- Intuitive user interface

### 🔌 REST API
- Full REST API built with FastAPI
- Programmatic access to all features
- Batch conversion endpoints
- Summarization API
- Speech-to-Text transcription API
- Health check endpoints
- Swagger/OpenAPI documentation

### 🎤 Speech-to-Text
- Convert audio files to text
- Multiple STT engines (Google, Sphinx, Whisper)
- Multi-language support
- Real-time transcription
- Download transcribed text

### ⚡ Fast Performance
- Quick text extraction
- Efficient audio generation
- Progress tracking during conversion
- Parallel batch processing

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Tesseract OCR (for OCR feature) - [Download here](https://github.com/tesseract-ocr/tesseract)
- Poppler (for PDF to image conversion) - Included with pdf2image on most systems
- PyAudio (for audio recording) - Install separately if needed

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd SelfProjects
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install Tesseract OCR (for OCR feature):
- **Windows**: Download from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
- **macOS**: `brew install tesseract`
- **Linux**: `sudo apt-get install tesseract-ocr`

4. Install PyAudio (for STT feature):
- **Windows**: `pip install pyaudio-win32`
- **macOS**: `brew install portaudio && pip install pyaudio`
- **Linux**: `sudo apt-get install python3-pyaudio`

5. Run the Streamlit application:
```bash
streamlit run PDF2Voice.py
```

The application will open in your default web browser at `http://localhost:8501`

6. Run the REST API (optional):
```bash
python api.py
```

The API will be available at `http://localhost:8000` with Swagger docs at `http://localhost:8000/docs`

## 📖 Usage

### Quick Start

**PDF to Audio:**
1. **Upload PDF**: Click the "Browse files" button and select your PDF document
2. **Configure Settings**: 
   - Choose your preferred language from the sidebar
   - Select TTS engine (gTTS for online, pyttsx3 for offline)
   - Toggle slow speech if needed
   - Select page range (all pages or custom)
   - Enable text cleaning options
   - Enable OCR for scanned PDFs
   - Enable AI summarization if desired
3. **Preview Text**: Click "Preview Extracted Text" to see and edit the content
4. **Convert**: Click the "Convert to Audio" button
5. **Listen or Download**: Play the audio in your browser or download the MP3 file

**Audio to Text:**
1. **Select Mode**: Choose "Audio to Text" from the mode selector
2. **Upload Audio**: Upload a WAV, FLAC, or AIFF audio file
3. **Configure Settings**: 
   - Select STT engine (Google for high accuracy, Sphinx for offline)
   - Choose audio language
4. **Transcribe**: Click "Transcribe to Text" button
5. **View & Download**: View the transcribed text and download as text file

### Advanced Features

#### OCR for Scanned PDFs
Enable OCR in the sidebar to extract text from image-based PDFs:
- Requires Tesseract OCR to be installed
- Automatically detects if PDF is scanned
- Falls back to standard extraction if OCR fails
- Configurable DPI for better accuracy

#### AI Summarization
Generate intelligent summaries before conversion:
- **Simple**: Fast, rule-based extraction (no dependencies)
- **OpenAI**: Advanced AI (requires API key)
- **HuggingFace**: Local ML (requires PyTorch)
- Preview summary before audio conversion
- Configurable summary length

#### Batch Processing
Convert multiple PDFs simultaneously:
- Select "Batch Processing" mode
- Upload multiple PDF files
- Configure settings for all files
- Start batch conversion
- View individual file results

#### Speech-to-Text
Convert audio files to text:
- Select "Audio to Text" mode
- Upload WAV, FLAC, or AIFF audio file
- Choose STT engine (Google or Sphinx)
- Select audio language
- Click "Transcribe to Text"
- View and download transcribed text

#### Custom Page Range
To convert specific pages, select "Custom range" in the sidebar and enter pages like:
- `1-5` (pages 1 through 5)
- `1,3,5` (pages 1, 3, and 5)
- `1-3, 5, 8-10` (mixed ranges)

#### Text Editing
After previewing the extracted text, you can:
- Edit the content directly
- Remove unwanted sections
- Fix formatting issues
- Add or modify text before conversion

#### Text Cleaning
Enable text preprocessing options to:
- Remove extra whitespace and newlines
- Filter special characters
- Improve audio quality by cleaning formatting artifacts

### REST API Usage

The application includes a REST API built with FastAPI. Start the API server:

```bash
python api.py
```

#### API Endpoints

**Convert PDF to Audio**
```bash
POST /convert
Content-Type: multipart/form-data

Parameters:
- file: PDF file
- language: Language code (default: en)
- slow: Slow speech speed (default: false)
- engine: TTS engine (default: gtts)
- use_ocr: Use OCR (default: false)
- clean_text: Clean formatting (default: true)
```

**Summarize PDF**
```bash
POST /summarize
Content-Type: multipart/form-data

Parameters:
- file: PDF file
- method: Summarization method (simple, openai, huggingface)
- max_length: Maximum summary length (default: 300)
- api_key: OpenAI API key (if using openai method)
```

**Batch Convert**
```bash
POST /batch
Content-Type: multipart/form-data

Parameters:
- files: Multiple PDF files
- language: Language code
- slow: Slow speech speed
- engine: TTS engine
- use_ocr: Use OCR
- max_workers: Maximum parallel workers (default: 3)
```

**List Available Engines**
```bash
GET /engines
```

**List Available Voices**
```bash
GET /voices?engine=pyttsx3
```

**Health Check**
```bash
GET /health
```

Visit `http://localhost:8000/docs` for interactive Swagger documentation.

## 🛠️ Technology Stack

- **Streamlit**: Web framework for the user interface
- **FastAPI**: REST API framework for programmatic access
- **PyPDF2**: PDF text extraction
- **pytesseract**: OCR for scanned PDFs
- **pdf2image**: PDF to image conversion for OCR
- **gTTS**: Google Text-to-Speech for audio generation
- **pyttsx3**: Offline text-to-speech engine
- **edge-tts**: Microsoft Edge TTS for premium voices
- **OpenAI**: GPT-based AI summarization
- **HuggingFace Transformers**: Local ML-based summarization
- **Python**: Core programming language

## 📁 Project Structure

```
SelfProjects/
├── PDF2Voice.py              # Main Streamlit application
├── api.py                    # FastAPI REST API server
├── ocr_module.py             # OCR processing module
├── summarization_module.py   # AI summarization module
├── tts_engines.py            # Multiple TTS engines module
├── batch_processor.py        # Batch processing module
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## 🔧 Configuration

### Dependencies
```
streamlit>=1.28.0
PyPDF2>=3.0.0
gTTS>=2.4.0
pytesseract>=0.3.10
Pillow>=10.0.0
pdf2image>=1.16.0
openai>=1.0.0
fastapi>=0.104.0
uvicorn>=0.24.0
python-multipart>=0.0.6
edge-tts>=6.1.0
pyttsx3>=2.90
pydub>=0.25.0
transformers>=4.35.0
torch>=2.0.0
```

### Streamlit Config
You can customize Streamlit behavior by creating a `.streamlit/config.toml` file:

```toml
[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

## 🌐 Deployment

### Streamlit Cloud
1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Deploy with one click

Note: OCR and some features may require additional system dependencies on cloud platforms.

### Docker Deployment
Create a `Dockerfile` for the Streamlit app:
```dockerfile
FROM python:3.9-slim

# Install system dependencies for OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "PDF2Voice.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Create a `Dockerfile` for the API:
```dockerfile
FROM python:3.9-slim

# Install system dependencies for OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

EXPOSE 8000
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
# Build Streamlit app
docker build -t pdf2voice-streamlit -f Dockerfile .
docker run -p 8501:8501 pdf2voice-streamlit

# Build API
docker build -t pdf2voice-api -f Dockerfile.api .
docker run -p 8000:8000 pdf2voice-api
```

### Docker Compose
Use `docker-compose.yml` to run both services:
```yaml
version: '3.8'
services:
  streamlit:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - .:/app
  
  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "8000:8000"
    volumes:
      - .:/app
```

## ⚠️ Limitations

- OCR requires Tesseract OCR to be installed separately
- OpenAI summarization requires an API key
- HuggingFace summarization requires PyTorch (large download)
- Large files may take longer to process
- gTTS requires internet connection
- pyttsx3 may have limited voice options on some systems
- Batch processing uses system resources heavily

## 🐛 Troubleshooting

### Common Issues

**"Could not extract text" error**
- Ensure PDF is text-based, not scanned images
- Try enabling OCR for scanned PDFs
- Verify Tesseract OCR is installed correctly
- Try a different PDF file to test

**OCR not working**
- Ensure Tesseract OCR is installed
- Check Tesseract path in system PATH
- Verify pdf2image and Poppler are installed
- Try with a simple text-based PDF first

**OpenAI summarization fails**
- Verify your API key is correct
- Check your OpenAI account has credits
- Ensure you have internet connection
- Try the simple summarization method instead

**HuggingFace summarization fails**
- Ensure PyTorch is installed correctly
- Check if you have enough disk space (models are large)
- Try with a smaller text sample
- Fall back to simple summarization

**Slow conversion**
- Large PDFs take longer to process
- Consider splitting large files into smaller sections
- Reduce batch size for batch processing
- Use pyttsx3 for offline conversion (faster for some cases)

**Audio not playing**
- Check browser compatibility
- Ensure MP3 format is supported
- Try downloading the file instead
- Verify audio file was generated successfully

**Language not working**
- Verify language code is correct
- Check if language is supported by selected TTS engine
- gTTS supports most languages
- pyttsx3 may have limited language support

**pyttsx3 not working**
- Ensure system audio drivers are installed
- Check if pyttsx3 is compatible with your OS
- Try gTTS as an alternative
- Verify audio output device is available

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io) for the amazing web framework
- [FastAPI](https://fastapi.tiangolo.com) for the modern REST API framework
- [PyPDF2](https://github.com/py-pdf/PyPDF2) for PDF processing
- [gTTS](https://github.com/pndurette/gTTS) for text-to-speech conversion
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for OCR capabilities
- [OpenAI](https://openai.com) for GPT-based summarization
- [HuggingFace](https://huggingface.co) for transformers library

## 📧 Contact

For questions, suggestions, or issues, please open an issue on the repository.

---

**Made with ❤️ using Streamlit**

Convert your documents to audio and listen on the go! 🎧
