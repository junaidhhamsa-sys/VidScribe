"""Audio extraction and transcription using MoviePy and Whisper"""

import whisper
try:
    # Try moviepy 2.x import
    from moviepy import VideoFileClip
except ImportError:
    # Fall back to moviepy 1.x import
    from moviepy.editor import VideoFileClip
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Extract audio from video and transcribe using Whisper"""
    
    def __init__(self, model_name="base", language=None):
        """
        Initialize AudioProcessor
        
        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
            language: Language code (None for auto-detect)
        """
        self.model_name = model_name
        self.language = language
        self.model = None
        
    def load_model(self):
        """Load Whisper model (lazy loading)"""
        if self.model is None:
            logger.info("="*60)
            logger.info(f"🎤 WHISPER MODEL LOADING")
            logger.info(f"   Model Size: {self.model_name}")
            logger.info(f"   Language: {self.language or 'Auto-detect'}")
            logger.info(f"   Purpose: Audio transcription")
            logger.info("="*60)
            self.model = whisper.load_model(self.model_name)
            logger.info("✅ Whisper model loaded successfully")
            logger.info("="*60)
            
    def extract_audio(self, video_path: str, audio_path: str = None) -> str:
        """
        Extract audio from video file
        
        Args:
            video_path: Path to input video
            audio_path: Path to save audio (optional, auto-generated if None)
            
        Returns:
            Path to extracted audio file
        """
        logger.info(f"Extracting audio from {video_path}")
        
        if audio_path is None:
            video_name = Path(video_path).stem
            audio_path = str(Path(video_path).parent / f"{video_name}_audio.wav")
            
        try:
            video = VideoFileClip(video_path)
            # MoviePy 2.x doesn't support verbose and logger parameters
            video.audio.write_audiofile(audio_path)
            video.close()
            logger.info(f"Audio extracted to {audio_path}")
            return audio_path
        except Exception as e:
            logger.error(f"Error extracting audio: {e}")
            raise
            
    def transcribe_audio(self, audio_path: str) -> dict:
        """
        Transcribe audio using Whisper
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary with transcription results
        """
        logger.info(f"Transcribing audio from {audio_path}")
        
        self.load_model()
        
        try:
            result = self.model.transcribe(
                audio_path,
                language=self.language,
                verbose=False
            )
            
            logger.info(f"Transcription complete. Detected language: {result.get('language', 'unknown')}")
            logger.info(f"Transcript length: {len(result['text'])} characters")
            
            return {
                'text': result['text'],
                'language': result.get('language'),
                'segments': result.get('segments', [])
            }
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise
            
    def process_video(self, video_path: str, temp_audio_path: str = None) -> dict:
        """
        Complete pipeline: extract audio and transcribe
        
        Args:
            video_path: Path to input video
            temp_audio_path: Path for temporary audio file
            
        Returns:
            Transcription results
        """
        logger.info(f"Processing video: {video_path}")
        
        # Extract audio
        audio_path = self.extract_audio(video_path, temp_audio_path)
        
        # Transcribe
        result = self.transcribe_audio(audio_path)
        
        return result
