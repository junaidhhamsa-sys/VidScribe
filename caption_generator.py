"""Generate captions for images using AI models"""

import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


class CaptionGenerator:
    """Generate descriptive captions for keyframe images"""
    
    def __init__(self, use_gemini_vision=False, api_key=None, model_name="gemini-2.0-flash-exp"):
        """
        Initialize CaptionGenerator
        
        Args:
            use_gemini_vision: Whether to use Gemini Flash API
            api_key: Gemini API key (required if use_gemini_vision=True)
            model_name: Gemini model to use
        """
        self.use_gemini_vision = use_gemini_vision
        self.api_key = api_key
        self.model_name = model_name
        self.model = None
        
        if use_gemini_vision and api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(model_name)
                logger.info("="*60)
                logger.info(f"✅ GEMINI VISION INITIALIZED")
                logger.info(f"   Model: {model_name}")
                logger.info(f"   Purpose: Image caption generation")
                logger.info("="*60)
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini: {e}")
                
    def generate_caption(self, image_path: str) -> str:
        """
        Generate caption for a single image
        
        Args:
            image_path: Path to image file
            
        Returns:
            Caption text
        """
        if self.use_gemini_vision and self.model:
            return self._generate_caption_gemini(image_path)
        else:
            return self._generate_caption_basic(image_path)
            
    def _generate_caption_gemini(self, image_path: str) -> str:
        """Generate caption using Gemini Flash"""
        try:
            from PIL import Image
            
            # Open image
            img = Image.open(image_path)
            
            # Create prompt
            prompt = "Describe this video frame in detail. Focus on the main content, any text visible, UI elements, and key visual elements. Be concise but informative."
            
            # Generate caption
            response = self.model.generate_content([prompt, img])
            caption = response.text.strip()
            
            logger.info(f"Generated Gemini caption: {caption[:100]}...")
            return caption
            
        except Exception as e:
            logger.error(f"Error with Gemini Vision, falling back to basic: {e}")
            return self._generate_caption_basic(image_path)
            
    def _generate_caption_basic(self, image_path: str) -> str:
        """Generate basic caption using image analysis"""
        import cv2
        import numpy as np
        
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                return f"Frame from video"
            
            # Analyze image properties
            height, width = img.shape[:2]
            brightness = np.mean(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
            
            # Count dominant colors
            pixels = img.reshape(-1, 3)
            unique_colors = len(np.unique(pixels, axis=0))
            
            # Simple heuristic caption
            brightness_desc = "bright" if brightness > 127 else "dark"
            complexity_desc = "detailed" if unique_colors > 10000 else "simple"
            
            caption = f"A {brightness_desc} frame showing {complexity_desc} visual content"
            
            # Try to detect if there's text (high contrast edges)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 100, 200)
            edge_density = np.sum(edges > 0) / edges.size
            
            if edge_density > 0.1:
                caption += " with text or diagrams"
            
            logger.info(f"Generated basic caption: {caption}")
            return caption
            
        except Exception as e:
            logger.error(f"Error generating basic caption: {e}")
            return "Video keyframe"
            
    def generate_captions_batch(self, image_paths: List[str]) -> List[str]:
        """
        Generate captions for multiple images
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            List of caption texts
        """
        logger.info(f"Generating captions for {len(image_paths)} images")
        captions = []
        
        for i, image_path in enumerate(image_paths):
            logger.info(f"Processing image {i+1}/{len(image_paths)}")
            caption = self.generate_caption(image_path)
            captions.append(caption)
            
        return captions
