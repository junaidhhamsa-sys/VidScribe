"""PowerPoint generation using python-pptx"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pathlib import Path
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class PPTGenerator:
    """Generate PowerPoint presentations from video summaries"""
    
    def __init__(self, title="Video Summary", subtitle="AI-Generated Summary"):
        """
        Initialize PPTGenerator
        
        Args:
            title: Presentation title
            subtitle: Presentation subtitle
        """
        self.title = title
        self.subtitle = subtitle
        
    def create_presentation(self, slides_data: List[Dict], keyframe_paths: List[str],
                           output_path: str, overall_summary: str = None) -> str:
        """
        Create PowerPoint presentation
        
        Args:
            slides_data: List of slide data dictionaries
            keyframe_paths: List of paths to keyframe images
            output_path: Path to save the presentation
            overall_summary: Optional overall summary text
            
        Returns:
            Path to created presentation
        """
        logger.info(f"Creating PowerPoint with {len(slides_data)} slides")
        
        prs = Presentation()
        prs.slide_width = Inches(10)
        prs.slide_height = Inches(7.5)
        
        # Title slide
        self._add_title_slide(prs, overall_summary)
        
        # Content slides
        for i, slide_data in enumerate(slides_data):
            image_path = keyframe_paths[i] if i < len(keyframe_paths) else None
            self._add_content_slide(prs, slide_data, image_path)
            
        # Save presentation
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        prs.save(output_path)
        logger.info(f"Presentation saved to {output_path}")
        
        return output_path
        
    def _add_title_slide(self, prs: Presentation, summary: str = None):
        """Add title slide"""
        slide_layout = prs.slide_layouts[0]  # Title slide layout
        slide = prs.slides.add_slide(slide_layout)
        
        # Set title
        title = slide.shapes.title
        title.text = self.title
        title.text_frame.paragraphs[0].font.size = Pt(44)
        title.text_frame.paragraphs[0].font.bold = True
        title.text_frame.paragraphs[0].font.color.rgb = RGBColor(44, 62, 80)
        
        # Set subtitle
        subtitle = slide.placeholders[1]
        if summary:
            subtitle.text = f"{self.subtitle}\n\n{summary[:200]}..."
        else:
            subtitle.text = self.subtitle
        subtitle.text_frame.paragraphs[0].font.size = Pt(20)
        subtitle.text_frame.paragraphs[0].font.color.rgb = RGBColor(52, 73, 94)
        
    def _add_content_slide(self, prs: Presentation, slide_data: Dict, image_path: str = None):
        """Add content slide with image and text"""
        
        # Use blank layout for custom positioning
        slide_layout = prs.slide_layouts[6]  # Blank layout
        slide = prs.slides.add_slide(slide_layout)
        
        # Add title
        title_box = slide.shapes.add_textbox(
            Inches(0.5), Inches(0.3), Inches(9), Inches(0.8)
        )
        title_frame = title_box.text_frame
        title_frame.text = slide_data.get('title', f"Slide {slide_data['number']}")
        title_para = title_frame.paragraphs[0]
        title_para.font.size = Pt(32)
        title_para.font.bold = True
        title_para.font.color.rgb = RGBColor(44, 62, 80)
        
        # Add image if available
        if image_path and Path(image_path).exists():
            try:
                # Image on the left side
                slide.shapes.add_picture(
                    image_path,
                    Inches(0.5), Inches(1.5),
                    width=Inches(4.5), height=Inches(5)
                )
            except Exception as e:
                logger.error(f"Error adding image to slide: {e}")
        
        # Add text content on the right side
        text_box = slide.shapes.add_textbox(
            Inches(5.2), Inches(1.5), Inches(4.2), Inches(5)
        )
        text_frame = text_box.text_frame
        text_frame.word_wrap = True
        
        # Add content text
        content = slide_data.get('content', '')
        if content:
            p = text_frame.paragraphs[0]
            p.text = content
            p.font.size = Pt(14)
            p.font.color.rgb = RGBColor(52, 73, 94)
            p.line_spacing = 1.2
        
        # Add timestamp if available
        if slide_data.get('timestamp') is not None:
            timestamp_box = slide.shapes.add_textbox(
                Inches(0.5), Inches(7), Inches(2), Inches(0.3)
            )
            timestamp_frame = timestamp_box.text_frame
            timestamp_frame.text = f"⏱ {self._format_timestamp(slide_data['timestamp'])}"
            timestamp_frame.paragraphs[0].font.size = Pt(10)
            timestamp_frame.paragraphs[0].font.color.rgb = RGBColor(149, 165, 166)
            
    def _format_timestamp(self, seconds: float) -> str:
        """Format timestamp as MM:SS"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
