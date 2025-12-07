"""Enhanced pipeline with Gemini native video processing option"""

import logging
from pathlib import Path
from typing import Dict
import os

from keyframe_extractor import KeyframeExtractor
from audio_processor import AudioProcessor
from caption_generator import CaptionGenerator
from content_summarizer import ContentSummarizer
from text_summarizer import TextSummarizer
from ppt_generator import PPTGenerator
from gemini_video_analyzer import GeminiVideoAnalyzer
from utils.helpers import cleanup_temp_files
import config

logger = logging.getLogger(__name__)


class VideoSummarizerPipeline:
    """Main pipeline for video summarization with Gemini video processing option"""
    
    def __init__(self):
        """Initialize pipeline with all components"""
        logger.info("\n" + "="*70)
        logger.info("🚀 VIDEO SUMMARIZER PIPELINE INITIALIZATION")
        logger.info("="*70)
        
        # Check if using Gemini video processing
        self.use_gemini_video = config.USE_GEMINI_VIDEO and config.GEMINI_API_KEY
        
        if self.use_gemini_video:
            logger.info("\n📍 PROCESSING MODE: Gemini Native Video")
            logger.info("   ├─ Single API Call for entire video")
            logger.info("   ├─ Visual + Audio analysis combined")
            logger.info("   └─ Model: " + config.GEMINI_MODEL)
            logger.info("")
            self.gemini_analyzer = GeminiVideoAnalyzer(
                api_key=config.GEMINI_API_KEY,
                model_name=config.GEMINI_MODEL
            )
        else:
            logger.info("\n📍 PROCESSING MODE: Traditional Multi-Step Pipeline")
            logger.info("   ├─ Step 1: OpenCV keyframe extraction")
            logger.info("   ├─ Step 2: Whisper (" + config.WHISPER_MODEL + ") audio transcription")
            logger.info("   ├─ Step 3: Gemini (" + config.GEMINI_MODEL + ") image captions")
            logger.info("   ├─ Step 4: Text summarization")
            logger.info("   └─ Step 5: PowerPoint generation")
            logger.info("")
            
            # Initialize traditional components
            logger.info("🔧 Initializing OpenCV Keyframe Extractor...")
            self.keyframe_extractor = KeyframeExtractor(
                motion_threshold=config.MOTION_THRESHOLD,
                histogram_threshold=config.HISTOGRAM_THRESHOLD,
                min_frame_interval=config.MIN_FRAME_INTERVAL,
                max_keyframes=config.MAX_KEYFRAMES
            )
            
            logger.info("🎤 Initializing Whisper Audio Processor...")
            self.audio_processor = AudioProcessor(
                model_name=config.WHISPER_MODEL,
                language=config.WHISPER_LANGUAGE
            )
            
            logger.info("🖼️  Initializing Gemini Caption Generator...")
            self.caption_generator = CaptionGenerator(
                use_gemini_vision=config.USE_GEMINI_VISION,
                api_key=config.GEMINI_API_KEY,
                model_name=config.GEMINI_MODEL
            )
            
            logger.info("📝 Initializing Content Summarizer...")
            self.content_summarizer = ContentSummarizer(
                api_key=config.GEMINI_API_KEY,
                model_name=config.GEMINI_MODEL
            )
        
        # Always need PowerPoint generator
        logger.info("📊 Initializing PowerPoint Generator...")
        self.ppt_generator = PPTGenerator(
            title=config.PPT_TITLE,
            subtitle=config.PPT_SUBTITLE
        )
        
        logger.info("="*70)
        logger.info("✅ Pipeline initialization complete!")
        logger.info("="*70 + "\n")
        
    def process_video(self, video_path: str, output_name: str = None) -> Dict:
        """
        Process video through pipeline
        
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
        
        results = {
            'status': 'processing',
            'video_path': video_path,
            'output_name': output_name,
            'method': 'gemini_video' if self.use_gemini_video else 'traditional'
        }
        
        try:
            if self.use_gemini_video:
                return self._process_with_gemini_video(video_path, output_name, results)
            else:
                return self._process_traditional(video_path, output_name, results)
                
        except Exception as e:
            logger.error(f"Error in pipeline: {e}", exc_info=True)
            results['status'] = 'error'
            results['error'] = str(e)
            return results
    
    def _process_with_gemini_video(self, video_path: str, output_name: str, results: Dict) -> Dict:
        """Process video using Gemini's native video understanding"""
        
        logger.info("\n" + "="*70)
        logger.info("🎬 GEMINI NATIVE VIDEO PROCESSING")
        logger.info("="*70)
        logger.info(f"Model: {config.GEMINI_MODEL}")
        logger.info(f"Method: File API → Multimodal Analysis")
        logger.info("="*70 + "\n")
        
        # Step 1: Upload video to Gemini
        logger.info("📤 Step 1/3: Uploading video to Gemini File API...")
        results['status'] = 'uploading_video'
        video_file = self.gemini_analyzer.upload_video(video_path)
        
        # Step 2: Analyze video
        logger.info(f"\n🔍 Step 2/3: Analyzing video with {config.GEMINI_MODEL}...")
        logger.info("   ├─ Processing visual content (sampled frames)")
        logger.info("   ├─ Processing audio/speech")
        logger.info("   ├─ Identifying key moments with timestamps")
        logger.info("   └─ Generating comprehensive analysis")
        results['status'] = 'analyzing_video'
        analysis = self.gemini_analyzer.analyze_video(video_file, num_keyframes=config.MAX_KEYFRAMES)
        
        results['summary'] = analysis['summary']
        results['transcript'] = analysis['transcript']
        results['keyframe_count'] = len(analysis['key_moments'])
        results['language'] = 'auto-detected'
        
        logger.info(f"Analysis complete: {len(analysis['key_moments'])} key moments identified")
        
        # Step 3: Generate PowerPoint
        logger.info(f"\n📊 Step 3/3: Generating PowerPoint...")
        logger.info(f"   ├─ Creating {len(analysis['key_moments'])} slides")
        logger.info(f"   └─ Format: Text-based with timestamps")
        results['status'] = 'generating_ppt'
        
        # Convert Gemini analysis to slide format
        slides = []
        for i, moment in enumerate(analysis['key_moments']):
            slides.append({
                'number': i + 1,
                'title': f"Key Moment at {moment['timestamp_formatted']}",
                'content': moment['description'],
                'image_caption': moment['description'],
                'timestamp': moment['timestamp']
            })
        
        results['slides'] = slides
        
        # Generate PowerPoint
        ppt_path = config.OUTPUT_FOLDER / f"{output_name}_summary.pptx"
        
        # For Gemini video, we don't have actual keyframe images
        # Create a simple PPT with text only
        self.ppt_generator.create_presentation(
            slides,
            [],  # No keyframe images
            str(ppt_path),
            analysis['summary']
        )
        
        results['ppt_path'] = str(ppt_path)
        results['status'] = 'complete'
        logger.info(f"PowerPoint saved to: {ppt_path}")
        
        # Cleanup
        self.gemini_analyzer.cleanup_file(video_file)
        
        return results
    
    def _process_traditional(self, video_path: str, output_name: str, results: Dict) -> Dict:
        """Process video using content-focused traditional pipeline"""
        
        logger.info("\n" + "="*70)
        logger.info("🔧 CONTENT-FOCUSED PROCESSING")
        logger.info("="*70)
        logger.info(f"Whisper Model: {config.WHISPER_MODEL}")
        logger.info(f"Gemini Model: {config.GEMINI_MODEL}")
        logger.info(f"Summary Slides: {config.SUMMARY_SLIDES_COUNT}")
        logger.info("="*70 + "\n")
        
        # Create temp directory
        temp_dir = config.TEMP_FOLDER / output_name
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        keyframes_dir = temp_dir / "keyframes"
        audio_path = temp_dir / "audio.wav"
        
        # Step 1: Extract keyframes
        logger.info("📸 Step 1/4: Extracting keyframes...")
        results['status'] = 'extracting_keyframes'
        keyframes = self.keyframe_extractor.extract_keyframes(
            video_path, 
            str(keyframes_dir)
        )
        
        keyframe_paths = [kf[1] for kf in keyframes]
        logger.info(f"✅ Extracted {len(keyframes)} keyframes")
        
        # Step 2: Transcribe audio with Whisper
        logger.info(f"\n🎤 Step 2/4: Transcribing audio with Whisper ({config.WHISPER_MODEL})...")
        results['status'] = 'transcribing_audio'
        transcript_data = self.audio_processor.process_video(
            video_path,
            str(audio_path)
        )
        
        results['transcript'] = transcript_data['text']
        results['language'] = transcript_data.get('language', 'unknown')
        logger.info(f"✅ Transcription complete: {len(transcript_data['text'])} chars, Language: {results['language']}")
        
        # Step 3: Create summary with Gemini
        logger.info(f"\n📝 Step 3/4: Creating content summary with Gemini...")
        logger.info(f"   ├─ Analyzing transcript")
        logger.info(f"   ├─ Identifying key topics")
        logger.info(f"   └─ Creating {config.SUMMARY_SLIDES_COUNT} content sections")
        results['status'] = 'summarizing'
        
        summary_data = self.content_summarizer.create_presentation_summary(
            transcript_data['text'],
            num_slides=config.SUMMARY_SLIDES_COUNT
        )
        
        results['summary'] = summary_data['overview']
        logger.info(f"✅ Created summary: '{summary_data['title']}'")
        logger.info(f"   Sections: {[s['title'] for s in summary_data['sections']]}")
        
        # Step 4: Select key visuals (optional)
        selected_keyframes = []
        if config.SELECT_KEY_VISUALS and keyframe_paths:
            logger.info(f"\n🖼️  Step 4/4: Selecting key visuals...")
            logger.info(f"   ├─ Analyzing {len(keyframe_paths)} keyframes")
            logger.info(f"   └─ Selecting {min(5, len(keyframe_paths))} most important")
            
            # Generate captions for selection
            captions = self.caption_generator.generate_captions_batch(keyframe_paths)
            
            # Select most important keyframes
            num_visuals = min(config.SUMMARY_SLIDES_COUNT, len(keyframe_paths))
            selected_keyframes = self.content_summarizer.select_key_visuals(
                keyframe_paths,
                captions,
                num_visuals=num_visuals
            )
            logger.info(f"✅ Selected {len(selected_keyframes)} key visuals")
        
        # Step 5: Generate PowerPoint
        logger.info(f"\n📊 Step 5/5: Generating PowerPoint...")
        logger.info(f"   ├─ Title slide")
        logger.info(f"   ├─ {len(summary_data['sections'])} content slides")
        if selected_keyframes:
            logger.info(f"   ├─ With {len(selected_keyframes)} visual elements")
        logger.info(f"   └─ Summary slide with key takeaways")
        results['status'] = 'generating_ppt'
        
        # Create slides from summary
        slides = []
        
        # Add content sections
        for i, section in enumerate(summary_data['sections']):
            # Find matching keyframe if available
            keyframe_path = None
            if selected_keyframes and i < len(selected_keyframes):
                _, keyframe_path, _ = selected_keyframes[i]
            
            slides.append({
                'number': i + 1,
                'title': section['title'],
                'content': '\n'.join(section['content']),
                'keyframe_path': keyframe_path
            })
        
        # Add takeaways slide
        if summary_data.get('takeaways'):
            slides.append({
                'number': len(slides) + 1,
                'title': 'Key Takeaways',
                'content': '\n'.join(summary_data['takeaways'])
            })
        
        results['slides'] = slides
        results['keyframe_count'] = len(selected_keyframes) if selected_keyframes else 0
        
        # Generate PowerPoint with content-focused layout
        ppt_path = config.OUTPUT_FOLDER / f"{output_name}_summary.pptx"
        
        # Extract just the keyframe paths for PPT generator
        visual_paths = [s['keyframe_path'] for s in slides if s.get('keyframe_path')]
        
        self.ppt_generator.create_presentation(
            slides,
            visual_paths,
            str(ppt_path),
            summary_data['overview']
        )
        
        results['ppt_path'] = str(ppt_path)
        results['status'] = 'complete'
        logger.info(f"\n✅ PowerPoint saved to: {ppt_path}")
        logger.info("="*70 + "\n")
        
        # Cleanup audio file
        cleanup_temp_files(str(audio_path))
        
        return results


def main():
    """CLI entry point for testing"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pipeline_gemini.py <video_path>")
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
        print(f"  - Method: {results['method']}")
        print(f"  - Keyframes/Moments: {results['keyframe_count']}")
        print(f"  - Language: {results['language']}")
        print(f"  - Summary: {results['summary'][:200]}...")
        print(f"  - PowerPoint: {results['ppt_path']}")
    else:
        print(f"\n✗ Error: {results.get('error', 'Unknown error')}")
        

if __name__ == "__main__":
    main()
