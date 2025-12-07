"""Minimalist template - Clean black & white"""

from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

MINIMALIST_TEMPLATE = {
    'name': 'Minimalist',
    'description': 'Simple black & white with lots of whitespace',
    
    # Colors - Monochrome
    'colors': {
        'primary': RGBColor(0, 0, 0),          # Black
        'secondary': RGBColor(255, 255, 255),  # White
        'accent': RGBColor(100, 100, 100),     # Dark gray
        'text': RGBColor(50, 50, 50),          # Charcoal
        'background': RGBColor(255, 255, 255), # White
        'subtitle': RGBColor(150, 150, 150)    # Light gray
    },
    
    # Typography - Clean sans-serif
    'fonts': {
        'title': {
            'name': 'Helvetica',
            'size': Pt(56),
            'bold': True,
            'color': 'primary'
        },
        'subtitle': {
            'name': 'Helvetica',
            'size': Pt(20),
            'bold': False,
            'color': 'subtitle'
        },
        'heading': {
            'name': 'Helvetica',
            'size': Pt(40),
            'bold': True,
            'color': 'primary'
        },
        'body': {
            'name': 'Helvetica',
            'size': Pt(16),
            'bold': False,
            'color': 'text'
        },
        'caption': {
            'name': 'Helvetica',
            'size': Pt(12),
            'bold': False,
            'color': 'subtitle'
        }
    },
    
    # Layout - Large images, minimal text
    'layout': {
        'title_slide': {
            'title_top': Inches(3.0),
            'title_height': Inches(1.5),
            'subtitle_top': Inches(4.8),
            'subtitle_height': Inches(0.8),
            'alignment': PP_ALIGN.LEFT
        },
        'content_slide': {
            'title_top': Inches(0.6),
            'title_height': Inches(0.7),
            'image_left': Inches(0.5),
            'image_top': Inches(1.5),
            'image_width': Inches(6.0),
            'image_height': Inches(5.5),
            'text_left': Inches(6.8),
            'text_top': Inches(2.0),
            'text_width': Inches(2.8),
            'text_height': Inches(4.5),
            'has_image': True
        },
        'text_only_slide': {
            'title_top': Inches(0.6),
            'title_height': Inches(0.7),
            'content_left': Inches(2.0),
            'content_top': Inches(2.5),
            'content_width': Inches(6.0),
            'content_height': Inches(4.0)
        }
    },
    
    'background': {
        'type': 'solid',
        'color': 'background'
    }
}