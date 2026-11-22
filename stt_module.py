"""
Speech-to-Text Module for transcribing audio files
Supports multiple STT engines
"""
import speech_recognition as sr
import tempfile
import os


class STTEngine:
    """Base class for Speech-to-Text engines"""
    
    def transcribe(self, audio_file_path: str, **kwargs) -> str:
        """Transcribe audio to text"""
        raise NotImplementedError


class GoogleSTTEngine(STTEngine):
    """Google Speech Recognition engine (online)"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
    
    def transcribe(self, audio_file_path: str, language: str = "en-US", **kwargs) -> str:
        """Transcribe audio using Google Speech Recognition"""
        try:
            with sr.AudioFile(audio_file_path) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data, language=language)
                return text
        except sr.UnknownValueError:
            return "Could not understand the audio"
        except sr.RequestError as e:
            raise Exception(f"Google Speech Recognition service error: {str(e)}")
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")


class SphinxSTTEngine(STTEngine):
    """CMU Sphinx engine (offline)"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
    
    def transcribe(self, audio_file_path: str, language: str = "en-US", **kwargs) -> str:
        """Transcribe audio using CMU Sphinx (offline)"""
        try:
            with sr.AudioFile(audio_file_path) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_sphinx(audio_data)
                return text
        except sr.UnknownValueError:
            return "Could not understand the audio"
        except sr.RequestError as e:
            raise Exception(f"Sphinx recognition error: {str(e)}")
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")


class WhisperSTTEngine(STTEngine):
    """OpenAI Whisper engine (high accuracy)"""
    
    def __init__(self):
        try:
            import whisper
            self.whisper = whisper
            self.model = None
        except ImportError:
            raise ImportError("Whisper not installed. Install with: pip install openai-whisper")
    
    def load_model(self, model_size: str = "base"):
        """Load Whisper model"""
        if self.model is None:
            self.model = self.whisper.load_model(model_size)
    
    def transcribe(self, audio_file_path: str, model_size: str = "base", **kwargs) -> str:
        """Transcribe audio using Whisper"""
        try:
            self.load_model(model_size)
            result = self.model.transcribe(audio_file_path)
            return result["text"]
        except Exception as e:
            raise Exception(f"Whisper transcription failed: {str(e)}")


class STTEngineManager:
    """Manager for multiple STT engines"""
    
    def __init__(self):
        self.engines = {
            'google': GoogleSTTEngine(),
            'sphinx': SphinxSTTEngine(),
            'whisper': WhisperSTTEngine()
        }
        self.default_engine = 'google'
    
    def get_engine(self, engine_name: str) -> STTEngine:
        """Get specific STT engine"""
        if engine_name not in self.engines:
            raise ValueError(f"Unknown engine: {engine_name}. Available: {list(self.engines.keys())}")
        return self.engines[engine_name]
    
    def transcribe(self, audio_file_path: str, engine: str = None, **kwargs) -> str:
        """Transcribe audio using specified engine"""
        engine_name = engine or self.default_engine
        stt_engine = self.get_engine(engine_name)
        return stt_engine.transcribe(audio_file_path, **kwargs)
    
    def list_engines(self):
        """List available engines"""
        return list(self.engines.keys())


def get_stt_manager():
    """Factory function to get STT manager"""
    return STTEngineManager()
