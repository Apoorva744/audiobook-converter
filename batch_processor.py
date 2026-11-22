"""
Batch Processing Module for converting multiple PDFs simultaneously
"""
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Callable
from datetime import datetime
import tempfile


class BatchProcessor:
    """Handles batch processing of multiple PDFs"""
    
    def __init__(self, max_workers: int = 3):
        self.max_workers = max_workers
        self.results = []
    
    def process_single_pdf(self, pdf_file: str, process_func: Callable, **kwargs) -> Dict:
        """Process a single PDF file"""
        try:
            start_time = datetime.now()
            
            # Call the processing function
            result = process_func(pdf_file, **kwargs)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return {
                'file': os.path.basename(pdf_file),
                'status': 'success',
                'result': result,
                'duration': duration,
                'timestamp': end_time.isoformat()
            }
        
        except Exception as e:
            return {
                'file': os.path.basename(pdf_file),
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def process_batch(self, pdf_files: List[str], process_func: Callable, 
                     progress_callback: Callable = None, **kwargs) -> List[Dict]:
        """
        Process multiple PDFs in parallel
        
        Args:
            pdf_files: List of PDF file paths
            process_func: Function to process each PDF
            progress_callback: Optional callback for progress updates
            **kwargs: Additional arguments for process_func
        
        Returns:
            List of processing results
        """
        self.results = []
        completed = 0
        total = len(pdf_files)
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(self.process_single_pdf, pdf_file, process_func, **kwargs): pdf_file
                for pdf_file in pdf_files
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_file):
                result = future.result()
                self.results.append(result)
                completed += 1
                
                # Call progress callback if provided
                if progress_callback:
                    progress_callback(completed, total, result)
        
        return self.results
    
    def get_summary(self) -> Dict:
        """Get summary of batch processing results"""
        if not self.results:
            return {}
        
        successful = [r for r in self.results if r['status'] == 'success']
        failed = [r for r in self.results if r['status'] == 'error']
        
        total_duration = sum(r.get('duration', 0) for r in successful)
        
        return {
            'total': len(self.results),
            'successful': len(successful),
            'failed': len(failed),
            'total_duration': total_duration,
            'average_duration': total_duration / len(successful) if successful else 0,
            'failed_files': [r['file'] for r in failed]
        }


class AudioBatchProcessor(BatchProcessor):
    """Specialized batch processor for audio conversion"""
    
    def __init__(self, output_dir: str = None, max_workers: int = 3):
        super().__init__(max_workers)
        self.output_dir = output_dir or tempfile.gettempdir()
    
    def process_pdf_to_audio(self, pdf_file: str, tts_engine, 
                            language: str = 'en', slow: bool = False,
                            use_ocr: bool = False, **kwargs) -> Dict:
        """Process PDF to audio conversion"""
        try:
            from PyPDF2 import PdfReader
            from ocr_module import get_ocr_processor
            
            # Extract text
            if use_ocr:
                ocr = get_ocr_processor()
                with open(pdf_file, 'rb') as f:
                    text = ocr.extract_text_from_pdf_images(f)
            else:
                pdf_reader = PdfReader(pdf_file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + " "
            
            # Generate output filename
            base_name = os.path.splitext(os.path.basename(pdf_file))[0]
            output_path = os.path.join(self.output_dir, f"{base_name}_audio.mp3")
            
            # Convert to audio
            tts_engine.text_to_speech(text, output_path, language=language, slow=slow)
            
            return {
                'output_file': output_path,
                'text_length': len(text),
                'word_count': len(text.split())
            }
        
        except Exception as e:
            raise Exception(f"Audio conversion failed: {str(e)}")


def get_batch_processor(max_workers: int = 3):
    """Factory function to get batch processor"""
    return BatchProcessor(max_workers=max_workers)


def get_audio_batch_processor(output_dir: str = None, max_workers: int = 3):
    """Factory function to get audio batch processor"""
    return AudioBatchProcessor(output_dir=output_dir, max_workers=max_workers)
