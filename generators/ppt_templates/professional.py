"""Professional template - Clean corporate style"""

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
            'size': Pt(44),
            'bold': True,
            'color': 'primary'
        },
        'subtitle': {
            'name': 'Calibri',
            'size': Pt(24),
            'bold': False,
            'color': 'subtitle'
        },
        'heading': {
            'name': 'Calibri',
            'size': Pt(32),
            'bold': True,
            'color': 'primary'
        },
        'body': {
            'name': 'Calibri',
            'size': Pt(18),
            'bold': False,
            'color': 'text'
        },
        'caption': {
            'name': 'Calibri',
            'size': Pt(14),
            'bold': False,
            'color': 'subtitle'
        }
    },
    
    # Layout settings
    'layout': {
        'title_slide': {
            'title_top': Inches(2.5),
            'title_height': Inches(1.5),
            'subtitle_top': Inches(4.2),
            'subtitle_height': Inches(1.0),
            'alignment': PP_ALIGN.CENTER
        },
        'content_slide': {
            'title_top': Inches(0.5),
            'title_height': Inches(0.8),
            'image_left': Inches(0.5),
            'image_top': Inches(1.5),
            'image_width': Inches(4.5),
            'image_height': Inches(5.0),
            'text_left': Inches(5.2),
            'text_top': Inches(1.5),
            'text_width': Inches(4.3),
            'text_height': Inches(5.0),
            'has_image': True
        },
        'text_only_slide': {
            'title_top': Inches(0.5),
            'title_height': Inches(0.8),
            'content_left': Inches(1.0),
            'content_top': Inches(1.8),
            'content_width': Inches(8.0),
            'content_height': Inches(5.0)
        }
    },
    
    # Slide background
    'background': {
        'type': 'solid',
        'color': 'background'
    }
}