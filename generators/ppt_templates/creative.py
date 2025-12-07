"""Creative template - Vibrant and bold"""

from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

CREATIVE_TEMPLATE = {
    'name': 'Creative',
    'description': 'Vibrant gradients and bold typography',
    
    # Colors - Bold and vibrant
    'colors': {
        'primary': RGBColor(231, 76, 60),      # Red
        'secondary': RGBColor(46, 204, 113),   # Green
        'accent': RGBColor(155, 89, 182),      # Purple
        'text': RGBColor(44, 62, 80),          # Dark blue
        'background': RGBColor(236, 240, 241), # Light gray
        'subtitle': RGBColor(52, 152, 219)     # Blue
    },
    
    # Typography - Bold and expressive
    'fonts': {
        'title': {
            'name': 'Impact',
            'size': Pt(52),
            'bold': True,
            'color': 'primary'
        },
        'subtitle': {
            'name': 'Arial',
            'size': Pt(24),
            'bold': False,
            'color': 'subtitle'
        },
        'heading': {
            'name': 'Impact',
            'size': Pt(38),
            'bold': True,
            'color': 'accent'
        },
        'body': {
            'name': 'Arial',
            'size': Pt(19),
            'bold': False,
            'color': 'text'
        },
        'caption': {
            'name': 'Arial',
            'size': Pt(15),
            'bold': True,
            'color': 'secondary'
        }
    },
    
    # Layout - Mixed, creative positioning
    'layout': {
        'title_slide': {
            'title_top': Inches(2.0),
            'title_height': Inches(2.0),
            'subtitle_top': Inches(4.5),
            'subtitle_height': Inches(1.5),
            'alignment': PP_ALIGN.CENTER
        },
        'content_slide': {
            'title_top': Inches(0.4),
            'title_height': Inches(1.0),
            'image_left': Inches(0.3),
            'image_top': Inches(1.6),
            'image_width': Inches(5.0),
            'image_height': Inches(5.2),
            'text_left': Inches(5.5),
            'text_top': Inches(1.8),
            'text_width': Inches(4.2),
            'text_height': Inches(5.0),
            'has_image': True
        },
        'text_only_slide': {
            'title_top': Inches(0.4),
            'title_height': Inches(1.0),
            'content_left': Inches(1.0),
            'content_top': Inches(2.0),
            'content_width': Inches(8.0),
            'content_height': Inches(5.0)
        }
    },
    
    'background': {
        'type': 'solid',
        'color': 'background'
    }
}