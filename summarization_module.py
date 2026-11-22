"""
AI-powered PDF Summarization Module
Supports OpenAI GPT and HuggingFace transformers
"""
import os
from typing import Optional
import openai


class Summarizer:
    """Base class for text summarization"""
    
    def summarize(self, text: str, max_length: int = 300) -> str:
        """Summarize text"""
        raise NotImplementedError


class OpenAISummarizer(Summarizer):
    """Summarizer using OpenAI GPT models"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        openai.api_key = self.api_key
    
    def summarize(self, text: str, max_length: int = 300) -> str:
        """Summarize text using OpenAI"""
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a helpful assistant that summarizes text concisely. "
                                  f"Provide a summary in approximately {max_length} words."
                    },
                    {
                        "role": "user",
                        "content": f"Please summarize the following text:\n\n{text}"
                    }
                ],
                max_tokens=max_length * 2,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI summarization failed: {str(e)}")


class HuggingFaceSummarizer(Summarizer):
    """Summarizer using HuggingFace transformers"""
    
    def __init__(self, model_name: str = "facebook/bart-large-cnn"):
        try:
            from transformers import pipeline
            self.summarizer = pipeline("summarization", model=model_name)
        except ImportError:
            raise ImportError("transformers library is required. Install with: pip install transformers torch")
    
    def summarize(self, text: str, max_length: int = 300) -> str:
        """Summarize text using HuggingFace"""
        try:
            # Truncate text if too long (model limit is typically 1024 tokens)
            max_input_length = 3000
            if len(text) > max_input_length:
                text = text[:max_input_length]
            
            result = self.summarizer(
                text,
                max_length=max_length,
                min_length=50,
                do_sample=False
            )
            return result[0]['summary_text']
        except Exception as e:
            raise Exception(f"HuggingFace summarization failed: {str(e)}")


class SimpleSummarizer(Summarizer):
    """Simple extractive summarizer (no AI required)"""
    
    def summarize(self, text: str, max_length: int = 300) -> str:
        """Simple extractive summarization"""
        sentences = text.split('.')
        
        # Score sentences by length and position
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            if len(sentence.strip()) > 20:  # Ignore very short sentences
                score = len(sentence.split()) * (1 - i / len(sentences))
                scored_sentences.append((sentence.strip(), score))
        
        # Sort by score and take top sentences
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        
        summary = '. '.join([s[0] for s in scored_sentences[:5]])
        
        # Truncate to max length
        words = summary.split()
        if len(words) > max_length:
            summary = ' '.join(words[:max_length])
        
        return summary


def get_summarizer(method: str = "simple", **kwargs):
    """Factory function to get summarizer"""
    if method == "openai":
        return OpenAISummarizer(**kwargs)
    elif method == "huggingface":
        return HuggingFaceSummarizer(**kwargs)
    elif method == "simple":
        return SimpleSummarizer()
    else:
        raise ValueError(f"Unknown summarizer method: {method}")
