"""
Git-to-Image: Generate artistic portraits from GitHub profiles
"""

__version__ = "1.0.0"
__author__ = "Nano Banana Hackathon Team"

# Import the module functions, not classes
from . import github_analyzer
from . import style_guide  
from . import prompt_generator
from .image_generator import ImageGenerator

__all__ = ['github_analyzer', 'style_guide', 'prompt_generator', 'ImageGenerator']
