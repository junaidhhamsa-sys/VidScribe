"""Gemini AI processor for video analysis and summarization"""

import google.generativeai as genai
from PIL import Image
import logging
from typing import List, Dict, Optional
import time
import config

logger = logging.getLogger(__name__)


class GeminiProcessor:
    """Handle all Gemini AI interactions"""
    
    def __init__(self, api_key: str = None, model_name: str = None):
        """
        Initialize Gemini processor
        
        Args:
            api_key: Gemini API key (uses config if None)
            model_name: Model name (uses config if None)
        """
        self.api_key = api_key or config.GEMINI_API_KEY
        self.model_name = model_name or config.GEMINI_MODEL
        
        if not self.api_key:
            raise ValueError("Gemini API key not configured. Set GEMINI_API_KEY in .env file")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize model
        self.model = genai.GenerativeModel(self.model_name)
        
        logger.info(f"Gemini processor initialized with model: {self.model_name}")
    
    def generate_image_caption(self, image_path: str, custom_prompt: str = None) -> str:
        """
        Generate caption for a single image
        
        Args:
            image_path: Path to image file
            custom_prompt: Custom prompt (uses default if None)
            
        Returns:
            Generated caption text
        """
        try:
            # Load image
            img = Image.open(image_path)
            
            # Default prompt
            prompt = custom_prompt or """
            Describe what's happening in this image in 2-3 sentences.
            Focus on:
            - Main subject or topic
            - Key visual elements
            - Important text or diagrams (if any)
            - Context or setting
            
            Be concise and informative.
            """
            
            # Generate caption
            response = self.model.generate_content([prompt, img])
            caption = response.text.strip()
            
            logger.debug(f"Generated caption for {image_path}")
            return caption
            
        except Exception as e:
            logger.error(f"Error generating caption for {image_path}: {e}")
            return f"[Caption generation failed: {str(e)}]"
    
    def generate_captions_batch(self, image_paths: List[str], 
                                delay: float = 0.5) -> List[Dict[str, str]]:
        """
        Generate captions for multiple images
        
        Args:
            image_paths: List of image file paths
            delay: Delay between API calls (to avoid rate limits)
            
        Returns:
            List of dictionaries with image_path and caption
        """
        captions = []
        
        logger.info(f"Generating captions for {len(image_paths)} images...")
        
        for i, image_path in enumerate(image_paths, 1):
            try:
                caption = self.generate_image_caption(image_path)
                captions.append({
                    'image_path': image_path,
                    'caption': caption
                })
                
                logger.info(f"  [{i}/{len(image_paths)}] Captioned: {image_path}")
                
                # Rate limiting
                if i < len(image_paths):
                    time.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Error processing {image_path}: {e}")
                captions.append({
                    'image_path': image_path,
                    'caption': f"[Error: {str(e)}]"
                })
        
        return captions
    
    def create_video_summary(self, transcript: str, captions: List[Dict], 
                            custom_prompt: str = None) -> Dict[str, str]:
        """
        Create comprehensive video summary from transcript and captions
        
        Args:
            transcript: Audio transcript text
            captions: List of image captions with timestamps
            custom_prompt: Custom prompt (uses default if None)
            
        Returns:
            Dictionary with summary components
        """
        try:
            # Combine visual and audio information
            visual_content = "\n\n".join([
                f"Visual {i+1}: {cap['caption']}" 
                for i, cap in enumerate(captions)
            ])
            
            # Default prompt
            prompt = custom_prompt or f"""
            You are analyzing a video. Below is the audio transcript and descriptions of key visual moments.
            
            AUDIO TRANSCRIPT:
            {transcript}
            
            VISUAL DESCRIPTIONS:
            {visual_content}
            
            Please provide:
            
            1. **Title**: A concise, descriptive title for this video (max 10 words)
            
            2. **Overview**: A 2-3 sentence summary of the main topic and purpose (max 100 words)
            
            3. **Key Points**: List 5-8 main points covered in the video as bullet points
            
            4. **Detailed Summary**: A comprehensive summary organized into clear sections (max 400 words)
            
            Format your response as:
            
            TITLE: [title here]
            
            OVERVIEW: [overview here]
            
            KEY POINTS:
            - [point 1]
            - [point 2]
            ...
            
            DETAILED SUMMARY:
            [detailed summary here]
            """
            
            # Generate summary
            response = self.model.generate_content(prompt)
            summary_text = response.text.strip()
            
            # Parse response
            summary = self._parse_summary_response(summary_text)
            
            logger.info("Video summary generated successfully")
            return summary
            
        except Exception as e:
            logger.error(f"Error creating video summary: {e}")
            return {
                'title': 'Video Summary',
                'overview': f'Error generating summary: {str(e)}',
                'key_points': [],
                'detailed_summary': ''
            }
    
    def create_content_sections(self, transcript: str, 
                               num_sections: int = 5) -> Dict:
        """
        Create structured content sections from transcript
        
        Args:
            transcript: Full transcript text
            num_sections: Number of sections to create
            
        Returns:
            Dictionary with title, overview, and sections
        """
        try:
            prompt = f"""
            Analyze this video transcript and create a structured presentation with {num_sections} main content sections.
            
            TRANSCRIPT:
            {transcript}
            
            Provide:
            1. A catchy title (max 10 words)
            2. A brief overview (2-3 sentences)
            3. {num_sections} main content sections, each with:
               - A section title (3-6 words)
               - 3-5 bullet points explaining the key information
            4. 3-5 key takeaways from the entire content
            
            Format as:
            
            TITLE: [title]
            
            OVERVIEW: [overview]
            
            SECTION 1: [title]
            - [bullet point 1]
            - [bullet point 2]
            ...
            
            SECTION 2: [title]
            ...
            
            KEY TAKEAWAYS:
            - [takeaway 1]
            - [takeaway 2]
            ...
            """
            
            response = self.model.generate_content(prompt)
            result = self._parse_sections_response(response.text.strip())
            
            logger.info(f"Created {len(result['sections'])} content sections")
            return result
            
        except Exception as e:
            logger.error(f"Error creating content sections: {e}")
            return {
                'title': 'Video Content Summary',
                'overview': f'Error: {str(e)}',
                'sections': [],
                'takeaways': []
            }
    
    def select_key_visuals(self, captions: List[Dict], 
                          transcript: str, num_visuals: int = 5) -> List[int]:
        """
        Use AI to select most important visuals
        
        Args:
            captions: List of image captions
            transcript: Full transcript
            num_visuals: Number of visuals to select
            
        Returns:
            List of indices of selected images
        """
        try:
            captions_text = "\n".join([
                f"{i}. {cap['caption']}" 
                for i, cap in enumerate(captions)
            ])
            
            prompt = f"""
            Given these visual descriptions from a video and the transcript, 
            select the {num_visuals} MOST IMPORTANT visuals that best represent the key concepts.
            
            VISUALS:
            {captions_text}
            
            TRANSCRIPT SNIPPET:
            {transcript[:1000]}...
            
            Return ONLY the numbers (0-{len(captions)-1}) of the {num_visuals} most important visuals, 
            comma-separated, like: 0,3,7,12,15
            """
            
            response = self.model.generate_content(prompt)
            indices_text = response.text.strip()
            
            # Parse indices
            indices = [int(x.strip()) for x in indices_text.split(',') if x.strip().isdigit()]
            indices = [i for i in indices if 0 <= i < len(captions)][:num_visuals]
            
            logger.info(f"Selected {len(indices)} key visuals: {indices}")
            return indices
            
        except Exception as e:
            logger.error(f"Error selecting visuals: {e}")
            # Fallback: evenly spaced selection
            step = len(captions) // num_visuals if num_visuals > 0 else 1
            return list(range(0, len(captions), step))[:num_visuals]
    
    def _parse_summary_response(self, text: str) -> Dict[str, any]:
        """Parse structured summary response"""
        result = {
            'title': 'Video Summary',
            'overview': '',
            'key_points': [],
            'detailed_summary': ''
        }
        
        try:
            lines = text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                
                if line.startswith('TITLE:'):
                    result['title'] = line.replace('TITLE:', '').strip()
                elif line.startswith('OVERVIEW:'):
                    result['overview'] = line.replace('OVERVIEW:', '').strip()
                    current_section = 'overview'
                elif line.startswith('KEY POINTS:'):
                    current_section = 'key_points'
                elif line.startswith('DETAILED SUMMARY:'):
                    current_section = 'detailed_summary'
                elif line.startswith('- ') and current_section == 'key_points':
                    result['key_points'].append(line[2:].strip())
                elif current_section == 'overview' and line and not line.startswith(('TITLE:', 'KEY POINTS:')):
                    result['overview'] += ' ' + line
                elif current_section == 'detailed_summary' and line:
                    result['detailed_summary'] += line + '\n'
            
            result['overview'] = result['overview'].strip()
            result['detailed_summary'] = result['detailed_summary'].strip()
            
        except Exception as e:
            logger.error(f"Error parsing summary: {e}")
        
        return result
    
    def _parse_sections_response(self, text: str) -> Dict:
        """Parse structured sections response"""
        result = {
            'title': 'Content Summary',
            'overview': '',
            'sections': [],
            'takeaways': []
        }
        
        try:
            lines = text.split('\n')
            current_section = None
            current_section_data = None
            
            for line in lines:
                line = line.strip()
                
                if line.startswith('TITLE:'):
                    result['title'] = line.replace('TITLE:', '').strip()
                elif line.startswith('OVERVIEW:'):
                    result['overview'] = line.replace('OVERVIEW:', '').strip()
                elif line.startswith('SECTION '):
                    if current_section_data:
                        result['sections'].append(current_section_data)
                    title = line.split(':', 1)[1].strip() if ':' in line else line
                    current_section_data = {'title': title, 'content': []}
                elif line.startswith('KEY TAKEAWAYS:'):
                    if current_section_data:
                        result['sections'].append(current_section_data)
                        current_section_data = None
                    current_section = 'takeaways'
                elif line.startswith('- '):
                    content = line[2:].strip()
                    if current_section == 'takeaways':
                        result['takeaways'].append(content)
                    elif current_section_data:
                        current_section_data['content'].append(content)
            
            # Add last section
            if current_section_data:
                result['sections'].append(current_section_data)
            
        except Exception as e:
            logger.error(f"Error parsing sections: {e}")
        
        return result


def test_gemini_connection(api_key: str = None) -> bool:
    """
    Test Gemini API connection
    
    Args:
        api_key: API key to test (uses config if None)
        
    Returns:
        True if connection successful
    """
    try:
        processor = GeminiProcessor(api_key=api_key)
        
        # Simple test prompt
        response = processor.model.generate_content("Say 'Hello, Gemini is working!'")
        result = response.text.strip()
        
        logger.info(f"✅ Gemini test successful: {result}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Gemini test failed: {e}")
        return False