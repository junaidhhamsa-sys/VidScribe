"""Educational template - Friendly learning style"""

from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

EDUCATIONAL_TEMPLATE = {
    'name': 'Educational',
    'description': 'Friendly learning style with warm colors',
    
    # Colors - Warm and inviting
    'colors': {
        'primary': RGBColor(230, 126, 34),     # Orange
        'secondary': RGBColor(255, 255, 255),  # White
        'accent': RGBColor(241, 196, 15),      # Yellow
        'text': RGBColor(52, 73, 94),          # Dark blue-gray
        'background': RGBColor(253, 245, 230), # Light cream
        'subtitle': RGBColor(149, 165, 166)    # Gray
    },
    
    # Typography - Friendly fonts
    'fonts': {
        'title': {
            'name': 'Arial Rounded MT Bold',
            'size': Pt(48),
            'bold': True,
            'color': 'primary'
        },
        'subtitle': {
            'name': 'Arial',
            'size': Pt(22),
            'bold': False,
            'color': 'text'
        },
        'heading': {
            'name': 'Arial Rounded MT Bold',
            'size': Pt(36),
            'bold': True,
            'color': 'primary'
        },
        'body': {
            'name': 'Arial',
            'size': Pt(20),
            'bold': False,
            'color': 'text'
        },
        'caption': {
            'name': 'Arial',
            'size': Pt(16),
            'bold': False,
            'color': 'subtitle'
        }
    },
    
    # Layout - Image on top, text below
    'layout': {
        'title_slide': {
            'title_top': Inches(2.5),
            'title_height': Inches(1.5),
            'subtitle_top': Inches(4.3),
            'subtitle_height': Inches(1.2),
            'alignment': PP_ALIGN.CENTER
        },
        'content_slide': {
            'title_top': Inches(0.5),
            'title_height': Inches(0.9),
            'image_left': Inches(2.0),
            'image_top': Inches(1.6),
            'image_width': Inches(6.0),
            'image_height': Inches(3.5),
            'text_left': Inches(0.8),
            'text_top': Inches(5.3),
            'text_width': Inches(8.4),
            'text_height': Inches(1.8),
            'has_image': True
        },
        'text_only_slide': {
            'title_top': Inches(0.5),
            'title_height': Inches(0.9),
            'content_left': Inches(1.2),
            'content_top': Inches(2.0),
            'content_width': Inches(7.6),
            'content_height': Inches(4.5)
        }
    },
    
    'background': {
        'type': 'solid',
        'color': 'background'
    }
}