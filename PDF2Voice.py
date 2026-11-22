import streamlit as st
from PyPDF2 import PdfReader
from gtts import gTTS
import os
import datetime
import re
from io import BytesIO
import sys

# Set up the page configuration (this must be the first Streamlit command)
st.set_page_config(
    page_title="Audiobook Converter",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem !important;
        font-weight: 700 !important;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
    }
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .stat-box {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
    }
    .dark-mode .stat-box {
        background: #262730;
    }
    .upload-box {
        border: 2px dashed #667eea;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
    }
    .success-message {
        background: #d4edda;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
    }
    .dark-mode .success-message {
        background: #1e4620;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'conversion_history' not in st.session_state:
    st.session_state.conversion_history = []
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = ""
if 'pdf_info' not in st.session_state:
    st.session_state.pdf_info = None
if 'batch_files' not in st.session_state:
    st.session_state.batch_files = []
if 'summary' not in st.session_state:
    st.session_state.summary = ""

# Hero section
st.markdown('<h1 class="main-header">🎧 Audiobook Converter</h1>', unsafe_allow_html=True)
st.markdown("### Convert text to audio or audio to text instantly!")
st.markdown("---")

# Feature cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("""
    <div class="feature-card">
        <h3>🌍 Multi-Language</h3>
        <p>13+ languages</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="feature-card">
        <h3>🔍 OCR Support</h3>
        <p>Scanned PDFs</p>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div class="feature-card">
        <h3>🤖 AI Summary</h3>
        <p>Smart summaries</p>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown("""
    <div class="feature-card">
        <h3>� Batch Process</h3>
        <p>Multiple files</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Dark mode toggle in sidebar
st.sidebar.header("🎨 Appearance")
dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=False)

if dark_mode:
    st.markdown('<style>.stApp { background-color: #1e1e1e; color: #ffffff; } .dark-mode { color: #ffffff; }</style>', unsafe_allow_html=True)

# Initialize default values (will be overridden based on conversion type)
language = "en"
tts_engine = "gTTS"
slow_speed = False
clean_text = True
remove_special_chars = False
use_ocr = False
enable_summary = False
summary_method = "simple"
api_key = None
page_range_option = "All pages"
custom_page_range = ""

# Check if advanced features are available (for local deployment)
HAS_OCR = False
HAS_STT = False
HAS_AI = False

try:
    import pytesseract
    import pdf2image
    HAS_OCR = True
except:
    pass

try:
    import speech_recognition
    HAS_STT = True
except:
    pass

try:
    import transformers
    HAS_AI = True
except:
    pass

# Main content area
st.header("🎯 What would you like to do?")

# Main conversion type selection
conversion_options = ["📝 Convert Text to Audio"]
if HAS_STT:
    conversion_options.append("🎤 Convert Audio to Text")

conversion_type = st.radio(
    "Select conversion type",
    options=conversion_options,
    horizontal=True,
    label_visibility="collapsed"
)

if conversion_type == "📝 Convert Text to Audio":
    st.header("📤 Upload Your Document")
    
    # Text to Audio specific settings in sidebar
    st.sidebar.header("⚙️ Audio Settings")
    
    language = st.sidebar.selectbox(
        "🌍 Select Language",
        options=["en", "es", "fr", "de", "hi", "ja", "it", "pt", "ru", "zh-CN", "ko", "nl", "ar"],
        format_func=lambda x: {
            "en": "English",
            "es": "Spanish", 
            "fr": "French",
            "de": "German",
            "hi": "Hindi",
            "ja": "Japanese",
            "it": "Italian",
            "pt": "Portuguese",
            "ru": "Russian",
            "zh-CN": "Chinese (Simplified)",
            "ko": "Korean",
            "nl": "Dutch",
            "ar": "Arabic"
        }[x]
    )
    
    # TTS Engine Selection
    st.sidebar.subheader("🎤 Voice Engine")
    tts_engine = st.sidebar.selectbox(
        "Select Engine",
        options=["gTTS", "pyttsx3"],
        format_func=lambda x: {
            "gTTS": "Google TTS (Online)",
            "pyttsx3": "Offline TTS"
        }[x]
    )
    
    slow_speed = st.sidebar.checkbox("🐢 Slow speech speed", value=False)
    
    # Text preprocessing options
    st.sidebar.header("📝 Text Processing")
    clean_text = st.sidebar.checkbox("Clean formatting (remove extra spaces/newlines)", value=True)
    remove_special_chars = st.sidebar.checkbox("Remove special characters", value=False)
    
    # OCR option (only show if available)
    if HAS_OCR:
        st.sidebar.header("🔍 Scanned PDF Support")
        use_ocr = st.sidebar.checkbox(
            "Enable for scanned/image-based PDFs",
            value=False,
            help="Turn this on if your PDF is a scanned document or image. Requires additional software."
        )
    
    # Summarization option (only show if available)
    if HAS_AI:
        st.sidebar.header("📝 Quick Summary")
        enable_summary = st.sidebar.checkbox(
            "Generate a quick summary",
            value=False,
            help="Get a short summary of your document before converting to audio"
        )
        summary_method = st.sidebar.selectbox(
            "Summary Type",
            options=["simple", "openai", "huggingface"],
            format_func=lambda x: {
                "simple": "Fast & Simple (Recommended)",
                "openai": "AI-Powered (Requires API Key)",
                "huggingface": "Advanced AI (Large Download)"
            }[x],
            help="Choose how you want the summary to be generated"
        )
        if summary_method == "openai":
            api_key = st.sidebar.text_input("OpenAI API Key", type="password", help="Required for AI-powered summary")
    
    # Page range selection
    st.sidebar.header("📄 Page Selection")
    page_range_option = st.sidebar.radio(
        "Select pages to convert",
        options=["All pages", "Custom range"],
        label_visibility="visible"
    )
    
    custom_page_range = ""
    if page_range_option == "Custom range":
        custom_page_range = st.sidebar.text_input(
            "Enter page range (e.g., 1-5, 8, 10-12)",
            placeholder="1-5, 8, 10-12",
            help="Use commas to separate pages/ranges"
        )
    
    # File uploader widget
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload a PDF document to convert to audio"
    )

elif conversion_type == "🎤 Convert Audio to Text":
    st.header("🎤 Upload Your Audio")
    st.info("Convert audio files to text using speech recognition")
    st.warning("⚠️ This feature requires additional dependencies. Please run the app locally to use Speech-to-Text.")
    
    # Audio file uploader
    audio_file = st.file_uploader(
        "Choose an audio file",
        type=['wav', 'flac', 'aiff', 'aiffc'],
        help="Upload WAV, FLAC, or AIFF audio files",
        disabled=True
    )

def preprocess_text(text, clean=True, remove_special=False):
    """
    Preprocess text before conversion.
    """
    if clean:
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', ' ', text)
    
    if remove_special:
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^a-zA-Z0-9\s.,!?;:()-]', '', text)
    
    return text.strip()


def extract_text_with_ocr(pdf_file, use_ocr=False):
    """Extract text from PDF with optional OCR support"""
    if use_ocr:
        try:
            from ocr_module import get_ocr_processor
            ocr = get_ocr_processor()
            ocr.configure_tesseract()
            return ocr.extract_text_from_pdf_images(pdf_file)
        except Exception as e:
            st.error(f"OCR failed: {str(e)}. Falling back to standard extraction.")
    
    # Standard text extraction
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + " "
    return text


def generate_summary(text, method="simple", api_key=None):
    """Generate summary using selected method"""
    try:
        from summarization_module import get_summarizer
        summarizer = get_summarizer(method=method, api_key=api_key)
        return summarizer.summarize(text, max_length=300)
    except Exception as e:
        st.warning(f"Summarization failed: {str(e)}")
        return None

def parse_page_range(range_str, total_pages):
    """
    Parse page range string into list of page indices.
    """
    pages = []
    try:
        parts = range_str.split(',')
        for part in parts:
            part = part.strip()
            if '-' in part:
                start, end = map(int, part.split('-'))
                pages.extend(range(start - 1, min(end, total_pages)))
            else:
                page_num = int(part) - 1
                if 0 <= page_num < total_pages:
                    pages.append(page_num)
    except:
        return list(range(total_pages))
    return sorted(list(set(pages)))

def pdf_to_audiobook(pdf_file, output_path, language='en', slow=False, 
                     page_range=None, clean=True, remove_special=False,
                     use_ocr=False, tts_engine='gtts', enable_summary=False,
                     summary_method='simple', api_key=None):
    """
    Converts uploaded PDF file into an audiobook.
    Returns: (success: bool, message: str, stats: dict, summary: str)
    """
    try:
        # Extract text with optional OCR
        text = extract_text_with_ocr(pdf_file, use_ocr=use_ocr)
        
        # Preprocess text
        text = preprocess_text(text, clean=clean, remove_special=remove_special)
        
        # Check if text was extracted
        if not text.strip():
            return False, "Could not extract text. The PDF might be image-based or empty.", {}, None
        
        # Generate summary if requested
        summary = None
        if enable_summary:
            summary = generate_summary(text, method=summary_method, api_key=api_key)
        
        # Calculate statistics
        word_count = len(text.split())
        char_count = len(text)
        estimated_duration = word_count / 150  # Average reading speed: 150 words/minute
        
        # Convert text to speech using selected engine
        if tts_engine == 'pyttsx3':
            try:
                from tts_engines import get_tts_manager
                tts_manager = get_tts_manager()
                tts_manager.convert(text, output_path, engine='pyttsx3', language=language, slow=slow)
            except Exception as e:
                # Fallback to gTTS if pyttsx3 fails
                st.warning(f"pyttsx3 failed: {str(e)}. Using gTTS instead.")
                tts = gTTS(text=text, lang=language, slow=slow)
                tts.save(output_path)
        else:
            # Use gTTS
            tts = gTTS(text=text, lang=language, slow=slow)
            tts.save(output_path)
        
        stats = {
            'word_count': word_count,
            'char_count': char_count,
            'duration': estimated_duration,
            'pages_processed': 'All' if not page_range else 'Custom'
        }
        
        return True, "Conversion successful!", stats, summary
        
    except Exception as e:
        return False, f"An error occurred: {str(e)}", {}, None

# Process the uploaded file
if conversion_type == "📝 Convert Text to Audio" and uploaded_file is not None:
    # Display file details
    st.success(f"✅ File uploaded: {uploaded_file.name}")
    
    # Get PDF info
    pdf_reader = PdfReader(uploaded_file)
    total_pages = len(pdf_reader.pages)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📄 File Size", f"{uploaded_file.size / 1024:.2f} KB")
    with col2:
        st.metric("📑 Total Pages", total_pages)
    with col3:
        st.metric("📊 Status", "Ready to convert")
    
    # Extract text preview button
    if st.button("👁️ Preview Extracted Text", type="secondary"):
        with st.spinner("Extracting text for preview..."):
            text = extract_text_with_ocr(uploaded_file, use_ocr=use_ocr)
            text = preprocess_text(text, clean=clean_text, remove_special=remove_special_chars)
            st.session_state.extracted_text = text
            st.session_state.pdf_info = {'name': uploaded_file.name, 'pages': total_pages}
    
    # Show text preview if available
    if st.session_state.extracted_text:
        st.subheader("📝 Extracted Text Preview")
        edited_text = st.text_area(
            "Edit the text before conversion (optional):",
            value=st.session_state.extracted_text,
            height=300,
            key="text_editor"
        )
        st.session_state.extracted_text = edited_text
        
        # Quick stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📝 Words", len(edited_text.split()))
        with col2:
            st.metric("🔤 Characters", len(edited_text))
        with col3:
            est_duration = len(edited_text.split()) / 150
            st.metric("⏱️ Est. Duration", f"{est_duration:.1f} min")
    
    # Add a convert button
    st.markdown("---")
    col_left, col_right = st.columns([2, 1])
    with col_left:
        convert_button = st.button("🎵 Convert to Audio", type="primary", use_container_width=True)
    
    if convert_button:
        with st.spinner("Processing your PDF..."):
            # Create output filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"audiobook_{timestamp}.mp3"
            
            # Determine page range
            page_range = custom_page_range if page_range_option == "Custom range" else None
            
            # Get API key if using OpenAI
            openai_key = api_key if summary_method == "openai" else None
            
            # Use edited text if available, otherwise extract from PDF
            if st.session_state.extracted_text:
                # Convert edited text directly
                text_to_convert = st.session_state.extracted_text
                
                # Generate summary if requested
                summary = None
                if enable_summary:
                    summary = generate_summary(text_to_convert, method=summary_method, api_key=openai_key)
                
                try:
                    if tts_engine == 'pyttsx3':
                        from tts_engines import get_tts_manager
                        tts_manager = get_tts_manager()
                        tts_manager.convert(text_to_convert, output_filename, engine='pyttsx3', language=language, slow=slow_speed)
                    else:
                        tts = gTTS(text=text_to_convert, lang=language, slow=slow_speed)
                        tts.save(output_filename)
                    
                    word_count = len(text_to_convert.split())
                    char_count = len(text_to_convert)
                    estimated_duration = word_count / 150
                    
                    stats = {
                        'word_count': word_count,
                        'char_count': char_count,
                        'duration': estimated_duration,
                        'pages_processed': 'Custom text'
                    }
                    success = True
                    message = "Conversion successful!"
                except Exception as e:
                    success = False
                    message = f"An error occurred: {str(e)}"
                    stats = {}
                    summary = None
            else:
                # Convert from PDF
                success, message, stats, summary = pdf_to_audiobook(
                    uploaded_file, 
                    output_filename,
                    language=language,
                    slow=slow_speed,
                    page_range=page_range,
                    clean=clean_text,
                    remove_special=remove_special_chars,
                    use_ocr=use_ocr,
                    tts_engine=tts_engine,
                    enable_summary=enable_summary,
                    summary_method=summary_method,
                    api_key=openai_key
                )
            
            if success:
                st.markdown(f'<div class="success-message">✅ {message}</div>', unsafe_allow_html=True)
                
                # Show summary if generated
                if summary:
                    st.subheader("🤖 AI Summary")
                    st.info(summary)
                
                # Show statistics dashboard
                st.subheader("📊 Conversion Statistics")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📝 Words", f"{stats['word_count']:,}")
                with col2:
                    st.metric("🔤 Characters", f"{stats['char_count']:,}")
                with col3:
                    st.metric("⏱️ Duration", f"{stats['duration']:.1f} min")
                with col4:
                    st.metric("📄 Pages", stats['pages_processed'])
                
                # Read the audio file for playback and download
                with open(output_filename, 'rb') as audio_file:
                    audio_bytes = audio_file.read()
                
                # Audio player
                st.subheader("🎧 Audio Player")
                st.audio(audio_bytes, format='audio/mp3')
                
                # Download button
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="⬇️ Download MP3",
                        data=audio_bytes,
                        file_name=output_filename,
                        mime="audio/mp3",
                        use_container_width=True
                    )
                with col2:
                    if st.button("🔄 Convert Again", use_container_width=True):
                        st.session_state.extracted_text = ""
                        st.rerun()
                
                # Add to history
                history_entry = {
                    'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'filename': uploaded_file.name,
                    'language': language,
                    'duration': f"{stats['duration']:.1f} min",
                    'words': stats['word_count'],
                    'engine': tts_engine,
                    'ocr_used': use_ocr
                }
                st.session_state.conversion_history.insert(0, history_entry)
                
                # Clean up the temporary file
                try:
                    os.remove(output_filename)
                except:
                    pass
            else:
                st.error(message)

# Conversion History section
if st.session_state.conversion_history:
    st.markdown("---")
    st.header("📜 Conversion History")
    
    for entry in st.session_state.conversion_history:
        with st.expander(f"📁 {entry['filename']} - {entry['timestamp']}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"🌍 **Language**: {entry['language']}")
            with col2:
                st.write(f"⏱️ **Duration**: {entry['duration']}")
            with col3:
                st.write(f"📝 **Words**: {entry['words']:,}")
    
    if st.button("🗑️ Clear History"):
        st.session_state.conversion_history = []
        st.rerun()

# Instructions section
with st.expander("ℹ️ How to Use"):
    st.markdown("""
    ### Quick Start Guide
    
    1. **📤 Upload a PDF**: Click the 'Browse files' button and select your PDF document
    2. **⚙️ Configure Settings**: 
       - Choose your preferred language from the sidebar
       - Toggle slow speech if needed
       - Select page range (all or custom)
       - Enable text cleaning options
    3. **👁️ Preview Text**: Click 'Preview Extracted Text' to see and edit the content
    4. **🎵 Convert**: Click the 'Convert to Audio' button
    5. **🎧 Listen or Download**: Play the audio in your browser or download the MP3 file
    
    ### Features
    - **🌍 Multi-Language Support**: 13+ languages including English, Spanish, French, German, Hindi, Japanese, and more
    - **📄 Page Selection**: Convert specific pages or the entire document
    - **📝 Text Editing**: Preview and edit extracted text before conversion
    - **🧹 Text Cleaning**: Remove extra spaces, newlines, and special characters
    - **📊 Statistics**: View word count, character count, and estimated duration
    - **📜 History**: Track your recent conversions
    - **🌙 Dark Mode**: Toggle between light and dark themes
    
    ### Tips
    - Works best with text-based PDFs
    - Scanned documents (images) may not work without OCR
    - Large files may take longer to process
    - Use the text preview to verify content before conversion
    
    ### Supported Languages
    English, Spanish, French, German, Hindi, Japanese, Italian, Portuguese, Russian, Chinese (Simplified), Korean, Dutch, Arabic
    """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>Built with ❤️ using Streamlit | PDF to Speech Converter</p>
        <p style='font-size: 0.8em;'>Convert your documents to audio and listen on the go!</p>
    </div>
    """, unsafe_allow_html=True
)