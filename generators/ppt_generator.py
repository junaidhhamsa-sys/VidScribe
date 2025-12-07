"""PowerPoint generation with improved professional layouts"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, PP_PARAGRAPH_ALIGNMENT
from pptx.dml.color import RGBColor
from pathlib import Path
import logging
from typing import List, Dict, Optional
from PIL import Image

from .ppt_templates import TEMPLATES
import config

logger = logging.getLogger(__name__)


class PPTGenerator:
    """Generate PowerPoint presentations with template support"""
    
    def __init__(self, template_name: str = None):
        """
        Initialize PPT Generator
        
        Args:
            template_name: Name of template to use (uses config default if None)
        """
        self.template_name = template_name or config.DEFAULT_TEMPLATE
        
        # Load template configuration
        if self.template_name not in TEMPLATES:
            logger.warning(f"Template '{self.template_name}' not found, using default")
            self.template_name = config.DEFAULT_TEMPLATE
        
        self.template = TEMPLATES[self.template_name]
        logger.info(f"PPT Generator initialized with template: {self.template['name']}")
    
    def create_presentation(self, slides_data: List[Dict], output_path: str,
                           title: str = None, subtitle: str = None) -> str:
        """
        Create PowerPoint presentation
        
        Args:
            slides_data: List of slide data dictionaries
            output_path: Path to save the presentation
            title: Presentation title (optional)
            subtitle: Presentation subtitle (optional)
            
        Returns:
            Path to created presentation
        """
        logger.info(f"Creating presentation with {len(slides_data)} slides using {self.template['name']} template")
        
        # Create presentation
        prs = Presentation()
        prs.slide_width = Inches(10)
        prs.slide_height = Inches(7.5)
        
        # Add title slide
        self._add_title_slide(prs, title, subtitle)
        
        # Add content slides
        for i, slide_data in enumerate(slides_data, 1):
            try:
                self._add_content_slide(prs, slide_data)
                logger.debug(f"Added slide {i}/{len(slides_data)}")
            except Exception as e:
                logger.error(f"Error adding slide {i}: {e}")
        
        # Save presentation
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        prs.save(output_path)
        logger.info(f"Presentation saved to {output_path}")
        
        return output_path
    
    def _add_title_slide(self, prs: Presentation, title: str = None, subtitle: str = None):
        """Add title slide with improved centering"""
        
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        self._apply_background(slide)
        
        layout = self.template['layout']['title_slide']
        
        # Title - centered and properly sized
        title_text = title or config.PPT_TITLE
        title_box = slide.shapes.add_textbox(
            Inches(0.5), layout['title_top'],
            Inches(9), layout['title_height']
        )
        
        title_frame = title_box.text_frame
        title_frame.text = title_text
        title_frame.word_wrap = True
        title_frame.vertical_anchor = 1  # Middle vertical alignment
        
        title_para = title_frame.paragraphs[0]
        title_para.alignment = layout['alignment']
        
        self._apply_font_style(title_para, self.template['fonts']['title'])
        
        # Subtitle - properly positioned
        subtitle_text = subtitle or config.PPT_SUBTITLE
        subtitle_box = slide.shapes.add_textbox(
            Inches(1), layout['subtitle_top'],
            Inches(8), layout['subtitle_height']
        )
        
        subtitle_frame = subtitle_box.text_frame
        subtitle_frame.text = subtitle_text
        subtitle_frame.word_wrap = True
        subtitle_frame.vertical_anchor = 1
        
        subtitle_para = subtitle_frame.paragraphs[0]
        subtitle_para.alignment = layout['alignment']
        
        self._apply_font_style(subtitle_para, self.template['fonts']['subtitle'])
    
    def _add_content_slide(self, prs: Presentation, slide_data: Dict):
        """Add content slide with improved layout"""
        
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        self._apply_background(slide)
        
        # Check if slide has image
        has_image = 'keyframe_path' in slide_data and slide_data['keyframe_path']
        
        if has_image and Path(slide_data['keyframe_path']).exists():
            layout = self.template['layout']['content_slide']
            self._add_slide_with_image(slide, slide_data, layout)
        else:
            layout = self.template['layout']['text_only_slide']
            self._add_text_only_slide(slide, slide_data, layout)
    
    def _add_slide_with_image(self, slide, slide_data: Dict, layout: Dict):
        """Add slide with image and text - IMPROVED"""
        
        # Add title with better positioning
        title_box = slide.shapes.add_textbox(
            Inches(0.5), layout['title_top'],
            Inches(9), layout['title_height']
        )
        
        title_frame = title_box.text_frame
        title_frame.text = slide_data.get('title', f"Slide {slide_data.get('number', '')}")
        title_frame.margin_left = Inches(0.1)
        title_frame.margin_right = Inches(0.1)
        title_frame.margin_top = Inches(0.05)
        title_frame.margin_bottom = Inches(0.05)
        title_frame.vertical_anchor = 1  # Center vertically
        
        title_para = title_frame.paragraphs[0]
        self._apply_font_style(title_para, self.template['fonts']['heading'])
        
        # Add image with proper scaling
        try:
            image_path = slide_data['keyframe_path']
            img = Image.open(image_path)
            img_width, img_height = img.size
            
            # Calculate best fit
            target_width = layout['image_width']
            target_height = layout['image_height']
            
            img_ratio = img_width / img_height
            target_ratio = target_width / target_height
            
            if img_ratio > target_ratio:
                actual_width = target_width
                actual_height = target_width / img_ratio
            else:
                actual_height = target_height
                actual_width = target_height * img_ratio
            
            # Center image
            image_left = layout['image_left'] + (target_width - actual_width) / 2
            image_top = layout['image_top'] + (target_height - actual_height) / 2
            
            slide.shapes.add_picture(
                image_path,
                image_left, image_top,
                width=actual_width, height=actual_height
            )
            
        except Exception as e:
            logger.error(f"Error adding image: {e}")
        
        # Add text content with IMPROVED formatting
        text_box = slide.shapes.add_textbox(
            layout['text_left'], layout['text_top'],
            layout['text_width'], layout['text_height']
        )
        
        text_frame = text_box.text_frame
        text_frame.word_wrap = True
        text_frame.margin_left = Inches(0.2)
        text_frame.margin_right = Inches(0.2)
        text_frame.margin_top = Inches(0.15)
        text_frame.margin_bottom = Inches(0.15)
        
        # Parse and add content as proper bullet points
        content = slide_data.get('content', '')
        if content:
            points = self._parse_content(content)
            
            for i, point in enumerate(points):
                if i > 0:
                    text_frame.add_paragraph()
                
                p = text_frame.paragraphs[i]
                p.text = point
                p.level = 0
                p.space_after = Pt(8)  # Space after each bullet
                p.line_spacing = 1.3  # Line spacing within bullet
                
                self._apply_font_style(p, self.template['fonts']['body'])
    
    def _add_text_only_slide(self, slide, slide_data: Dict, layout: Dict):
        """Add text-only slide with IMPROVED formatting"""
        
        # Add title
        title_box = slide.shapes.add_textbox(
            Inches(0.5), layout['title_top'],
            Inches(9), layout['title_height']
        )
        
        title_frame = title_box.text_frame
        title_frame.text = slide_data.get('title', f"Slide {slide_data.get('number', '')}")
        title_frame.margin_left = Inches(0.1)
        title_frame.margin_top = Inches(0.05)
        title_frame.vertical_anchor = 1
        
        title_para = title_frame.paragraphs[0]
        self._apply_font_style(title_para, self.template['fonts']['heading'])
        
        # Add content with proper bullet formatting
        content_box = slide.shapes.add_textbox(
            layout['content_left'], layout['content_top'],
            layout['content_width'], layout['content_height']
        )
        
        content_frame = content_box.text_frame
        content_frame.word_wrap = True
        content_frame.margin_left = Inches(0.3)
        content_frame.margin_right = Inches(0.3)
        content_frame.margin_top = Inches(0.2)
        content_frame.margin_bottom = Inches(0.2)
        
        content = slide_data.get('content', '')
        if content:
            points = self._parse_content(content)
            
            for i, point in enumerate(points):
                if i > 0:
                    content_frame.add_paragraph()
                
                p = content_frame.paragraphs[i]
                p.text = point
                p.level = 0
                p.space_after = Pt(12)  # More space for text-only
                p.line_spacing = 1.4
                
                self._apply_font_style(p, self.template['fonts']['body'])
    
    def _parse_content(self, content: str) -> List[str]:
        """Parse content into clean bullet points"""
        if not content:
            return []
        
        # Split by newlines
        lines = content.split('\n')
        
        # Clean and filter
        points = []
        for line in lines:
            line = line.strip()
            
            # Remove existing bullet markers
            if line.startswith(('- ', '• ', '* ', '→ ')):
                line = line[2:].strip()
            elif line.startswith(('1.', '2.', '3.', '4.', '5.')):
                line = line[2:].strip()
            
            # Add if not empty
            if line:
                # Capitalize first letter
                line = line[0].upper() + line[1:] if len(line) > 1 else line.upper()
                
                # Add period if missing
                if not line.endswith(('.', '!', '?', ':')):
                    line += '.'
                
                points.append(line)
        
        return points
    
    def _apply_background(self, slide):
        """Apply background styling to slide"""
        background = slide.background
        fill = background.fill
        fill.solid()
        
        color_name = self.template['background']['color']
        color = self.template['colors'][color_name]
        fill.fore_color.rgb = color
    
    def _apply_font_style(self, paragraph, font_config: Dict):
        """Apply font styling with improved settings"""
        
        font = paragraph.font
        font.name = font_config['name']
        font.size = font_config['size']
        font.bold = font_config['bold']
        
        # Set color
        color_name = font_config['color']
        color = self.template['colors'][color_name]
        font.color.rgb = color
        
        # Set paragraph alignment to left for better readability
        paragraph.alignment = PP_PARAGRAPH_ALIGNMENT.LEFT
    
    def get_template_info(self) -> Dict:
        """Get information about current template"""
        return {
            'name': self.template['name'],
            'description': self.template['description'],
            'id': self.template_name
        }


def get_available_templates() -> List[Dict]:
    """Get list of available templates"""
    return [
        {
            'id': template_id,
            'name': template['name'],
            'description': template['description']
        }
        for template_id, template in TEMPLATES.items()
    ]