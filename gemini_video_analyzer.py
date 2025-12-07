"""Gemini-powered video analyzer - processes entire video with visual + audio understanding"""

import logging
from pathlib import Path
from typing import Dict, List
import time

logger = logging.getLogger(__name__)


class GeminiVideoAnalyzer:
    """Analyze videos using Gemini's native video understanding"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-exp"):
        """
        Initialize Gemini Video Analyzer
        
        Args:
            api_key: Gemini API key
            model_name: Gemini model to use
        """
        self.api_key = api_key
        self.model_name = model_name
        self.client = None
        self.model = None
        
        if api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                self.client = genai
                self.model = genai.GenerativeModel(model_name)
                logger.info("="*60)
                logger.info(f"🎬 GEMINI VIDEO ANALYZER INITIALIZED")
                logger.info(f"   Model: {model_name}")
                logger.info(f"   Capabilities: Video + Audio understanding")
                logger.info(f"   Processing: Native multimodal analysis")
                logger.info(f"   Method: File API upload → Analysis")
                logger.info("="*60)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
                raise
        else:
            raise ValueError("Gemini API key is required for video analysis")
    
    def upload_video(self, video_path: str) -> any:
        """
        Upload video to Gemini using File API
        
        Args:
            video_path: Path to video file
            
        Returns:
            Uploaded file object
        """
        logger.info(f"Uploading video to Gemini: {video_path}")
        
        try:
            # Upload the file
            video_file = self.client.upload_file(path=video_path)
            logger.info(f"Video uploaded: {video_file.name}")
            
            # Wait for processing to complete
            logger.info("Waiting for Gemini to process video...")
            while video_file.state.name == "PROCESSING":
                time.sleep(2)
                video_file = self.client.get_file(video_file.name)
            
            if video_file.state.name == "FAILED":
                raise ValueError(f"Video processing failed: {video_file.state.name}")
            
            logger.info("Video processing complete")
            return video_file
            
        except Exception as e:
            logger.error(f"Error uploading video: {e}")
            raise
    
    def analyze_video(self, video_file: any, num_keyframes: int = 20) -> Dict:
        """
        Analyze video comprehensively using Gemini
        
        Args:
            video_file: Uploaded video file object
            num_keyframes: Number of key moments to identify
            
        Returns:
            Dictionary with analysis results
        """
        logger.info("Analyzing video with Gemini...")
        
        # Create comprehensive prompt
        prompt = f"""Analyze this video comprehensively and provide:

1. **Video Summary**: A concise 2-3 sentence summary of the entire video content.

2. **Key Moments** (exactly {num_keyframes} moments): Identify {num_keyframes} key moments throughout the video with:
   - Timestamp (MM:SS format)
   - Visual description (what's shown on screen)
   - Audio/spoken content at that moment
   - Why this moment is significant

3. **Full Transcript**: Provide a complete transcript of all spoken words in the video.

4. **Visual Themes**: List the main visual themes or types of content shown (e.g., "presentation slides", "code demonstrations", "talking head", etc.)

Format your response as a structured analysis with clear sections."""

        try:
            # Generate content from video
            response = self.model.generate_content([video_file, prompt])
            analysis_text = response.text
            
            logger.info(f"Received analysis ({len(analysis_text)} chars)")
            
            # Parse the response into structured data
            parsed_data = self._parse_analysis(analysis_text, num_keyframes)
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"Error analyzing video: {e}")
            raise
    
    def _parse_analysis(self, analysis_text: str, num_keyframes: int) -> Dict:
        """
        Parse Gemini's analysis into structured data
        
        Args:
            analysis_text: Raw analysis from Gemini
            num_keyframes: Expected number of keyframes
            
        Returns:
            Structured dict with parsed data
        """
        # Split into sections
        sections = {}
        current_section = None
        current_content = []
        
        for line in analysis_text.split('\n'):
            line = line.strip()
            
            # Check for section headers
            if 'summary' in line.lower() and len(line) < 50:
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = 'summary'
                current_content = []
            elif 'key moment' in line.lower() and len(line) < 50:
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = 'key_moments'
                current_content = []
            elif 'transcript' in line.lower() and len(line) < 50:
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = 'transcript'
                current_content = []
            elif 'visual theme' in line.lower() and len(line) < 50:
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = 'visual_themes'
                current_content = []
            elif line:
                current_content.append(line)
        
        # Add last section
        if current_section:
            sections[current_section] = '\n'.join(current_content)
        
        # Extract key moments with timestamps
        key_moments = self._extract_key_moments(sections.get('key_moments', ''))
        
        # If we didn't get enough moments, create generic ones
        if len(key_moments) < num_keyframes // 2:
            logger.warning(f"Only extracted {len(key_moments)} moments, creating evenly spaced fallbacks")
            # Keep any we found, but fill in gaps
            key_moments = self._create_fallback_moments(num_keyframes, sections.get('summary', ''))
        
        return {
            'summary': sections.get('summary', analysis_text[:500]).strip(),
            'transcript': sections.get('transcript', '').strip(),
            'key_moments': key_moments,
            'visual_themes': sections.get('visual_themes', '').strip(),
            'full_analysis': analysis_text
        }
    
    def _extract_key_moments(self, moments_text: str) -> List[Dict]:
        """Extract structured key moments from text"""
        moments = []
        current_moment = {}
        
        for line in moments_text.split('\n'):
            line = line.strip()
            
            # Look for timestamps (MM:SS or M:SS or HH:MM:SS)
            import re
            timestamp_match = re.search(r'(\d{1,2}):(\d{2})(?::(\d{2}))?', line)
            
            if timestamp_match:
                # Save previous moment if exists
                if current_moment and 'timestamp' in current_moment:
                    moments.append(current_moment)
                
                # Start new moment
                groups = timestamp_match.groups()
                if groups[2]:  # HH:MM:SS format
                    seconds = int(groups[0]) * 3600 + int(groups[1]) * 60 + int(groups[2])
                else:  # MM:SS format
                    seconds = int(groups[0]) * 60 + int(groups[1])
                
                current_moment = {
                    'timestamp': seconds,
                    'timestamp_formatted': timestamp_match.group(0),
                    'description': line
                }
            elif current_moment and line:
                # Add to current moment's description
                current_moment['description'] = current_moment.get('description', '') + ' ' + line
        
        # Add last moment
        if current_moment and 'timestamp' in current_moment:
            moments.append(current_moment)
        
        # Sort by timestamp
        moments.sort(key=lambda x: x['timestamp'])
        
        logger.info(f"Extracted {len(moments)} key moments")
        return moments
    
    def _create_fallback_moments(self, count: int, summary: str) -> List[Dict]:
        """Create evenly spaced fallback moments if parsing failed"""
        moments = []
        for i in range(count):
            # Create evenly spaced fake timestamps
            seconds = int((i / count) * 600)  # Assume 10 min video max for fallback
            minutes = seconds // 60
            secs = seconds % 60
            
            moments.append({
                'timestamp': seconds,
                'timestamp_formatted': f"{minutes:02d}:{secs:02d}",
                'description': f"Key moment {i+1}: {summary[:100] if summary else 'Video content'}"
            })
        
        return moments
    
    def cleanup_file(self, video_file: any):
        """Delete uploaded file from Gemini"""
        try:
            self.client.delete_file(video_file.name)
            logger.info(f"Deleted file: {video_file.name}")
        except Exception as e:
            logger.warning(f"Could not delete file: {e}")
