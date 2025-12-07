"""Modern Tech template - Dark mode with neon accents"""

from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

MODERN_TECH_TEMPLATE = {
    'name': 'Modern Tech',
    'description': 'Dark mode with neon accents',
    
    # Colors - Dark theme with neon
    'colors': {
        'primary': RGBColor(0, 255, 255),      # Cyan neon
        'secondary': RGBColor(255, 0, 255),    # Magenta neon
        'accent': RGBColor(57, 255, 20),       # Green neon
        'text': RGBColor(220, 220, 220),       # Light gray
        'background': RGBColor(20, 20, 30),    # Dark blue-black
        'subtitle': RGBColor(150, 150, 170)    # Purple-gray
    },
    
    # Typography - Modern tech fonts
    'fonts': {
        'title': {
            'name': 'Consolas',
            'size': Pt(50),
            'bold': True,
            'color': 'primary'
        },
        'subtitle': {
            'name': 'Segoe UI',
            'size': Pt(22),
            'bold': False,
            'color': 'subtitle'
        },
        'heading': {
            'name': 'Consolas',
            'size': Pt(34),
            'bold': True,
            'color': 'secondary'
        },
        'body': {
            'name': 'Segoe UI',
            'size': Pt(18),
            'bold': False,
            'color': 'text'
        },
        'caption': {
            'name': 'Segoe UI',
            'size': Pt(14),
            'bold': False,
            'color': 'accent'
        }
    },
    
    # Layout - Grid-based, compact
    'layout': {
        'title_slide': {
            'title_top': Inches(2.5),
            'title_height': Inches(1.5),
            'subtitle_top': Inches(4.5),
            'subtitle_height': Inches(1.0),
            'alignment': PP_ALIGN.LEFT
        },
        'content_slide': {
            'title_top': Inches(0.3),
            'title_height': Inches(0.8),
            'image_left': Inches(0.4),
            'image_top': Inches(1.3),
            'image_width': Inches(4.2),
            'image_height': Inches(5.8),
            'text_left': Inches(4.8),
            'text_top': Inches(1.5),
            'text_width': Inches(4.8),
            'text_height': Inches(5.4),
            'has_image': True
        },
        'text_only_slide': {
            'title_top': Inches(0.3),
            'title_height': Inches(0.8),
            'content_left': Inches(0.8),
            'content_top': Inches(1.5),
            'content_width': Inches(8.4),
            'content_height': Inches(5.5)
        }
    },
    
    'background': {
        'type': 'solid',
        'color': 'background'
    }
}