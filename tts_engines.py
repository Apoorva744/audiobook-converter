"""
Multiple TTS Engines Module
Supports gTTS, edge-tts, and pyttsx3
"""
import os
import tempfile
from typing import Optional
import asyncio


class TTSEngine:
    """Base class for TTS engines"""
    
    def text_to_speech(self, text: str, output_path: str, **kwargs) -> bool:
        """Convert text to speech"""
        raise NotImplementedError


class GTTSEngine(TTSEngine):
    """Google Text-to-Speech engine"""
    
    def __init__(self):
        try:
            from gtts import gTTS
            self.gTTS = gTTS
        except ImportError:
            raise ImportError("gTTS library is required. Install with: pip install gTTS")
    
    def text_to_speech(self, text: str, output_path: str, 
                      language: str = 'en', slow: bool = False, **kwargs) -> bool:
        """Convert text to speech using gTTS"""
        try:
            tts = self.gTTS(text=text, lang=language, slow=slow)
            tts.save(output_path)
            return True
        except Exception as e:
            raise Exception(f"gTTS conversion failed: {str(e)}")


class EdgeTTSEngine(TTSEngine):
    """Microsoft Edge TTS engine (higher quality, more voices)"""
    
    def __init__(self):
        try:
            import edge_tts
            self.edge_tts = edge_tts
        except ImportError:
            raise ImportError("edge-tts library is required. Install with: pip install edge-tts")
    
    async def _convert_async(self, text: str, output_path: str, voice: str = None):
        """Async conversion for edge-tts"""
        communicate = self.edge_tts.Communicate(text, voice or "en-US-AriaNeural")
        await communicate.save(output_path)
    
    def text_to_speech(self, text: str, output_path: str, 
                      voice: str = None, **kwargs) -> bool:
        """Convert text to speech using edge-tts"""
        try:
            asyncio.run(self._convert_async(text, output_path, voice))
            return True
        except Exception as e:
            raise Exception(f"Edge TTS conversion failed: {str(e)}")
    
    def get_available_voices(self):
        """Get list of available voices"""
        try:
            voices = asyncio.run(self.edge_tts.list_voices())
            return voices
        except:
            return []


class Pyttsx3Engine(TTSEngine):
    """Offline TTS engine using pyttsx3"""
    
    def __init__(self):
        try:
            import pyttsx3
            self.pyttsx3 = pyttsx3
        except ImportError:
            raise ImportError("pyttsx3 library is required. Install with: pip install pyttsx3")
    
    def text_to_speech(self, text: str, output_path: str, 
                      voice_id: str = None, rate: int = 150, volume: float = 1.0, **kwargs) -> bool:
        """Convert text to speech using pyttsx3"""
        try:
            engine = self.pyttsx3.init()
            
            # Set properties
            if voice_id:
                voices = engine.getProperty('voices')
                for voice in voices:
                    if voice_id in voice.id:
                        engine.setProperty('voice', voice.id)
                        break
            
            engine.setProperty('rate', rate)
            engine.setProperty('volume', volume)
            
            # Save to file
            engine.save_to_file(text, output_path)
            engine.runAndWait()
            
            return True
        except Exception as e:
            raise Exception(f"pyttsx3 conversion failed: {str(e)}")
    
    def get_available_voices(self):
        """Get list of available voices"""
        try:
            engine = self.pyttsx3.init()
            voices = engine.getProperty('voices')
            return [(v.id, v.name) for v in voices]
        except:
            return []


class TTSEngineManager:
    """Manager for multiple TTS engines"""
    
    def __init__(self):
        self.engines = {
            'gtts': GTTSEngine(),
            'edge': EdgeTTSEngine(),
            'pyttsx3': Pyttsx3Engine()
        }
        self.default_engine = 'gtts'
    
    def get_engine(self, engine_name: str) -> TTSEngine:
        """Get specific TTS engine"""
        if engine_name not in self.engines:
            raise ValueError(f"Unknown engine: {engine_name}. Available: {list(self.engines.keys())}")
        return self.engines[engine_name]
    
    def convert(self, text: str, output_path: str, engine: str = None, **kwargs) -> bool:
        """Convert text using specified engine"""
        engine_name = engine or self.default_engine
        tts_engine = self.get_engine(engine_name)
        return tts_engine.text_to_speech(text, output_path, **kwargs)
    
    def list_engines(self):
        """List available engines"""
        return list(self.engines.keys())


def get_tts_manager():
    """Factory function to get TTS manager"""
    return TTSEngineManager()
