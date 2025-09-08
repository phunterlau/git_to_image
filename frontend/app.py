#!/usr/bin/env python3
"""
Git-to-Image Streamlit UI
A retro Nintendo-style web interface for generating artistic portraits from GitHub profiles
"""

import streamlit as st
import sys
import os
from pathlib import Path
import json
from typing import Optional, Dict, Any

# Add the parent directory to the path to import git_to_image modules
sys.path.append(str(Path(__file__).parent.parent))

from git_to_image import github_analyzer, prompt_generator
from git_to_image.image_generator import ImageGenerator
from git_to_image.image_to_image_generator import ImageToImageGenerator

# Page configuration
st.set_page_config(
    page_title="Git-to-Image Generator",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Nintendo-style theme
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
    
    .main-header {
        font-family: 'Press Start 2P', cursive;
        color: #00FF00;
        text-align: center;
        font-size: 24px;
        margin-bottom: 30px;
        text-shadow: 2px 2px 0px #000000;
        background: linear-gradient(45deg, #1a1a2e, #16213e);
        padding: 20px;
        border: 3px solid #00FF00;
        border-radius: 10px;
    }
    
    .pixel-button {
        font-family: 'Press Start 2P', cursive;
        background: #FF6B6B;
        color: white;
        border: 3px solid #000;
        padding: 10px 20px;
        font-size: 12px;
        cursor: pointer;
        text-transform: uppercase;
    }
    
    .pixel-button:hover {
        background: #FF5252;
        transform: scale(1.05);
    }
    
    .retro-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: 3px solid #000;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    
    .profile-summary {
        font-family: 'Press Start 2P', cursive;
        font-size: 10px;
        background: #000;
        color: #00FF00;
        padding: 15px;
        border-radius: 5px;
        border: 2px solid #00FF00;
    }
    
    .stSelectbox label, .stTextInput label, .stRadio label, .stCheckbox label {
        font-family: 'Press Start 2P', cursive;
        font-size: 12px;
        color: #FF6B6B;
    }
    
    .stTextInput input, .stSelectbox select, .stRadio div, .stCheckbox div {
        font-family: 'Press Start 2P', cursive;
        font-size: 10px;
        background: #000;
        color: #00FF00;
        border: 2px solid #00FF00;
        border-radius: 5px;
        padding: 8px;
    }
    
    .stTextInput input::placeholder {
        font-family: 'Press Start 2P', cursive;
        color: #666;
        font-size: 8px;
    }
    
    .stButton button {
        font-family: 'Press Start 2P', cursive;
        background: #FF6B6B;
        color: white;
        border: 3px solid #000;
        padding: 15px 25px;
        font-size: 12px;
        text-transform: uppercase;
        border-radius: 8px;
    }
    
    .stButton button:hover {
        background: #FF5252;
        transform: scale(1.05);
        box-shadow: 0 0 10px #FF6B6B;
    }
    
    .stExpander summary {
        font-family: 'Press Start 2P', cursive;
        font-size: 12px;
        color: #00FF00;
    }
    
    .stDownloadButton button {
        font-family: 'Press Start 2P', cursive;
        background: #4CAF50;
        color: white;
        border: 3px solid #000;
        padding: 10px 20px;
        font-size: 10px;
        text-transform: uppercase;
        border-radius: 5px;
    }
    
    .stDownloadButton button:hover {
        background: #45a049;
        transform: scale(1.05);
    }
    
    .loading-text {
        font-family: 'Press Start 2P', cursive;
        color: #00FF00;
        font-size: 14px;
        text-align: center;
    }
    
    /* Apply Nintendo font to all text elements */
    h1, h2, h3, h4, h5, h6, p, div, span, .stMarkdown {
        font-family: 'Press Start 2P', cursive !important;
    }
    
    .stMarkdown h3 {
        color: #FF6B6B;
        font-size: 14px;
        text-shadow: 1px 1px 0px #000000;
    }
    
    .stMarkdown h4 {
        color: #00FF00;
        font-size: 12px;
        text-shadow: 1px 1px 0px #000000;
    }
    
    .stSuccess, .stError, .stWarning, .stInfo {
        font-family: 'Press Start 2P', cursive;
        font-size: 10px;
    }
    
    .stAlert {
        font-family: 'Press Start 2P', cursive;
        border: 2px solid;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

class GitToImageUI:
    def __init__(self):
        self.output_dir = Path("generated_images")
        self.profile_dir = Path("user_profile")
        self.image_generator = ImageGenerator(self.output_dir)
        self.image_to_image_generator = ImageToImageGenerator()
        
        # Ensure directories exist
        self.output_dir.mkdir(exist_ok=True)
        self.profile_dir.mkdir(exist_ok=True)
    
    def load_existing_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """Load existing profile if it exists"""
        profile_path = self.profile_dir / f"{username}_profile.json"
        if profile_path.exists():
            try:
                with open(profile_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return None
        return None
    
    def display_profile_summary(self, profile: Dict[str, Any]):
        """Display profile summary in retro style"""
        with st.expander("📊 Developer Profile Analysis", expanded=False):
            st.markdown('<div class="profile-summary">', unsafe_allow_html=True)
            
            username = profile.get('username', 'Unknown')
            st.write(f"👤 DEVELOPER: {username.upper()}")
            
            # Languages
            if 'language_profile' in profile:
                lang_profile = profile['language_profile']
                if lang_profile:
                    top_lang = max(lang_profile.items(), key=lambda x: x[1])
                    st.write(f"💻 PRIMARY LANG: {top_lang[0]} ({top_lang[1]:.1f}%)")
            
            # Domain focus
            if 'domain_focus' in profile:
                domain_focus = profile['domain_focus']
                if isinstance(domain_focus, dict):
                    domain = domain_focus.get('primary_domain', 'Unknown')
                elif isinstance(domain_focus, list) and domain_focus:
                    domain = ', '.join(domain_focus)
                else:
                    domain = 'Unknown'
                st.write(f"🎯 FOCUS: {domain.upper()}")
            
            # Contribution style
            if 'contribution_style' in profile:
                contrib_style = profile['contribution_style']
                if isinstance(contrib_style, dict):
                    style = contrib_style.get('style', 'Unknown')
                else:
                    style = contrib_style
                st.write(f"⚡ STYLE: {style.upper()}")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    def render_ui(self):
        """Render the main UI"""
        load_css()
        
        # Header
        st.markdown('<div class="main-header">🎮 CODE PORTRAIT ARCADE 🎮</div>', 
                   unsafe_allow_html=True)
        
        # Main container
        with st.container():
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown('<div class="retro-container">', unsafe_allow_html=True)
                st.markdown("### 🕹️ PLAYER CONFIG")
                
                # Username input
                username = st.text_input("GitHub Username", placeholder="Enter username...")
                
                # Generation mode
                generation_mode = st.radio(
                    "Generation Mode",
                    ["Text-to-Image", "Image-to-Image"],
                    help="Choose between text-based or profile picture-based generation"
                )
                
                # Dynamic options based on mode
                if generation_mode == "Text-to-Image":
                    st.markdown("#### 🎨 PORTRAIT MODE")
                    
                    use_auto_mode = st.radio(
                        "Generation Style",
                        ["🍀 I feel lucky (Let AI decide)", "🎯 Custom options"],
                        help="Choose automatic generation or customize your options"
                    )
                    
                    if use_auto_mode == "🎯 Custom options":
                        artistic_style = st.selectbox(
                            "Artistic Style",
                            ["Vibrant pop art", "Minimalist design", "Dark cyberpunk", 
                             "1980s retro wave", "Futuristic cyberpunk", "Chinese ink wash painting",
                             "Steampunk mechanical", "Dark fantasy concept art"]
                        )
                        
                        character_archetype = st.selectbox(
                            "Character Archetype",
                            ["Majestic Bear", "Wise Owl", "Industrious Beaver", "Cunning Fox",
                             "Agile Octopus", "Loyal Wolf", "Meticulous Hummingbird", 
                             "Playful Otter", "GitHub Octopus"]
                        )
                        
                        background_env = st.selectbox(
                            "Background Environment",
                            ["A server room with glowing racks", "A digital forest with flowing data streams",
                             "A library of ancient code scrolls", "A futuristic city skyline",
                             "A workshop filled with gears and circuits", 
                             "An abstract representation of a neural network"]
                        )
                    else:
                        # Set defaults for "I feel lucky" mode
                        artistic_style = None
                        character_archetype = None
                        background_env = None
                
                else:  # Image-to-Image
                    st.markdown("#### 🖼️ REMIX MODE")
                    
                    transformation_mode = st.selectbox(
                        "Transformation Mode",
                        ["Portrait Enhancement", "Character Fusion", "Style Transfer", "Technical Overlay"],
                        help="Choose how to transform the profile picture"
                    )
                    
                    privacy_consent = st.checkbox(
                        "I consent to downloading and using the GitHub profile picture",
                        help="Required for image-to-image generation"
                    )
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="retro-container">', unsafe_allow_html=True)
                st.markdown("### 🎯 GAME START")
                
                # Generate button
                generate_clicked = st.button("🚀 GENERATE PORTRAIT", type="primary")
                
                # Status area
                status_placeholder = st.empty()
                
                # Results area
                if generate_clicked and username:
                    self.handle_generation(
                        username, generation_mode, status_placeholder,
                        artistic_style if generation_mode == "Text-to-Image" else None,
                        character_archetype if generation_mode == "Text-to-Image" else None,
                        background_env if generation_mode == "Text-to-Image" else None,
                        transformation_mode if generation_mode == "Image-to-Image" else None,
                        privacy_consent if generation_mode == "Image-to-Image" else True,
                        use_auto_mode if generation_mode == "Text-to-Image" else None
                    )
                elif generate_clicked:
                    st.error("⚠️ Please enter a GitHub username!")
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    def handle_generation(self, username: str, mode: str, status_placeholder, 
                         artistic_style=None, character_archetype=None, background_env=None,
                         transformation_mode=None, privacy_consent=True, use_auto_mode=None):
        """Handle the image generation process"""
        
        if mode == "Image-to-Image" and not privacy_consent:
            st.error("⚠️ Privacy consent required for image-to-image generation!")
            return
        
        try:
            # Check for existing profile
            with status_placeholder:
                st.markdown('<div class="loading-text">🔍 LOADING PROFILE...</div>', 
                           unsafe_allow_html=True)
            
            profile = self.load_existing_profile(username)
            
            if not profile:
                with status_placeholder:
                    st.markdown('<div class="loading-text">📊 ANALYZING GITHUB PROFILE...</div>', 
                               unsafe_allow_html=True)
                
                # Check for required environment variables
                github_token = os.getenv('GITHUB_TOKEN')
                gemini_api_key = os.getenv('GEMINI_API_KEY')
                
                if not github_token:
                    st.error("❌ GITHUB_TOKEN environment variable not set!")
                    return
                
                if not gemini_api_key:
                    st.error("❌ GEMINI_API_KEY environment variable not set!")
                    return
                
                profile = github_analyzer.analyze_user_profile(username, github_token, gemini_api_key)
                
                if not profile:
                    st.error(f"❌ Failed to analyze GitHub profile for {username}")
                    return
            
            # Display profile summary
            self.display_profile_summary(profile)
            
            # Generate image based on mode
            if mode == "Text-to-Image":
                self.generate_text_to_image(profile, username, status_placeholder, use_auto_mode)
            else:
                self.generate_image_to_image(profile, username, transformation_mode, status_placeholder)
                
        except Exception as e:
            st.error(f"❌ Error during generation: {str(e)}")
    
    def generate_text_to_image(self, profile: Dict[str, Any], username: str, status_placeholder, use_auto_mode=None):
        """Generate image using text-to-image mode"""
        with status_placeholder:
            if use_auto_mode == "🍀 I feel lucky (Let AI decide)":
                st.markdown('<div class="loading-text">🍀 FEELING LUCKY... GENERATING PORTRAIT...</div>', 
                           unsafe_allow_html=True)
            else:
                st.markdown('<div class="loading-text">🎨 GENERATING PORTRAIT...</div>', 
                           unsafe_allow_html=True)
        
        if 'image_prompts' not in profile:
            st.error("❌ No image prompts found in profile!")
            return
        
        # Use the main prompt for generation (backend decides all options)
        prompt = profile['image_prompts']['main_prompt']
        session_id = self.image_generator.generate_session_id()
        filename = f"{username}_ui_generated"
        
        success, result = self.image_generator.generate_image(prompt, filename, session_id)
        
        if success:
            if use_auto_mode == "🍀 I feel lucky (Let AI decide)":
                st.success("🍀 LUCKY PORTRAIT GENERATED SUCCESSFULLY!")
            else:
                st.success("✅ PORTRAIT GENERATED SUCCESSFULLY!")
            
            # Display the generated image
            if os.path.exists(result):
                st.image(result, caption=f"Generated portrait for {username}", use_container_width=True)
                
                # Download button
                with open(result, "rb") as file:
                    st.download_button(
                        label="💾 DOWNLOAD IMAGE",
                        data=file.read(),
                        file_name=f"{username}_portrait.png",
                        mime="image/png"
                    )
            else:
                st.warning("⚠️ Image file not found, but generation reported success")
        else:
            st.error(f"❌ Image generation failed: {result}")
    
    def generate_image_to_image(self, profile: Dict[str, Any], username: str, 
                               transformation_mode: str, status_placeholder):
        """Generate image using image-to-image mode"""
        
        # Check if image-to-image generator is available
        if not self.image_to_image_generator.available:
            st.error("❌ Image-to-Image generation not available. Check GEMINI_API_KEY.")
            return
        
        try:
            # Step 1: Download profile picture
            with status_placeholder:
                st.markdown('<div class="loading-text">📸 DOWNLOADING PROFILE PICTURE...</div>', 
                           unsafe_allow_html=True)
            
            picture_result = github_analyzer.get_github_profile_picture(username)
            
            if not picture_result['success']:
                st.error(f"❌ Failed to get profile picture: {picture_result['error']}")
                return
            
            image_path = picture_result['image_path']
            st.success(f"✅ Profile picture downloaded: {image_path}")
            
            # Step 2: Validate the image
            with status_placeholder:
                st.markdown('<div class="loading-text">🔍 VALIDATING IMAGE...</div>', 
                           unsafe_allow_html=True)
            
            validation_result = github_analyzer.validate_profile_image(image_path)
            if not validation_result['success']:
                st.error(f"❌ Profile picture validation failed: {validation_result['error']}")
                return
            
            st.info(f"✅ Image validated: {validation_result['dimensions']} pixels, {validation_result['format']}")
            
            # Step 3: Generate the portrait
            with status_placeholder:
                st.markdown('<div class="loading-text">🎨 TRANSFORMING PORTRAIT...</div>', 
                           unsafe_allow_html=True)
            
            # Map UI transformation modes to backend style modes
            style_mode_map = {
                "Portrait Enhancement": "tech_enhancement",
                "Character Fusion": "character_fusion", 
                "Style Transfer": "artistic_transformation",
                "Technical Overlay": "fusion"
            }
            
            style_mode = style_mode_map.get(transformation_mode, "fusion")
            
            result = self.image_to_image_generator.generate_profile_based_portrait(
                profile=profile,
                image_path=image_path,
                style_mode=style_mode
            )
            
            if result['success']:
                st.success("🎨 PORTRAIT TRANSFORMATION COMPLETE!")
                
                # Display the original profile picture
                st.markdown("#### 📸 Original Profile Picture")
                st.image(image_path, caption=f"Original GitHub profile picture for {username}", width=200)
                
                # Display the generated images
                st.markdown("#### 🎨 Generated Portrait(s)")
                for i, generated_file in enumerate(result['generated_files']):
                    if os.path.exists(generated_file):
                        st.image(generated_file, caption=f"Transformed portrait ({style_mode})", use_container_width=True)
                        
                        # Download button for each generated image
                        with open(generated_file, "rb") as file:
                            st.download_button(
                                label=f"💾 DOWNLOAD PORTRAIT {i+1}",
                                data=file.read(),
                                file_name=f"{username}_{style_mode}_portrait_{i+1}.png",
                                mime="image/png",
                                key=f"download_{i}"
                            )
                
                # Show session info
                st.info(f"🎯 Style Mode: {transformation_mode} ({style_mode})")
                st.info(f"📁 Session ID: {result['session_id']}")
                
            else:
                st.error(f"❌ Portrait transformation failed: {result['error']}")
                
        except Exception as e:
            st.error(f"❌ Error during image-to-image generation: {str(e)}")

def main():
    """Main application entry point"""
    app = GitToImageUI()
    app.render_ui()

if __name__ == "__main__":
    main()
