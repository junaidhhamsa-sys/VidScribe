"""Content-focused summarization using Gemini for concise presentations"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class ContentSummarizer:
    """Create content-focused summaries using Gemini"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash-lite"):
        """
        Initialize ContentSummarizer
        
        Args:
            api_key: Gemini API key
            model_name: Gemini model to use
        """
        self.api_key = api_key
        self.model_name = model_name
        self.model = None
        
        if api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(model_name)
                logger.info("="*60)
                logger.info(f"📝 GEMINI CONTENT SUMMARIZER INITIALIZED")
                logger.info(f"   Model: {model_name}")
                logger.info(f"   Purpose: Create concise content summaries")
                logger.info("="*60)
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini: {e}")
    
    def create_presentation_summary(
        self, 
        transcript: str, 
        num_slides: int = 5,
        presentation_style: str = "professional"
    ) -> Dict:
        """
        Create a concise summary for presentation
        
        Args:
            transcript: Full video transcript
            num_slides: Number of content slides to create
            presentation_style: Style of presentation (professional, educational, casual)
            
        Returns:
            Dictionary with title, overview, and slide sections
        """
        if not self.model:
            logger.warning("Gemini not available, using basic summarization")
            return self._create_basic_summary(transcript, num_slides)
        
        logger.info(f"Creating {num_slides}-slide presentation summary with Gemini...")
        
        prompt = f"""Analyze this video transcript and create a concise presentation summary.

TRANSCRIPT:
{transcript[:8000]}  # Limit to avoid token limits

TASK:
Create a structured presentation with exactly {num_slides} main content sections.

FORMAT YOUR RESPONSE AS:
## TITLE
[A clear, engaging title for the presentation]

## OVERVIEW
[2-3 sentence overview of what this video covers]

## SECTION 1: [Section Title]
[2-3 bullet points of key content]

## SECTION 2: [Section Title]
[2-3 bullet points of key content]

[Continue for all {num_slides} sections]

## KEY TAKEAWAYS
[3-4 main takeaways from the video]

RULES:
- Be concise and actionable
- Focus on main ideas, not every detail
- Use clear, professional language
- Each section should cover a distinct topic
- Bullet points should be short (1-2 lines max)
"""

        try:
            response = self.model.generate_content(prompt)
            summary_text = response.text
            
            # Parse the response
            parsed = self._parse_gemini_response(summary_text, num_slides)
            
            logger.info(f"✅ Created presentation with {len(parsed['sections'])} sections")
            return parsed
            
        except Exception as e:
            logger.error(f"Error with Gemini summarization: {e}")
            return self._create_basic_summary(transcript, num_slides)
    
    def _parse_gemini_response(self, response_text: str, expected_slides: int) -> Dict:
        """Parse Gemini's structured response"""
        
        lines = response_text.split('\n')
        result = {
            'title': 'Video Summary',
            'overview': '',
            'sections': [],
            'takeaways': []
        }
        
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('## TITLE'):
                continue
            elif line.startswith('## OVERVIEW'):
                current_section = 'overview'
                current_content = []
            elif line.startswith('## KEY TAKEAWAYS'):
                if current_section and current_content:
                    if current_section == 'overview':
                        result['overview'] = ' '.join(current_content)
                    elif isinstance(current_section, dict):
                        current_section['content'] = current_content
                        result['sections'].append(current_section)
                current_section = 'takeaways'
                current_content = []
            elif line.startswith('## SECTION'):
                # Save previous section
                if current_section == 'overview':
                    result['overview'] = ' '.join(current_content)
                elif isinstance(current_section, dict):
                    current_section['content'] = current_content
                    result['sections'].append(current_section)
                
                # Start new section
                title = line.split(':', 1)[1].strip() if ':' in line else f"Section {len(result['sections']) + 1}"
                current_section = {'title': title, 'content': []}
                current_content = []
            elif line and current_section:
                if line.startswith('#'):
                    # It's a title line
                    if current_section == 'overview' and not result['title'] == 'Video Summary':
                        pass  # Already have title
                    elif line.strip('#').strip():
                        result['title'] = line.strip('#').strip()
                else:
                    current_content.append(line)
        
        # Save last section
        if current_section == 'takeaways':
            result['takeaways'] = current_content
        elif isinstance(current_section, dict):
            current_section['content'] = current_content
            result['sections'].append(current_section)
        
        logger.info(f"Parsed: {result['title']}, {len(result['sections'])} sections")
        return result
    
    def _create_basic_summary(self, transcript: str, num_slides: int) -> Dict:
        """Fallback basic summarization without Gemini"""
        
        # Split transcript into chunks
        words = transcript.split()
        chunk_size = len(words) // num_slides if len(words) > num_slides else len(words)
        
        sections = []
        for i in range(num_slides):
            start = i * chunk_size
            end = start + chunk_size
            chunk = ' '.join(words[start:end])
            
            # Get first sentence as title
            sentences = chunk.split('.')
            title = sentences[0][:50] + "..." if len(sentences[0]) > 50 else sentences[0]
            
            sections.append({
                'title': f"Part {i+1}: {title}",
                'content': [chunk[:200] + "..."]
            })
        
        return {
            'title': 'Video Summary',
            'overview': transcript[:300] + "...",
            'sections': sections,
            'takeaways': ['See transcript for full details']
        }
    
    def select_key_visuals(
        self,
        keyframe_paths: List[str],
        captions: List[str],
        num_visuals: int = 5
    ) -> List[tuple]:
        """
        Select most important keyframes based on caption analysis
        
        Args:
            keyframe_paths: List of keyframe image paths
            captions: Descriptions of each keyframe
            num_visuals: Number of keyframes to select
            
        Returns:
            List of (index, path, caption) tuples for selected keyframes
        """
        if not self.model or not captions:
            # Fallback: select evenly spaced frames
            indices = [int(i * len(keyframe_paths) / num_visuals) for i in range(num_visuals)]
            return [(i, keyframe_paths[i], captions[i] if i < len(captions) else "") for i in indices]
        
        logger.info(f"Selecting {num_visuals} most important visuals from {len(keyframe_paths)} keyframes...")
        
        # Create prompt to select important frames
        captions_list = "\n".join([f"{i+1}. {cap[:100]}" for i, cap in enumerate(captions)])
        
        prompt = f"""From these video frame descriptions, select the {num_visuals} MOST IMPORTANT and VISUALLY DISTINCT frames that best represent the key moments of the video.

FRAME DESCRIPTIONS:
{captions_list}

Return ONLY the numbers (1-{len(captions)}) of the {num_visuals} most important frames, separated by commas.
Choose frames that:
- Show different key moments or topics
- Are visually informative or distinct
- Best illustrate the main content

Your response (ONLY numbers, comma-separated):"""

        try:
            response = self.model.generate_content(prompt)
            selected_text = response.text.strip()
            
            # Extract numbers
            selected_indices = []
            for part in selected_text.replace(' ', '').split(','):
                try:
                    idx = int(part) - 1  # Convert to 0-indexed
                    if 0 <= idx < len(keyframe_paths):
                        selected_indices.append(idx)
                except:
                    continue
            
            # If we didn't get enough, fill in with evenly spaced
            if len(selected_indices) < num_visuals:
                step = len(keyframe_paths) // (num_visuals - len(selected_indices))
                for i in range(0, len(keyframe_paths), step):
                    if i not in selected_indices and len(selected_indices) < num_visuals:
                        selected_indices.append(i)
            
            # Limit to requested number
            selected_indices = selected_indices[:num_visuals]
            
            result = [
                (idx, keyframe_paths[idx], captions[idx] if idx < len(captions) else "")
                for idx in selected_indices
            ]
            
            logger.info(f"✅ Selected keyframes at indices: {selected_indices}")
            return result
            
        except Exception as e:
            logger.error(f"Error selecting keyframes: {e}, using evenly spaced")
            indices = [int(i * len(keyframe_paths) / num_visuals) for i in range(num_visuals)]
            return [(i, keyframe_paths[i], captions[i] if i < len(captions) else "") for i in indices]
