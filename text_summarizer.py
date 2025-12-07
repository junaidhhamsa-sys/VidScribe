"""Text summarization combining transcripts and captions"""

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class TextSummarizer:
    """Summarize video content from transcripts and captions"""
    
    def __init__(self, max_length=500):
        """
        Initialize TextSummarizer
        
        Args:
            max_length: Maximum length of summary in words
        """
        self.max_length = max_length
        
    def summarize(self, transcript: str, captions: List[str], 
                  keyframe_timestamps: List[float] = None) -> Dict:
        """
        Create summary from transcript and captions
        
        Args:
            transcript: Full video transcript
            captions: List of keyframe captions
            keyframe_timestamps: Optional timestamps for keyframes
            
        Returns:
            Dictionary with summary and slide content
        """
        logger.info("Creating summary from transcript and captions")
        
        # Create overall summary
        overall_summary = self._create_overall_summary(transcript, captions)
        
        # Create slide content
        slides = self._create_slide_content(transcript, captions, keyframe_timestamps)
        
        return {
            'overall_summary': overall_summary,
            'slides': slides,
            'total_slides': len(slides)
        }
        
    def _create_overall_summary(self, transcript: str, captions: List[str]) -> str:
        """Create overall video summary"""
        
        # Extract key sentences from transcript
        sentences = [s.strip() for s in transcript.split('.') if s.strip()]
        
        # Simple extractive summarization - take important sentences
        # In a production system, you'd use a proper NLP model here
        summary_sentences = []
        
        # Add opening context
        if sentences:
            summary_sentences.append(sentences[0])
        
        # Add middle context
        if len(sentences) > 2:
            mid_point = len(sentences) // 2
            summary_sentences.append(sentences[mid_point])
        
        # Add closing context
        if len(sentences) > 1:
            summary_sentences.append(sentences[-1])
        
        # Combine with visual context
        visual_summary = f"The video contains {len(captions)} key visual segments."
        
        summary = '. '.join(summary_sentences) + '. ' + visual_summary
        
        # Truncate if too long
        words = summary.split()
        if len(words) > self.max_length:
            summary = ' '.join(words[:self.max_length]) + '...'
        
        logger.info(f"Created summary: {len(summary)} characters")
        return summary
        
    def _create_slide_content(self, transcript: str, captions: List[str], 
                             timestamps: List[float] = None) -> List[Dict]:
        """Create content for individual slides"""
        
        slides = []
        
        # Split transcript into segments based on number of captions
        if not captions:
            return slides
            
        # Simple approach: divide transcript into equal parts
        sentences = [s.strip() + '.' for s in transcript.split('.') if s.strip()]
        segment_size = max(1, len(sentences) // len(captions))
        
        for i, caption in enumerate(captions):
            # Get corresponding transcript segment
            start_idx = i * segment_size
            end_idx = min((i + 1) * segment_size, len(sentences))
            segment_text = ' '.join(sentences[start_idx:end_idx])
            
            # Create slide
            timestamp = timestamps[i] if timestamps and i < len(timestamps) else None
            
            slide = {
                'number': i + 1,
                'title': self._extract_title(segment_text, caption),
                'content': segment_text if segment_text else caption,
                'image_caption': caption,
                'timestamp': timestamp
            }
            
            slides.append(slide)
            
        logger.info(f"Created {len(slides)} slides")
        return slides
        
    def _extract_title(self, text: str, caption: str) -> str:
        """Extract or generate a title for the slide"""
        
        # Try to get first meaningful phrase
        words = text.split()
        if len(words) > 5:
            title = ' '.join(words[:5]) + '...'
        elif words:
            title = ' '.join(words)
        else:
            # Use caption to generate title
            caption_words = caption.split()
            title = ' '.join(caption_words[:5]) + '...' if len(caption_words) > 5 else caption
            
        # Capitalize and clean
        title = title.strip().capitalize()
        if not title.endswith('...'):
            title = title.rstrip('.')
            
        return title
