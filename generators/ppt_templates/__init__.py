"""PowerPoint template configurations"""

from .professional import PROFESSIONAL_TEMPLATE
from .educational import EDUCATIONAL_TEMPLATE
from .minimalist import MINIMALIST_TEMPLATE
from .creative import CREATIVE_TEMPLATE
from .modern_tech import MODERN_TECH_TEMPLATE

# Template registry
TEMPLATES = {
    'professional': PROFESSIONAL_TEMPLATE,
    'educational': EDUCATIONAL_TEMPLATE,
    'minimalist': MINIMALIST_TEMPLATE,
    'creative': CREATIVE_TEMPLATE,
    'modern_tech': MODERN_TECH_TEMPLATE
}

__all__ = [
    'TEMPLATES',
    'PROFESSIONAL_TEMPLATE',
    'EDUCATIONAL_TEMPLATE',
    'MINIMALIST_TEMPLATE',
    'CREATIVE_TEMPLATE',
    'MODERN_TECH_TEMPLATE'
]