"""
Image generation module using Google Gemini
Based on the image_gen_sample.py reference
"""

import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
from io import BytesIO

try:
    from google import genai
    from PIL import Image
    IMAGING_AVAILABLE = True
except ImportError:
    IMAGING_AVAILABLE = False


class ImageGenerator:
    """Handles actual image generation using Gemini image API"""
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path("generated_images")
        self.output_dir.mkdir(exist_ok=True)
        
        # Check if API key is available
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.client = None
        
        if self.api_key and IMAGING_AVAILABLE:
            try:
                self.client = genai.Client(api_key=self.api_key)
                self.available = True
            except Exception:
                self.available = False
        else:
            self.available = False
    
    def generate_session_id(self) -> str:
        """Generate a unique session ID for this generation session"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"{timestamp}_{unique_id}"
    
    def generate_image(self, prompt: str, filename: str, session_id: str = None) -> Tuple[bool, str]:
        """
        Generate an image using Gemini image API
        
        Args:
            prompt: The text prompt for image generation
            filename: Base filename (without extension)
            session_id: Optional session ID, generates one if not provided
            
        Returns:
            Tuple of (success, filepath_or_error_message)
        """
        if not self.available:
            error_msg = "Image generation not available. "
            if not IMAGING_AVAILABLE:
                error_msg += "Missing packages: pip install google-genai Pillow"
            elif not self.api_key:
                error_msg += "Missing GEMINI_API_KEY environment variable"
            else:
                error_msg += "Failed to initialize Gemini client"
            return False, error_msg
        
        if session_id is None:
            session_id = self.generate_session_id()
        
        try:
            print(f"🎨 Generating image with Gemini (session: {session_id})...")
            print(f"📝 Prompt preview: {prompt[:100]}...")
            
            # Call the Gemini image generation API
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-image-preview",
                contents=prompt,
            )
            
            # Extract image data from response
            image_parts = [
                part.inline_data.data
                for part in response.candidates[0].content.parts
                if part.inline_data
            ]
            
            if not image_parts:
                return False, "No image data received from Gemini API"
            
            # Save the image
            image = Image.open(BytesIO(image_parts[0]))
            image_path = self.output_dir / f"{session_id}_{filename}.png"
            image.save(image_path)
            
            # Also save the prompt for reference
            prompt_path = self.output_dir / f"{session_id}_{filename}_prompt.txt"
            with open(prompt_path, 'w') as f:
                f.write(f"Session ID: {session_id}\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write(f"Filename: {filename}\n")
                f.write("=" * 50 + "\n\n")
                f.write(prompt)
            
            return True, str(image_path)
            
        except Exception as e:
            error_msg = f"Error generating image: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
    
    def generate_multiple_images(self, prompts: dict, base_filename: str, session_id: str = None) -> dict:
        """
        Generate multiple images from a set of prompts
        
        Args:
            prompts: Dict with keys like 'main_prompt', 'variations' etc.
            base_filename: Base filename for all images
            session_id: Optional session ID
            
        Returns:
            Dict of results with success status and file paths
        """
        if session_id is None:
            session_id = self.generate_session_id()
        
        results = {
            'session_id': session_id,
            'images': {},
            'success_count': 0,
            'total_count': 0
        }
        
        # Generate main image
        if 'main_prompt' in prompts:
            results['total_count'] += 1
            success, result = self.generate_image(
                prompts['main_prompt'], 
                f"{base_filename}_main", 
                session_id
            )
            results['images']['main'] = {
                'success': success,
                'result': result
            }
            if success:
                results['success_count'] += 1
        
        # Generate variations
        if 'variations' in prompts:
            for i, variation in enumerate(prompts['variations']):
                results['total_count'] += 1
                variation_prompt = variation.get('prompt', '')
                randomness = variation.get('randomness_level', 0)
                
                success, result = self.generate_image(
                    variation_prompt,
                    f"{base_filename}_var{i+1}_r{randomness}",
                    session_id
                )
                results['images'][f'variation_{i+1}'] = {
                    'success': success,
                    'result': result,
                    'randomness': randomness
                }
                if success:
                    results['success_count'] += 1
        
        return results

    # =============================================================================
    # PHASE 4: Multi-Style Generation
    # =============================================================================

    def generate_style_variations(self, profile, num_styles=4, session_id=None):
        """
        Generate multiple artistic style variations for the same developer profile.
        
        Args:
            profile: Developer profile with enhanced analysis
            num_styles: Number of different artistic styles to generate
            session_id: Optional session ID for organizing outputs
        
        Returns:
            dict: Results of multi-style generation with success metrics
        """
        if not self.available:
            return {
                'success': False,
                'error': 'Gemini API not available',
                'styles': {}
            }
        
        if session_id is None:
            session_id = self.generate_session_id()
        
        # Import here to avoid circular imports
        from .prompt_generator import generate_multi_style_prompts
        
        # Generate prompts for different artistic styles
        style_prompts = generate_multi_style_prompts(profile, num_styles)
        
        results = {
            'success': True,
            'session_id': session_id,
            'username': profile.get('username', 'unknown'),
            'developer_category': style_prompts[0].get('dev_category', 'general') if style_prompts else 'general',
            'styles': {},
            'success_count': 0,
            'total_styles': len(style_prompts)
        }
        
        print(f"🎨 Generating {len(style_prompts)} artistic style variations for {profile.get('username', 'developer')}...")
        
        for style_data in style_prompts:
            style_name = style_data['style_name']
            prompt = style_data['prompt']
            variation_num = style_data['variation']
            
            # Generate filename for this style
            safe_username = "".join(c for c in profile.get('username', 'dev') if c.isalnum() or c in '-_')
            safe_style = "".join(c for c in style_name.lower().replace(' ', '_') if c.isalnum() or c in '-_')
            filename = f"{safe_username}_{safe_style}"
            
            print(f"   🖼️  Generating {style_name} style...")
            
            success, result = self.generate_image(
                prompt=prompt,
                filename=filename,
                session_id=session_id
            )
            
            results['styles'][style_name] = {
                'success': success,
                'result': result,
                'variation_number': variation_num,
                'developer_category': style_data.get('dev_category', 'general'),
                'prompt_length': len(prompt)
            }
            
            if success:
                results['success_count'] += 1
                print(f"   ✅ {style_name} completed: {result}")
            else:
                print(f"   ❌ {style_name} failed: {result}")
        
        # Print summary
        if results['success_count'] > 0:
            print(f"🎉 Generated {results['success_count']}/{results['total_styles']} style variations successfully!")
        else:
            print(f"❌ Failed to generate any style variations")
            results['success'] = False
        
        return results

    def batch_generate_images(self, profiles, style_options=None):
        """
        Efficiently generate images for multiple developer profiles.
        
        Args:
            profiles: List of developer profiles
            style_options: Dict with style generation preferences
        
        Returns:
            dict: Batch generation results
        """
        if not self.available:
            return {
                'success': False,
                'error': 'Gemini API not available',
                'profiles': {}
            }
        
        style_options = style_options or {'num_styles': 4, 'include_variations': False}
        batch_session_id = self.generate_session_id()
        
        results = {
            'success': True,
            'batch_session_id': batch_session_id,
            'profiles': {},
            'total_profiles': len(profiles),
            'successful_profiles': 0,
            'total_images_generated': 0
        }
        
        print(f"🚀 Starting batch generation for {len(profiles)} profiles...")
        
        for i, profile in enumerate(profiles, 1):
            username = profile.get('username', f'user_{i}')
            print(f"\n📊 Processing profile {i}/{len(profiles)}: {username}")
            
            # Generate style variations for this profile
            if style_options.get('multi_style', True):
                profile_results = self.generate_style_variations(
                    profile=profile,
                    num_styles=style_options.get('num_styles', 4),
                    session_id=f"{batch_session_id}_{username}"
                )
            else:
                # Generate single image with variations
                profile_results = self.generate_with_variations(
                    profile=profile,
                    num_variations=style_options.get('num_variations', 3),
                    randomness_range=style_options.get('randomness_range', (0.1, 0.3)),
                    session_id=f"{batch_session_id}_{username}"
                )
            
            results['profiles'][username] = profile_results
            
            if profile_results.get('success', False):
                results['successful_profiles'] += 1
                if 'success_count' in profile_results:
                    results['total_images_generated'] += profile_results['success_count']
        
        # Print batch summary
        success_rate = (results['successful_profiles'] / results['total_profiles']) * 100
        print(f"\n🎯 Batch Complete: {results['successful_profiles']}/{results['total_profiles']} profiles successful ({success_rate:.1f}%)")
        print(f"📈 Total images generated: {results['total_images_generated']}")
        
        return results

    def apply_style_template(self, base_prompt, style_category):
        """
        Apply predefined style templates to base prompts.
        
        Args:
            base_prompt: Base prompt string
            style_category: Style category ('legendary', 'frontend', 'backend', 'professional')
        
        Returns:
            str: Enhanced prompt with style template applied
        """
        style_templates = {
            'legendary': {
                'prefix': 'Epic heroic portrait,',
                'style_modifiers': 'legendary proportions, aura of mastery',
                'color_scheme': 'rich golds and deep blues',
                'lighting': 'dramatic cinematic lighting'
            },
            'frontend': {
                'prefix': 'Modern creative portrait,',
                'style_modifiers': 'vibrant and user-friendly aesthetic',
                'color_scheme': 'bright modern UI colors with gradients',
                'lighting': 'clean contemporary lighting'
            },
            'backend': {
                'prefix': 'Technical focused portrait,',
                'style_modifiers': 'systematic and powerful presence',
                'color_scheme': 'monochromatic with terminal green accents',
                'lighting': 'industrial dramatic lighting'
            },
            'professional': {
                'prefix': 'Professional portrait,',
                'style_modifiers': 'corporate and polished appearance',
                'color_scheme': 'professional color palette',
                'lighting': 'professional studio lighting'
            }
        }
        
        template = style_templates.get(style_category, style_templates['professional'])
        
        enhanced_prompt = f"{template['prefix']} {base_prompt}"
        enhanced_prompt += f"\n\nStyle Enhancement: {template['style_modifiers']}"
        enhanced_prompt += f"\nColor Scheme: {template['color_scheme']}"
        enhanced_prompt += f"\nLighting: {template['lighting']}"
        
        return enhanced_prompt
