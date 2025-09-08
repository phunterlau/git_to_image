#!/usr/bin/env python3
"""
Git-to-Image CLI - Generate artistic portraits from GitHub profiles
Part of the Nano Banana Hackathon project
"""

import argparse
import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from . import github_analyzer
from . import prompt_generator
from .image_generator import ImageGenerator


class GitToImageCLI:
    def __init__(self):
        self.output_dir = Path("generated_images")
        self.profile_dir = Path("user_profile")
        self.image_generator = ImageGenerator(self.output_dir)
        
        # Ensure output directories exist
        self.output_dir.mkdir(exist_ok=True)
        self.profile_dir.mkdir(exist_ok=True)
    
    def load_existing_profile(self, username: str) -> Optional[dict]:
        """Load existing profile if it exists"""
        profile_path = self.profile_dir / f"{username}_profile.json"
        if profile_path.exists():
            try:
                with open(profile_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return None
        return None
    
    def generate_image(self, prompt: str, filename: str, session_id: str = None) -> bool:
        """Generate image using Gemini and save to file"""
        try:
            success, result = self.image_generator.generate_image(prompt, filename, session_id)
            
            if success:
                print(f"✅ Image saved to: {result}")
                return True
            else:
                print(f"❌ Image generation failed: {result}")
                # Fallback: save prompt as text file
                self.save_prompt_fallback(prompt, filename, session_id)
                return False
                
        except Exception as e:
            print(f"❌ Error generating image: {e}")
            self.save_prompt_fallback(prompt, filename, session_id)
            return False
    
    def save_prompt_fallback(self, prompt: str, filename: str, session_id: str = None):
        """Save prompt as text file when image generation fails"""
        if session_id is None:
            session_id = self.image_generator.generate_session_id()
            
        prompt_file = self.output_dir / f"{session_id}_{filename}_prompt.txt"
        with open(prompt_file, 'w') as f:
            f.write(f"Session ID: {session_id}\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Filename: {filename}\n")
            f.write("=" * 50 + "\n\n")
            f.write(prompt)
        
    def generate_multiple_images(self, prompts: dict, username: str, session_id: str = None) -> dict:
        """Generate multiple images from all prompts"""
        print(f"🎨 Starting image generation session for {username}...")
        
        results = self.image_generator.generate_multiple_images(
            prompts, username, session_id
        )
        
        print(f"\n📊 Generation Results (Session: {results['session_id']}):")
        print(f"✅ Success: {results['success_count']}/{results['total_count']} images")
        
        for key, result in results['images'].items():
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {key}: {result['result']}")
        
        return results
    
    def interactive_mode(self):
        """Interactive mode for selecting options"""
        print("🎨 Git-to-Image Generator")
        print("=" * 40)
        
        # Get username
        while True:
            username = input("Enter GitHub username: ").strip()
            if username:
                break
            print("Please enter a valid username")
        
        # Check for existing profile
        profile = self.load_existing_profile(username)
        if profile:
            print(f"✅ Found existing profile for {username}")
            use_existing = input("Use existing profile? (y/n): ").lower().startswith('y')
            if not use_existing:
                profile = None
        
        # Generate new profile if needed
        if not profile:
            print(f"🔍 Analyzing GitHub profile for {username}...")
            try:
                github_token = os.getenv('GITHUB_TOKEN')
                gemini_api_key = os.getenv('GEMINI_API_KEY')
                
                if not github_token:
                    print("❌ Error: GITHUB_TOKEN environment variable not set")
                    return False
                    
                if not gemini_api_key:
                    print("❌ Error: GEMINI_API_KEY environment variable not set")
                    return False
                
                profile = github_analyzer.analyze_user_profile(username, github_token, gemini_api_key)
                print("✅ Analysis complete!")
            except Exception as e:
                print(f"❌ Error analyzing profile: {e}")
                return False
        
        # Show profile summary
        self.display_profile_summary(profile)
        
        # Ask for generation mode
        print("\n🎯 Generation Mode Selection:")
        print("1. Preview Analysis Only (no image generation)")
        print("2. Standard Image Generation (existing prompts)")
        print("3. 🆕 Multi-Style Generation (Phase 4 - Generate 4+ artistic styles)")
        print("4. 🆕 Interactive Style Selection (choose your preferred styles)")
        
        while True:
            try:
                mode_choice = int(input("\nSelect generation mode: "))
                
                if mode_choice == 1:
                    # Preview analysis mode
                    return self.preview_analysis_mode(profile)
                elif mode_choice == 2:
                    # Standard generation with existing prompts
                    return self.standard_generation_mode(profile, username)
                elif mode_choice == 3:
                    # Multi-style generation
                    return self.multi_style_generation_mode(profile, username)
                elif mode_choice == 4:
                    # Interactive style selection
                    return self.interactive_style_selection_mode(profile, username)
                else:
                    print("Please select 1, 2, 3, or 4")
            except ValueError:
                print("Please enter a number")
    
    def preview_analysis_mode(self, profile):
        """Preview analysis mode - show detailed analysis without image generation"""
        print("\n" + "="*60)
        print("🔍 DETAILED ANALYSIS PREVIEW")
        print("="*60)
        
        # Enhanced profile display
        username = profile.get('username', 'Unknown')
        print(f"👤 Developer: {username}")
        print(f"📅 Last Updated: {profile.get('last_updated', 'Unknown')}")
        
        # Language analysis
        lang_profile = profile.get('language_profile', {})
        print(f"\n💻 Language Distribution:")
        for lang, percentage in lang_profile.items():
            print(f"   {lang}: {percentage:.1f}%")
        
        # Domain focus
        domain_focus = profile.get('domain_focus', {})
        if isinstance(domain_focus, dict):
            print(f"\n🎯 Domain Focus: {domain_focus.get('primary_domain', 'Unknown')}")
            if domain_focus.get('confidence'):
                print(f"   Confidence: {domain_focus['confidence']:.1f}%")
        elif isinstance(domain_focus, list) and domain_focus:
            print(f"\n🎯 Domain Focus: {', '.join(domain_focus)}")
        else:
            print(f"\n🎯 Domain Focus: Unknown")
        
        # Contribution analysis  
        contrib_style = profile.get('contribution_style', {})
        if isinstance(contrib_style, dict):
            print(f"\n👨‍💻 Contribution Style: {contrib_style.get('style', 'Unknown')}")
        else:
            print(f"\n👨‍💻 Contribution Style: {contrib_style}")
        
        # Originality analysis
        originality = profile.get('originality_analysis', {})
        if originality and isinstance(originality, dict):
            print(f"\n🚀 Code Originality:")
            print(f"   Original Repos: {originality.get('original_repos_count', 0)}")
            print(f"   Forked Repos: {originality.get('forked_repos_count', 0)}")
            print(f"   Originality Score: {originality.get('originality_score', 0):.2f}")
        
        # High-profile contributions
        high_profile = profile.get('high_profile_contributions', {})
        if isinstance(high_profile, dict) and high_profile.get('has_high_profile_contributions'):
            print(f"\n⭐ High-Profile Contributions:")
            frameworks = high_profile.get('frameworks_contributed', [])
            if isinstance(frameworks, list):
                for fw in frameworks:
                    if isinstance(fw, dict):
                        print(f"   • {fw.get('name', 'Unknown')} ({fw.get('impact_level', 'standard')})")
        
        # Frontend/Backend focus
        fb_focus = profile.get('frontend_backend_focus', {})
        if fb_focus and isinstance(fb_focus, dict):
            print(f"\n🎨 Development Focus: {fb_focus.get('primary_focus', 'Unknown')}")
        
        prompt_count = len(profile.get('image_prompts', {}).get('variations', []))
        print(f"\n📊 Generated Prompts Available: {prompt_count} variations")
        print("\nAnalysis complete! Use generation modes 2-4 to create images.")
        return True
    
    def standard_generation_mode(self, profile, username):
        """Standard generation mode using existing prompts"""
        if 'image_prompts' in profile:
            prompts = profile['image_prompts']
            print("\n🎨 Available image generation options:")
            print("0. Main prompt only")
            print("1. All variations (batch generation)")
            for i, variation in enumerate(prompts.get('variations', []), 2):
                print(f"{i}. Variation {variation['variation']} only (randomness: {variation['randomness_level']})")
            
            while True:
                try:
                    choice = int(input("\nSelect option: "))
                    session_id = self.image_generator.generate_session_id()
                    
                    if choice == 0:
                        # Generate main prompt only
                        selected_prompt = prompts['main_prompt']
                        filename = f"{username}_main"
                        success = self.generate_image(selected_prompt, filename, session_id)
                        break
                    elif choice == 1:
                        # Generate all images
                        results = self.generate_multiple_images(prompts, username, session_id)
                        success = results['success_count'] > 0
                        break
                    elif 2 <= choice <= len(prompts.get('variations', [])) + 1:
                        # Generate specific variation
                        var_index = choice - 2
                        selected_prompt = prompts['variations'][var_index]['prompt']
                        randomness = prompts['variations'][var_index]['randomness_level']
                        filename = f"{username}_var{var_index+1}_r{randomness}"
                        success = self.generate_image(selected_prompt, filename, session_id)
                        break
                    else:
                        print("Invalid choice")
                except ValueError:
                    print("Please enter a number")
        else:
            print("❌ No image prompts found in profile")
            return False
        
        # Generate image
        print(f"\n🎨 Starting image generation for {username}...")
        
        if success:
            print(f"✅ Image generation complete for {username}!")
        else:
            print(f"❌ Image generation failed for {username}")
        
        return success
    
    def multi_style_generation_mode(self, profile, username):
        """Multi-style generation mode - Phase 4 feature"""
        print("\n🎨 Multi-Style Generation Mode")
        print("This will generate 4+ distinct artistic styles based on your developer profile")
        
        num_styles = 4
        try:
            custom_num = input(f"Number of styles to generate (default {num_styles}): ").strip()
            if custom_num:
                num_styles = int(custom_num)
                num_styles = max(1, min(8, num_styles))  # Limit between 1-8
        except ValueError:
            pass
        
        print(f"\n🎯 Generating {num_styles} artistic style variations...")
        session_id = self.image_generator.generate_session_id()
        
        try:
            results = self.image_generator.generate_style_variations(
                profile=profile, 
                num_styles=num_styles,
                session_id=session_id
            )
            
            if results['success']:
                print(f"\n✅ Multi-style generation complete!")
                print(f"📊 Generated {results['success_count']}/{results['total_styles']} styles successfully")
                print(f"🎨 Developer Category: {results['developer_category']}")
                
                print("\n🖼️  Generated Styles:")
                for style_name, style_data in results['styles'].items():
                    status = "✅" if style_data['success'] else "❌"
                    print(f"   {status} {style_name}")
                
                return results['success_count'] > 0
            else:
                print("❌ Multi-style generation failed")
                return False
                
        except Exception as e:
            print(f"❌ Error in multi-style generation: {e}")
            return False
    
    def interactive_style_selection_mode(self, profile, username):
        """Interactive style selection mode - Phase 4 feature"""
        print("\n🎯 Interactive Style Selection Mode")
        
        # Import the style classification function
        from .prompt_generator import classify_developer_category
        
        dev_category = classify_developer_category(profile)
        print(f"📊 Detected Developer Category: {dev_category}")
        
        # Show available style categories
        style_categories = {
            1: "Professional Portrait - Corporate headshot style",
            2: "Artistic Creative - Contemporary digital art", 
            3: "Technical Schematic - Blueprint/diagram style",
            4: "Minimalist Abstract - Clean geometric design"
        }
        
        # Add category-specific styles based on developer type
        if dev_category == 'legendary':
            style_categories[5] = "Epic Legendary - Heroic open-source champion"
        elif dev_category == 'frontend':
            style_categories[5] = "Frontend Specialist - Vibrant UI-focused aesthetic"
        elif dev_category == 'backend':
            style_categories[5] = "Backend Engineer - Terminal/server room aesthetic"
        else:
            style_categories[5] = "Full-Stack Developer - Hybrid artistic style"
        
        print("\n🎨 Available Style Categories:")
        for num, desc in style_categories.items():
            print(f"{num}. {desc}")
        
        # Let user select multiple styles
        print("\nSelect style numbers (comma-separated, e.g., '1,3,5') or 'all' for all styles:")
        selection = input("Your selection: ").strip().lower()
        
        if selection == 'all':
            selected_styles = list(style_categories.keys())
        else:
            try:
                selected_styles = [int(x.strip()) for x in selection.split(',')]
                selected_styles = [s for s in selected_styles if s in style_categories]
            except ValueError:
                print("❌ Invalid selection, using default styles")
                selected_styles = [1, 2, 3]
        
        if not selected_styles:
            print("❌ No valid styles selected")
            return False
        
        print(f"\n🎯 Generating {len(selected_styles)} selected style(s)...")
        session_id = self.image_generator.generate_session_id()
        
        # Generate each selected style
        success_count = 0
        for style_num in selected_styles:
            style_desc = style_categories[style_num]
            print(f"\n🖼️  Generating: {style_desc}")
            
            # Create custom prompt based on selection
            custom_prompt = self.create_custom_style_prompt(profile, style_num, dev_category)
            filename = f"{username}_custom_style_{style_num}"
            
            success, result = self.generate_image(custom_prompt, filename, session_id)
            if success:
                success_count += 1
                print(f"   ✅ Success: {result}")
            else:
                print(f"   ❌ Failed: {result}")
        
        print(f"\n📊 Style Selection Complete: {success_count}/{len(selected_styles)} successful")
        return success_count > 0
    
    def create_custom_style_prompt(self, profile, style_num, dev_category):
        """Create custom prompt based on style selection"""
        from .prompt_generator import generate_image_prompt
        from .style_guide import get_weighted_style_elements
        
        # Get base style elements
        base_style = get_weighted_style_elements(profile, randomness=0.1)
        character = base_style['character']
        traits = ', '.join(base_style['character_traits'])
        
        # Style-specific modifications
        style_modifiers = {
            1: "Professional headshot style, corporate photography, clean background",
            2: "Artistic digital illustration, contemporary art style, creative composition", 
            3: "Technical blueprint aesthetic, schematic design, engineering drawing style",
            4: "Minimalist vector art, geometric design, simple clean lines",
            5: {
                'legendary': "Epic legendary portrait, heroic proportions, champion of open source",
                'frontend': "Vibrant UI-focused design, modern web aesthetic, colorful gradients",
                'backend': "Terminal matrix style, server room environment, cyberpunk elements",
                'default': "Full-stack hybrid design, balanced technical and creative elements"
            }
        }
        
        if style_num == 5:
            modifier = style_modifiers[5].get(dev_category, style_modifiers[5]['default'])
        else:
            modifier = style_modifiers.get(style_num, style_modifiers[1])
        
        # Construct the custom prompt
        primary_lang = list(profile.get('language_profile', {}).keys())[0] if profile.get('language_profile') else 'Programming'
        domain = profile.get('domain_focus', {}).get('primary_domain', 'Software Development')
        
        prompt = f"Create a {modifier} portrait of a {character} representing a {domain} developer who specializes in {primary_lang}. Character traits: {traits}. Professional quality, detailed artwork, suitable for a developer portfolio."
        
        return prompt
    
    def display_profile_summary(self, profile: dict):
        """Display a summary of the user's profile"""
        print(f"\n📊 Profile Summary for {profile['username']}:")
        print("-" * 40)
        
        # Languages
        if 'language_profile' in profile:
            top_lang = max(profile['language_profile'].items(), key=lambda x: x[1])
            print(f"🔤 Primary Language: {top_lang[0]} ({top_lang[1]:.1f}%)")
        
        # Domain focus
        if 'domain_focus' in profile:
            domains = ", ".join(profile['domain_focus'])
            print(f"🎯 Focus Areas: {domains}")
        
        # Contribution style
        if 'contribution_style' in profile:
            style_data = profile['contribution_style']
            if isinstance(style_data, dict):
                style = style_data['primary_style']
            else:
                style = style_data  # Handle string format for special profiles
            print(f"👨‍💻 Contribution Style: {style}")
        
        # Commit cadence
        if 'commit_cadence' in profile:
            cadence = profile['commit_cadence']
            if isinstance(cadence, dict):
                activity = cadence.get('activity_level', 'Unknown')
                time_pattern = cadence.get('time_of_day', 'Unknown')
                print(f"⏰ Activity: {activity} {time_pattern}")
            else:
                print(f"⏰ Activity: {cadence}")  # Handle string format

    # =============================================================================
    # PHASE 5: Profile Picture Integration Methods
    # =============================================================================
    
    def profile_picture_mode(self, username, transformation_mode='fusion', privacy_check=True):
        """Generate portraits using GitHub profile picture as input - Phase 5 feature"""
        from .image_to_image_generator import ImageToImageGenerator
        
        print(f"\n📸 Profile Picture Mode - {transformation_mode.replace('_', ' ').title()}")
        
        # Privacy check if enabled
        if privacy_check:
            print(f"This mode will download and use {username}'s GitHub profile picture.")
            consent = input("Do you consent to using their profile picture? (y/N): ").strip().lower()
            if consent not in ['y', 'yes']:
                print("❌ Profile picture usage declined. Falling back to text-only generation.")
                return False
        
        # Get or load user profile
        profile = self.load_existing_profile(username)
        if not profile:
            print(f"📊 No existing profile found for {username}. Analyzing GitHub profile...")
            profile = github_analyzer.analyze_and_save_user_profile(username)
            if not profile:
                print(f"❌ Failed to analyze GitHub profile for {username}")
                return False
        
        # Download profile picture
        print(f"📸 Downloading profile picture for {username}...")
        picture_result = github_analyzer.get_github_profile_picture(username)
        
        if not picture_result['success']:
            print(f"❌ Failed to get profile picture: {picture_result['error']}")
            print("💡 Falling back to text-only generation...")
            return self.standard_generation_mode(profile, username)
        
        image_path = picture_result['image_path']
        print(f"✅ Profile picture saved: {image_path}")
        
        # Validate the image
        validation_result = github_analyzer.validate_profile_image(image_path)
        if not validation_result['success']:
            print(f"❌ Profile picture validation failed: {validation_result['error']}")
            return False
        
        print(f"✅ Image validated: {validation_result['dimensions']} pixels, {validation_result['format']}")
        
        # Initialize image-to-image generator
        i2i_generator = ImageToImageGenerator()
        if not i2i_generator.available:
            print("❌ Image-to-image generation not available. Check GEMINI_API_KEY.")
            return False
        
        # Generate the portrait
        session_id = i2i_generator.generate_session_id()
        print(f"🎨 Generating {transformation_mode} portrait...")
        
        result = i2i_generator.generate_profile_based_portrait(
            profile=profile,
            image_path=image_path,
            style_mode=transformation_mode,
            session_id=session_id
        )
        
        if result['success']:
            print(f"✅ Profile picture transformation complete!")
            print(f"🎨 Style Mode: {result['style_mode']}")
            print(f"📁 Session ID: {result['session_id']}")
            print(f"🖼️  Generated Files:")
            for file_path in result['generated_files']:
                print(f"   📄 {file_path}")
            print(f"📝 Prompt saved: {result['prompt_file']}")
            return True
        else:
            print(f"❌ Profile picture transformation failed: {result['error']}")
            return False
    
    def multi_transformation_mode(self, username, privacy_check=True):
        """Generate multiple transformation modes from profile picture - Phase 5 feature"""
        from .image_to_image_generator import ImageToImageGenerator
        
        print(f"\n🎨 Multi-Transformation Mode")
        print("This will generate multiple artistic transformations from the GitHub profile picture")
        
        # Privacy check if enabled
        if privacy_check:
            print(f"This mode will download and use {username}'s GitHub profile picture.")
            consent = input("Do you consent to using their profile picture? (y/N): ").strip().lower()
            if consent not in ['y', 'yes']:
                print("❌ Profile picture usage declined.")
                return False
        
        # Get or load user profile
        profile = self.load_existing_profile(username)
        if not profile:
            print(f"📊 No existing profile found for {username}. Analyzing GitHub profile...")
            profile = github_analyzer.analyze_and_save_user_profile(username)
            if not profile:
                print(f"❌ Failed to analyze GitHub profile for {username}")
                return False
        
        # Download profile picture
        print(f"📸 Downloading profile picture for {username}...")
        picture_result = github_analyzer.get_github_profile_picture(username)
        
        if not picture_result['success']:
            print(f"❌ Failed to get profile picture: {picture_result['error']}")
            return False
        
        image_path = picture_result['image_path']
        print(f"✅ Profile picture ready: {image_path}")
        
        # Initialize image-to-image generator
        i2i_generator = ImageToImageGenerator()
        if not i2i_generator.available:
            print("❌ Image-to-image generation not available. Check GEMINI_API_KEY.")
            return False
        
        # Generate multiple transformations
        transformation_modes = ['tech_enhancement', 'character_fusion', 'artistic_transformation']
        
        print(f"🎯 Generating {len(transformation_modes)} transformation modes...")
        
        results = i2i_generator.generate_multiple_transformations(
            profile=profile,
            image_path=image_path,
            modes=transformation_modes
        )
        
        if results['success']:
            print(f"\n✅ Multi-transformation complete!")
            print(f"📊 Generated {results['success_count']}/{results['total_modes']} transformations successfully")
            
            print("\n🖼️  Generated Transformations:")
            for mode, mode_data in results['transformations'].items():
                status = "✅" if mode_data.get('success', False) else "❌"
                print(f"   {status} {mode.replace('_', ' ').title()}")
                if mode_data.get('success', False):
                    for file_path in mode_data.get('generated_files', []):
                        print(f"      📄 {file_path}")
            
            return results['success_count'] > 0
        else:
            print("❌ Multi-transformation failed")
            return False
    
    def transformation_preview(self, username):
        """Preview different transformation modes before generation - Phase 5 feature"""
        print(f"\n🔍 Transformation Preview for {username}")
        print("This shows what transformation modes are available based on the developer profile")
        
        # Get or load user profile
        profile = self.load_existing_profile(username)
        if not profile:
            print(f"📊 No existing profile found for {username}. Analyzing GitHub profile...")
            profile = github_analyzer.analyze_and_save_user_profile(username)
            if not profile:
                print(f"❌ Failed to analyze GitHub profile for {username}")
                return False
        
        # Show detailed profile analysis
        self.preview_analysis_mode(profile, username)
        
        # Show available transformation modes
        print("\n🎨 Available Transformation Modes:")
        
        
        from .style_guide import get_enhanced_style_elements
        style = get_enhanced_style_elements(profile)
        
        print(f"\n1. 🔧 Tech Enhancement:")
        print(f"   • Preserve natural appearance with subtle programming elements")
        print(f"   • Add {self.get_primary_language(profile)} and {self.get_primary_domain(profile)} visual elements")
        print(f"   • Professional developer aesthetic")
        
        print(f"\n2. 🤖 Character Fusion:")
        character = style.get('character', 'Wise Owl')
        archetype = style.get('archetype', 'The Developer')
        print(f"   • Blend with {character} characteristics")
        print(f"   • Express {archetype} qualities")
        print(f"   • Maintain recognizable features")
        
        print(f"\n3. 🎭 Artistic Transformation:")
        artistic_style = style.get('artistic_style', 'Professional digital art')
        print(f"   • Apply {artistic_style} aesthetic")
        print(f"   • Transform using coding-inspired artistic vision")
        print(f"   • Creative interpretation of developer identity")
        
        print(f"\n4. 🌟 Fusion (Balanced):")
        print(f"   • Skillful blend of person and developer identity")
        print(f"   • Professional yet creative approach")
        print(f"   • Express coding expertise through environment and styling")
        
        return True

    def get_primary_language(self, profile):
        """Helper to get primary programming language"""
        lang_profile = profile.get('language_profile', {})
        if lang_profile:
            return max(lang_profile, key=lang_profile.get)
        return 'Programming'
    
    def get_primary_domain(self, profile):
        """Helper to get primary domain focus"""
        domain_focus = profile.get('domain_focus', [])
        return domain_focus[0] if domain_focus else 'Development'
    
    # =============================================================================
    
    def batch_mode(self, usernames: list, output_prefix: str = "batch"):
        """Batch process multiple usernames"""
        print(f"🔄 Processing {len(usernames)} users in batch mode...")
        batch_session_id = self.image_generator.generate_session_id()
        print(f"📋 Batch Session ID: {batch_session_id}")
        
        results = []
        for i, username in enumerate(usernames, 1):
            print(f"\n[{i}/{len(usernames)}] Processing {username}...")
            
            try:
                # Check for existing profile
                profile = self.load_existing_profile(username)
                if not profile:
                    github_token = os.getenv('GITHUB_TOKEN')
                    gemini_api_key = os.getenv('GEMINI_API_KEY')
                    
                    if not github_token or not gemini_api_key:
                        print(f"❌ Missing API keys for {username}")
                        results.append({'username': username, 'success': False, 'error': 'Missing API keys'})
                        continue
                    
                    profile = github_analyzer.analyze_user_profile(username, github_token, gemini_api_key)
                
                # Generate image with main prompt
                if 'image_prompts' in profile:
                    prompt = profile['image_prompts']['main_prompt']
                    filename = f"{output_prefix}_{username}_main"
                    success = self.generate_image(prompt, filename, batch_session_id)
                    results.append({'username': username, 'success': success})
                else:
                    print(f"❌ No image prompts found for {username}")
                    results.append({'username': username, 'success': False})
                    
            except Exception as e:
                print(f"❌ Error processing {username}: {e}")
                results.append({'username': username, 'success': False, 'error': str(e)})
        
        # Summary
        successful = sum(1 for r in results if r['success'])
        print(f"\n📊 Batch Results (Session: {batch_session_id}): {successful}/{len(results)} successful")
        
        return results


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Generate artistic portraits from GitHub profiles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m git_to_image                         # Interactive mode with Phase 4 options
  python -m git_to_image -u phunterlau           # Generate for specific user  
  python -m git_to_image -u phunterlau -p        # Show profile only (no image)
  python -m git_to_image -u phunterlau --preview # 🆕 Detailed analysis preview
  python -m git_to_image -u phunterlau --multi-style --num-styles 6  # 🆕 Multi-style generation
  python -m git_to_image -u phunterlau --style-interactive            # 🆕 Interactive style selection
  python -m git_to_image -b user1 user2          # Batch mode for multiple users
        """
    )
    
    parser.add_argument('-u', '--username', help='GitHub username to analyze')
    parser.add_argument('-p', '--profile-only', action='store_true', 
                       help='Only show profile analysis (no image generation)')
    parser.add_argument('-b', '--batch', nargs='+', metavar='USERNAME',
                       help='Batch mode: process multiple usernames')
    parser.add_argument('--force-refresh', action='store_true',
                       help='Force refresh of existing profiles')
    
    # Phase 4 new arguments
    parser.add_argument('--preview', action='store_true',
                       help='🆕 Preview detailed analysis without image generation')
    parser.add_argument('--multi-style', action='store_true',
                       help='🆕 Generate multiple artistic styles (Phase 4)')
    parser.add_argument('--num-styles', type=int, default=4, metavar='N',
                       help='Number of styles for multi-style generation (1-8, default: 4)')
    parser.add_argument('--style-interactive', action='store_true',
                       help='🆕 Interactive style selection mode')
    
    # Phase 5 new arguments  
    parser.add_argument('--profile-picture', action='store_true',
                       help='🆕 Use GitHub profile picture for image-to-image generation (Phase 5)')
    parser.add_argument('--transformation-mode', choices=['tech_enhancement', 'character_fusion', 'artistic_transformation', 'fusion'], 
                       default='fusion', help='🆕 Transformation mode for profile picture (Phase 5)')
    parser.add_argument('--multi-transformation', action='store_true',
                       help='🆕 Generate multiple transformation modes from profile picture (Phase 5)')
    parser.add_argument('--privacy-mode', action='store_true',
                       help='🆕 Ask for consent before downloading profile picture (Phase 5)')
    
    args = parser.parse_args()
    
    cli = GitToImageCLI()
    
    try:
        if args.batch:
            # Batch mode
            results = cli.batch_mode(args.batch)
            sys.exit(0 if all(r['success'] for r in results) else 1)
            
        elif args.username:
            # Single user mode
            username = args.username
            
            # Load or generate profile
            profile = None if args.force_refresh else cli.load_existing_profile(username)
            if not profile:
                print(f"🔍 Analyzing GitHub profile for {username}...")
                github_token = os.getenv('GITHUB_TOKEN')
                gemini_api_key = os.getenv('GEMINI_API_KEY')
                
                if not github_token:
                    print("❌ Error: GITHUB_TOKEN environment variable not set")
                    sys.exit(1)
                    
                if not gemini_api_key:
                    print("❌ Error: GEMINI_API_KEY environment variable not set")
                    sys.exit(1)
                
                profile = github_analyzer.analyze_user_profile(username, github_token, gemini_api_key)
                print("✅ Analysis complete!")
            
            # Display profile
            cli.display_profile_summary(profile)
            
            # Handle different generation modes
            if args.preview:
                # Phase 4: Preview analysis mode
                success = cli.preview_analysis_mode(profile)
                sys.exit(0 if success else 1)
            elif args.profile_picture and args.multi_transformation:
                # Phase 5: Multi-transformation from profile picture
                success = cli.multi_transformation_mode(username, privacy_check=args.privacy_mode)
                sys.exit(0 if success else 1)
            elif args.profile_picture:
                # Phase 5: Single transformation from profile picture
                success = cli.profile_picture_mode(username, args.transformation_mode, privacy_check=args.privacy_mode)
                sys.exit(0 if success else 1)
            elif args.multi_style:
                # Phase 4: Multi-style generation
                session_id = cli.image_generator.generate_session_id()
                results = cli.image_generator.generate_style_variations(
                    profile=profile, 
                    num_styles=args.num_styles,
                    session_id=session_id
                )
                success = results.get('success_count', 0) > 0
                sys.exit(0 if success else 1)
            elif args.style_interactive:
                # Phase 4: Interactive style selection
                success = cli.interactive_style_selection_mode(profile, username)
                sys.exit(0 if success else 1)
            elif not args.profile_only and 'image_prompts' in profile:
                # Standard generation with main prompt
                session_id = cli.image_generator.generate_session_id()
                prompt = profile['image_prompts']['main_prompt']
                success = cli.generate_image(prompt, f"{username}_main", session_id)
                sys.exit(0 if success else 1)
        else:
            # Interactive mode
            success = cli.interactive_mode()
            sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
