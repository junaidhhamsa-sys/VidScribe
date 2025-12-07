"""Professional template - Clean corporate style - IMPROVED"""

from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

PROFESSIONAL_TEMPLATE = {
    'name': 'Professional',
    'description': 'Clean corporate style with navy blue theme',
    
    # Colors
    'colors': {
        'primary': RGBColor(0, 51, 102),      # Navy blue
        'secondary': RGBColor(255, 255, 255),  # White
        'accent': RGBColor(0, 112, 192),       # Light blue
        'text': RGBColor(44, 62, 80),          # Dark gray
        'background': RGBColor(255, 255, 255), # White
        'subtitle': RGBColor(127, 140, 141)    # Medium gray
    },
    
    # Typography
    'fonts': {
        'title': {
            'name': 'Calibri',
            'size': Pt(40),
            'bold': True,
            'color': 'primary'
        },
        'subtitle': {
            'name': 'Calibri',
            'size': Pt(20),
            'bold': False,
            'color': 'subtitle'
        },
        'heading': {
            'name': 'Calibri',
            'size': Pt(28),
            'bold': True,
            'color': 'primary'
        },
        'body': {
            'name': 'Calibri',
            'size': Pt(16),
            'bold': False,
            'color': 'text'
        },
        'caption': {
            'name': 'Calibri',
            'size': Pt(12),
            'bold': False,
            'color': 'subtitle'
        }
    },
    
    # Layout settings - IMPROVED spacing
    'layout': {
        'title_slide': {
            'title_top': Inches(2.5),
            'title_height': Inches(1.5),
            'subtitle_top': Inches(4.2),
            'subtitle_height': Inches(1.5),
            'alignment': PP_ALIGN.CENTER
        },
        'content_slide': {
            'title_top': Inches(0.3),
            'title_height': Inches(0.7),
            'image_left': Inches(0.4),
            'image_top': Inches(1.2),
            'image_width': Inches(4.5),
            'image_height': Inches(5.8),
            'text_left': Inches(5.1),
            'text_top': Inches(1.2),
            'text_width': Inches(4.5),
            'text_height': Inches(5.8),
            'has_image': True
        },
        'text_only_slide': {
            'title_top': Inches(0.3),
            'title_height': Inches(0.7),
            'content_left': Inches(0.8),
            'content_top': Inches(1.5),
            'content_width': Inches(8.4),
            'content_height': Inches(5.5)
        }
    },
    
    # Slide background
    'background': {
        'type': 'solid',
        'color': 'background'
    }
}