# git_to_image/image_to_image_generator.py
# Module for image-to-image generation using GitHub profile pictures

import os
import base64
import mimetypes
from datetime import datetime
from google import genai
from google.genai import types


class ImageToImageGenerator:
    """Handles image-to-image generation using Gemini 2.5 Flash Image Preview"""
    
    def __init__(self):
        """Initialize the image-to-image generator"""
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.available = bool(self.api_key)
        self.model = "gemini-2.5-flash-image-preview"
        
        if self.available:
            self.client = genai.Client(api_key=self.api_key)
            print("✅ Gemini Image-to-Image Generator initialized")
        else:
            print("❌ GEMINI_API_KEY not found. Image-to-image generation will be unavailable.")
    
    def generate_session_id(self):
        """Generate a unique session ID for organizing outputs"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Add a short random component
        import secrets
        random_component = secrets.token_hex(4)
        return f"{timestamp}_{random_component}"
    
    def save_binary_file(self, file_name, data):
        """Save binary image data to file"""
        try:
            with open(file_name, "wb") as f:
                f.write(data)
            print(f"✅ File saved to: {file_name}")
            return True
        except Exception as e:
            print(f"❌ Error saving file {file_name}: {str(e)}")
            return False
    
    def generate_profile_based_portrait(self, profile, image_path, style_mode='fusion', session_id=None):
        """
        Generate portrait using profile picture as input with coding style overlay.
        
        Args:
            profile: Developer profile with analysis data
            image_path: Path to the profile picture
            style_mode: Generation mode ('fusion', 'enhancement', 'style_transfer', 'character')
            session_id: Optional session ID for organizing outputs
            
        Returns:
            dict: Generation results with success status and file paths
        """
        if not self.available:
            return {
                'success': False,
                'error': 'Gemini API not available'
            }
        
        if session_id is None:
            session_id = self.generate_session_id()
        
        try:
            # Import here to avoid circular imports
            from .prompt_generator import generate_image_to_image_prompt
            
            # Generate the appropriate prompt for the style mode
            prompt = generate_image_to_image_prompt(profile, style_mode)
            
            # Read and validate the image
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
            
            mime_type = mimetypes.guess_type(image_path)[0]
            
            # Create the content for Gemini
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=prompt),
                        types.Part.from_bytes(
                            data=image_data,
                            mime_type=mime_type
                        ),
                    ],
                ),
            ]
            
            generate_content_config = types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            )
            
            # Generate filename
            username = profile.get('username', 'user')
            safe_username = "".join(c for c in username if c.isalnum() or c in '-_')
            base_filename = f"{session_id}_{safe_username}_{style_mode}"
            
            # Create output directory
            output_dir = 'generated_images'
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            print(f"🎨 Generating {style_mode} portrait for {username} (session: {session_id})...")
            print(f"📝 Using profile picture: {os.path.basename(image_path)}")
            
            # Stream generation and save results
            file_index = 0
            generated_files = []
            generation_text = []
            
            for chunk in self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=generate_content_config,
            ):
                if (
                    chunk.candidates is None
                    or chunk.candidates[0].content is None
                    or chunk.candidates[0].content.parts is None
                ):
                    continue
                
                # Handle image data
                if (chunk.candidates[0].content.parts[0].inline_data and 
                    chunk.candidates[0].content.parts[0].inline_data.data):
                    
                    inline_data = chunk.candidates[0].content.parts[0].inline_data
                    data_buffer = inline_data.data
                    file_extension = mimetypes.guess_extension(inline_data.mime_type) or '.png'
                    
                    output_filename = f"{base_filename}_{file_index}{file_extension}"
                    output_path = os.path.join(output_dir, output_filename)
                    
                    if self.save_binary_file(output_path, data_buffer):
                        generated_files.append(output_path)
                        file_index += 1
                
                # Collect text responses instead of printing immediately
                elif chunk.text:
                    generation_text.append(chunk.text)
            
            # Print collected generation text if any
            if generation_text:
                full_text = ''.join(generation_text)
                print(f"📝 Generation response: {full_text}")
            
            # Save the prompt used
            prompt_filename = f"{base_filename}_prompt.txt"
            prompt_path = os.path.join(output_dir, prompt_filename)
            
            with open(prompt_path, 'w') as f:
                f.write(f"Session ID: {session_id}\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write(f"Style Mode: {style_mode}\n")
                f.write(f"Input Image: {os.path.basename(image_path)}\n")
                f.write(f"Username: {username}\n")
                f.write("=" * 50 + "\n\n")
                f.write(prompt)
            
            if generated_files:
                return {
                    'success': True,
                    'session_id': session_id,
                    'style_mode': style_mode,
                    'generated_files': generated_files,
                    'prompt_file': prompt_path,
                    'input_image': image_path
                }
            else:
                return {
                    'success': False,
                    'error': 'No images were generated'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Generation failed: {str(e)}'
            }
    
    def create_character_fusion(self, profile, image_path, session_id=None):
        """
        Blend user photo with their coding archetype.
        
        Args:
            profile: Developer profile with analysis data
            image_path: Path to the profile picture
            session_id: Optional session ID for organizing outputs
            
        Returns:
            dict: Generation results
        """
        return self.generate_profile_based_portrait(
            profile=profile,
            image_path=image_path,
            style_mode='character_fusion',
            session_id=session_id
        )
    
    def apply_artistic_transformation(self, profile, image_path, artistic_style=None, session_id=None):
        """
        Transform profile picture using artistic style from profile analysis.
        
        Args:
            profile: Developer profile with analysis data
            image_path: Path to the profile picture
            artistic_style: Override artistic style (optional)
            session_id: Optional session ID for organizing outputs
            
        Returns:
            dict: Generation results
        """
        return self.generate_profile_based_portrait(
            profile=profile,
            image_path=image_path,
            style_mode='artistic_transformation',
            session_id=session_id
        )
    
    def enhance_with_tech_elements(self, profile, image_path, session_id=None):
        """
        Add subtle programming-related visual elements to the portrait.
        
        Args:
            profile: Developer profile with analysis data
            image_path: Path to the profile picture
            session_id: Optional session ID for organizing outputs
            
        Returns:
            dict: Generation results
        """
        return self.generate_profile_based_portrait(
            profile=profile,
            image_path=image_path,
            style_mode='tech_enhancement',
            session_id=session_id
        )
    
    def generate_multiple_transformations(self, profile, image_path, modes=None, session_id=None):
        """
        Generate multiple transformation modes for the same profile picture.
        
        Args:
            profile: Developer profile with analysis data
            image_path: Path to the profile picture
            modes: List of transformation modes to generate
            session_id: Optional session ID for organizing outputs
            
        Returns:
            dict: Results for all transformation modes
        """
        if modes is None:
            modes = ['tech_enhancement', 'character_fusion', 'artistic_transformation']
        
        if session_id is None:
            session_id = self.generate_session_id()
        
        results = {
            'success': True,
            'session_id': session_id,
            'username': profile.get('username', 'unknown'),
            'input_image': image_path,
            'transformations': {},
            'success_count': 0,
            'total_modes': len(modes)
        }
        
        username = profile.get('username', 'developer')
        print(f"🎨 Generating {len(modes)} transformation modes for {username}...")
        
        for mode in modes:
            print(f"   🖼️  Generating {mode} transformation...")
            
            mode_result = self.generate_profile_based_portrait(
                profile=profile,
                image_path=image_path,
                style_mode=mode,
                session_id=session_id
            )
            
            results['transformations'][mode] = mode_result
            
            if mode_result.get('success', False):
                results['success_count'] += 1
                print(f"   ✅ {mode} completed")
            else:
                print(f"   ❌ {mode} failed: {mode_result.get('error', 'Unknown error')}")
        
        # Print summary
        if results['success_count'] > 0:
            print(f"🎉 Generated {results['success_count']}/{results['total_modes']} transformations successfully!")
        else:
            print(f"❌ Failed to generate any transformations")
            results['success'] = False
        
        return results
