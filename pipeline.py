"""Main pipeline orchestrating all components"""

import logging
from pathlib import Path
from typing import Dict
import os

from keyframe_extractor import KeyframeExtractor
from audio_processor import AudioProcessor
from caption_generator import CaptionGenerator
from text_summarizer import TextSummarizer
from ppt_generator import PPTGenerator
from utils.helpers import cleanup_temp_files, format_time
import config

logger = logging.getLogger(__name__)


class VideoSummarizerPipeline:
    """Main pipeline for video summarization"""
    
    def __init__(self):
        """Initialize pipeline with all components"""
        logger.info("Initializing Video Summarizer Pipeline")
        
        # Initialize components
        self.keyframe_extractor = KeyframeExtractor(
            motion_threshold=config.MOTION_THRESHOLD,
            histogram_threshold=config.HISTOGRAM_THRESHOLD,
            min_frame_interval=config.MIN_FRAME_INTERVAL,
            max_keyframes=config.MAX_KEYFRAMES
        )
        
        self.audio_processor = AudioProcessor(
            model_name=config.WHISPER_MODEL,
            language=config.WHISPER_LANGUAGE
        )
        
        self.caption_generator = CaptionGenerator(
            use_gemini_vision=config.USE_GEMINI_VISION,
            api_key=config.GEMINI_API_KEY,
            model_name=config.GEMINI_MODEL
        )
        
        self.text_summarizer = TextSummarizer(
            max_length=config.SUMMARY_MAX_LENGTH
        )
        
        self.ppt_generator = PPTGenerator(
            title=config.PPT_TITLE,
            subtitle=config.PPT_SUBTITLE
        )
        
    def process_video(self, video_path: str, output_name: str = None) -> Dict:
        """
        Process video through complete pipeline
        
        Args:
            video_path: Path to input video
            output_name: Name for output files (optional)
            
        Returns:
            Dictionary with results and file paths
        """
        logger.info(f"Starting video processing pipeline for: {video_path}")
        
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Generate output name
        if output_name is None:
            output_name = Path(video_path).stem
            
        # Create temp directory for this video
        temp_dir = config.TEMP_FOLDER / output_name
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        keyframes_dir = temp_dir / "keyframes"
        audio_path = temp_dir / "audio.wav"
        
        results = {
            'status': 'processing',
            'video_path': video_path,
            'output_name': output_name
        }
        
        try:
            # Step 1: Extract keyframes
            logger.info("Step 1/5: Extracting keyframes...")
            results['status'] = 'extracting_keyframes'
            keyframes = self.keyframe_extractor.extract_keyframes(
                video_path, 
                str(keyframes_dir)
            )
            
            keyframe_paths = [kf[1] for kf in keyframes]
            keyframe_numbers = [kf[0] for kf in keyframes]
            
            results['keyframes'] = keyframe_paths
            results['keyframe_count'] = len(keyframes)
            logger.info(f"Extracted {len(keyframes)} keyframes")
            
            # Step 2: Extract and transcribe audio
            logger.info("Step 2/5: Extracting and transcribing audio...")
            results['status'] = 'transcribing_audio'
            transcript_data = self.audio_processor.process_video(
                video_path,
                str(audio_path)
            )
            
            results['transcript'] = transcript_data['text']
            results['language'] = transcript_data.get('language', 'unknown')
            logger.info(f"Transcription complete: {len(transcript_data['text'])} chars")
            
            # Step 3: Generate captions for keyframes
            logger.info("Step 3/5: Generating image captions...")
            results['status'] = 'generating_captions'
            captions = self.caption_generator.generate_captions_batch(keyframe_paths)
            
            results['captions'] = captions
            logger.info(f"Generated {len(captions)} captions")
            
            # Step 4: Create summary
            logger.info("Step 4/5: Creating summary...")
            results['status'] = 'summarizing'
            
            # Calculate timestamps for keyframes
            import cv2
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            cap.release()
            
            timestamps = [frame_num / fps for frame_num in keyframe_numbers]
            
            summary_data = self.text_summarizer.summarize(
                transcript_data['text'],
                captions,
                timestamps
            )
            
            results['summary'] = summary_data['overall_summary']
            results['slides'] = summary_data['slides']
            logger.info(f"Created summary with {len(summary_data['slides'])} slides")
            
            # Step 5: Generate PowerPoint
            logger.info("Step 5/5: Generating PowerPoint...")
            results['status'] = 'generating_ppt'
            
            ppt_path = config.OUTPUT_FOLDER / f"{output_name}_summary.pptx"
            self.ppt_generator.create_presentation(
                summary_data['slides'],
                keyframe_paths,
                str(ppt_path),
                summary_data['overall_summary']
            )
            
            results['ppt_path'] = str(ppt_path)
            results['status'] = 'complete'
            logger.info(f"PowerPoint saved to: {ppt_path}")
            
            # Cleanup audio file (keep keyframes for preview)
            cleanup_temp_files(str(audio_path))
            
            return results
            
        except Exception as e:
            logger.error(f"Error in pipeline: {e}", exc_info=True)
            results['status'] = 'error'
            results['error'] = str(e)
            return results


def main():
    """CLI entry point for testing"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pipeline.py <video_path>")
        sys.exit(1)
        
    video_path = sys.argv[1]
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run pipeline
    pipeline = VideoSummarizerPipeline()
    results = pipeline.process_video(video_path)
    
    if results['status'] == 'complete':
        print(f"\n✓ Video processing complete!")
        print(f"  - Keyframes: {results['keyframe_count']}")
        print(f"  - Language: {results['language']}")
        print(f"  - Summary: {results['summary'][:200]}...")
        print(f"  - PowerPoint: {results['ppt_path']}")
    else:
        print(f"\n✗ Error: {results.get('error', 'Unknown error')}")
        

if __name__ == "__main__":
    main()
