"""
REST API for PDF to Audiobook Converter
Built with FastAPI
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import os
import tempfile
import uuid
from datetime import datetime

# Import our modules
from tts_engines import get_tts_manager
from ocr_module import get_ocr_processor
from summarization_module import get_summarizer
from batch_processor import get_audio_batch_processor
from stt_module import get_stt_manager

app = FastAPI(
    title="PDF to Audiobook API",
    description="Convert PDFs to audio with OCR, AI summarization, multiple TTS engines, and Speech-to-Text",
    version="2.0.0"
)

# Global managers
tts_manager = get_tts_manager()
ocr_processor = get_ocr_processor()


class ConversionRequest(BaseModel):
    """Request model for PDF conversion"""
    language: str = "en"
    slow: bool = False
    engine: str = "gtts"
    use_ocr: bool = False
    clean_text: bool = True


class SummarizationRequest(BaseModel):
    """Request model for text summarization"""
    method: str = "simple"
    max_length: int = 300
    api_key: Optional[str] = None


class BatchConversionRequest(BaseModel):
    """Request model for batch conversion"""
    language: str = "en"
    slow: bool = False
    engine: str = "gtts"
    use_ocr: bool = False
    max_workers: int = 3


class TranscriptionRequest(BaseModel):
    """Request model for audio transcription"""
    engine: str = "google"
    language: str = "en-US"


# Temporary storage for files
TEMP_DIR = tempfile.gettempdir()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "PDF to Audiobook API",
        "version": "2.0.0",
        "endpoints": {
            "convert": "/convert",
            "summarize": "/summarize",
            "batch": "/batch",
            "transcribe": "/transcribe",
            "engines": "/engines",
            "voices": "/voices"
        }
    }


@app.get("/engines")
async def list_engines():
    """List available TTS engines"""
    return {
        "engines": tts_manager.list_engines(),
        "default": tts_manager.default_engine
    }


@app.get("/voices")
async def list_voices(engine: str = "pyttsx3"):
    """List available voices for an engine"""
    try:
        tts_engine = tts_manager.get_engine(engine)
        if hasattr(tts_engine, 'get_available_voices'):
            voices = tts_engine.get_available_voices()
            return {"engine": engine, "voices": voices}
        else:
            return {"engine": engine, "voices": "Voice listing not supported for this engine"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/convert")
async def convert_pdf(
    file: UploadFile = File(...),
    language: str = "en",
    slow: bool = False,
    engine: str = "gtts",
    use_ocr: bool = False,
    clean_text: bool = True
):
    """
    Convert a PDF file to audio
    
    Args:
        file: PDF file to convert
        language: Language code (en, es, fr, etc.)
        slow: Slow speech speed
        engine: TTS engine (gtts, edge, pyttsx3)
        use_ocr: Use OCR for scanned PDFs
        clean_text: Clean text formatting
    
    Returns:
        Audio file and conversion stats
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Save uploaded file temporarily
        temp_pdf_path = os.path.join(TEMP_DIR, f"{uuid.uuid4()}.pdf")
        with open(temp_pdf_path, "wb") as f:
            f.write(await file.read())
        
        # Extract text
        from PyPDF2 import PdfReader
        
        if use_ocr:
            ocr_processor.configure_tesseract()
            with open(temp_pdf_path, 'rb') as f:
                text = ocr_processor.extract_text_from_pdf_images(f)
        else:
            pdf_reader = PdfReader(temp_pdf_path)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + " "
        
        # Clean text if requested
        if clean_text:
            import re
            text = re.sub(r'\s+', ' ', text)
            text = re.sub(r'\n+', ' ', text)
        
        # Check if text was extracted
        if not text.strip():
            os.unlink(temp_pdf_path)
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
        
        # Generate output path
        output_filename = f"{uuid.uuid4()}.mp3"
        output_path = os.path.join(TEMP_DIR, output_filename)
        
        # Convert to audio
        tts_manager.convert(text, output_path, engine=engine, language=language, slow=slow)
        
        # Calculate stats
        word_count = len(text.split())
        char_count = len(text)
        duration = word_count / 150  # Approximate duration in minutes
        
        # Clean up PDF file
        os.unlink(temp_pdf_path)
        
        # Return audio file
        return FileResponse(
            output_path,
            media_type="audio/mpeg",
            filename=f"{os.path.splitext(file.filename)[0]}.mp3",
            headers={
                "X-Word-Count": str(word_count),
                "X-Char-Count": str(char_count),
                "X-Duration": f"{duration:.2f}"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


@app.post("/summarize")
async def summarize_pdf(
    file: UploadFile = File(...),
    method: str = "simple",
    max_length: int = 300,
    api_key: Optional[str] = None
):
    """
    Summarize a PDF file
    
    Args:
        file: PDF file to summarize
        method: Summarization method (simple, openai, huggingface)
        max_length: Maximum summary length in words
        api_key: API key for OpenAI (if using openai method)
    
    Returns:
        Summary text
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Save uploaded file temporarily
        temp_pdf_path = os.path.join(TEMP_DIR, f"{uuid.uuid4()}.pdf")
        with open(temp_pdf_path, "wb") as f:
            f.write(await file.read())
        
        # Extract text
        from PyPDF2 import PdfReader
        pdf_reader = PdfReader(temp_pdf_path)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + " "
        
        # Clean up
        os.unlink(temp_pdf_path)
        
        # Check if text was extracted
        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
        
        # Summarize
        summarizer = get_summarizer(method=method, api_key=api_key)
        summary = summarizer.summarize(text, max_length=max_length)
        
        return {
            "summary": summary,
            "original_length": len(text.split()),
            "summary_length": len(summary.split()),
            "method": method
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")


@app.post("/batch")
async def batch_convert(
    files: List[UploadFile] = File(...),
    language: str = "en",
    slow: bool = False,
    engine: str = "gtts",
    use_ocr: bool = False,
    max_workers: int = 3,
    background_tasks: BackgroundTasks = None
):
    """
    Convert multiple PDFs to audio in batch
    
    Args:
        files: List of PDF files to convert
        language: Language code
        slow: Slow speech speed
        engine: TTS engine
        use_ocr: Use OCR for scanned PDFs
        max_workers: Maximum parallel workers
    
    Returns:
        Batch conversion results
    """
    try:
        # Save files temporarily
        temp_files = []
        for file in files:
            if not file.filename.endswith('.pdf'):
                continue
            temp_path = os.path.join(TEMP_DIR, f"{uuid.uuid4()}.pdf")
            with open(temp_path, "wb") as f:
                f.write(await file.read())
            temp_files.append(temp_path)
        
        # Process batch
        batch_processor = get_audio_batch_processor(
            output_dir=TEMP_DIR,
            max_workers=max_workers
        )
        
        results = batch_processor.process_batch(
            temp_files,
            batch_processor.process_pdf_to_audio,
            tts_engine=tts_manager.get_engine(engine),
            language=language,
            slow=slow,
            use_ocr=use_ocr
        )
        
        # Clean up temp PDF files
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        
        # Get summary
        summary = batch_processor.get_summary()
        
        return {
            "results": results,
            "summary": summary
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch conversion failed: {str(e)}")


@app.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    engine: str = "google",
    language: str = "en-US"
):
    """
    Transcribe audio file to text
    
    Args:
        file: Audio file to transcribe (WAV, FLAC, AIFF)
        engine: STT engine (google, sphinx)
        language: Language code (en-US, es-ES, etc.)
    
    Returns:
        Transcribed text
    """
    try:
        # Validate file type
        allowed_extensions = ['wav', 'flac', 'aiff', 'aiffc']
        file_ext = file.filename.split('.')[-1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"Only {', '.join(allowed_extensions)} files are supported")
        
        # Save uploaded file temporarily
        temp_audio_path = os.path.join(TEMP_DIR, f"{uuid.uuid4()}.{file_ext}")
        with open(temp_audio_path, "wb") as f:
            f.write(await file.read())
        
        # Transcribe
        stt_manager = get_stt_manager()
        transcribed_text = stt_manager.transcribe(
            temp_audio_path,
            engine=engine,
            language=language
        )
        
        # Clean up
        os.unlink(temp_audio_path)
        
        # Calculate stats
        word_count = len(transcribed_text.split())
        char_count = len(transcribed_text)
        
        return {
            "text": transcribed_text,
            "word_count": word_count,
            "char_count": char_count,
            "engine": engine,
            "language": language
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
