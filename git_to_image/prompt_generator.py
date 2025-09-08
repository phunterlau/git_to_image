# git_to_image/prompt_generator.py
# Module to construct the final Gemini prompt

from .style_guide import get_weighted_style_elements
from .thematic_elements import LANGUAGE_THEMES, DOMAIN_THEMES
import random

def generate_image_prompt(profile, user_preferences=None, randomness=0.1):
    """
    Generate a detailed prompt for Gemini image generation based on user profile.
    
    Args:
        profile: The analyzed user profile
        user_preferences: Optional dict with user's style preferences
        randomness: Float 0-1, amount of randomness to inject
    
    Returns:
        String containing the complete image generation prompt
    """
    
    # Get style elements based on profile
    style = get_weighted_style_elements(profile, randomness)
    
    # Handle Linus Torvalds easter egg
    if profile.get('is_legend'):
        return generate_linus_prompt()
    
    # Build the main prompt
    character = style['character']
    drawing_style = style['drawing_style']
    background = style['background']
    lighting = style['lighting']
    color_scheme = style['color_scheme']
    atmosphere = style['atmosphere']
    character_traits = ', '.join(style['character_traits'])
    
    # Get some context from the profile
    username = profile.get('username', 'developer')
    primary_language = get_primary_language(profile)
    primary_domain = get_primary_domain(profile)
    activity_info = get_activity_description(profile)

    # Get weighted thematic elements for all significant languages and domains
    language_themes, domain_themes = get_weighted_thematic_descriptions(profile)
    
    # Build comprehensive thematic interaction section
    thematic_section = ""
    if language_themes or domain_themes:
        thematic_section = f"Thematic Interaction:\n- The scene should feature thematic elements representing the developer's diverse skill set. The {character} should be interacting with these elements naturally.\n"
        
        if language_themes:
            thematic_section += "- Programming Language Elements:\n"
            for lang_theme in language_themes:
                thematic_section += f"  • {lang_theme['language']} ({lang_theme['percentage']:.1f}%, {lang_theme['weight_desc']}): {lang_theme['theme']}\n"
        
        if domain_themes:
            thematic_section += "- Domain Expertise Elements:\n"
            for domain_theme in domain_themes:
                thematic_section += f"  • {domain_theme['domain']} ({domain_theme['weight_desc']} focus): {domain_theme['theme']}\n"
        
        thematic_section += "- Integration: These thematic elements should complement each other and create a cohesive scene that tells the story of a multi-skilled developer.\n\n"
    
    # Construct the detailed prompt
    prompt = f"""Create a {drawing_style} illustration of a {character_traits} {character} representing a software developer.

IMPORTANT: This must be a fully animal character - NO human face or human features should appear. Keep the character 100% as the specified animal while expressing personality through animal features and body language.

Character Details:
- The {character} should embody the essence of a {primary_domain} developer who primarily codes in {primary_language}
- Character traits: {character_traits}
- The character should appear {atmosphere} and dedicated to their craft
- Maintain authentic animal anatomy - no human facial features, expressions should be conveyed through animal eyes and body language

Setting & Environment:
- Background: {background}
- Lighting: {lighting}
- Color scheme: {color_scheme}
- Atmosphere: {atmosphere}

{thematic_section}Technical Context:
- Subtle references to {primary_language} programming (perhaps code snippets, logos, or related symbols in the background)
- The environment should reflect {primary_domain} development work
- {activity_info}

Artistic Style:
- Style: {drawing_style}
- High quality, detailed illustration
- The character should be the main focus
- Professional yet creative representation of a modern software developer

Additional Details:
- The {character} should look intelligent and capable through animal expressions only
- Include subtle technological elements that don't overwhelm the composition
- Maintain a balance between technical accuracy and artistic creativity
- STRICT REQUIREMENT: No human faces, mouths, or facial features - keep 100% animal characteristics"""

    # Apply user preferences if provided
    if user_preferences:
        prompt += f"\n\nUser Preferences:\n"
        for key, value in user_preferences.items():
            prompt += f"- {key}: {value}\n"
    
    return prompt

def generate_linus_prompt():
    """Generate the special Linus Torvalds easter egg prompt."""
    return """Create a legendary portrait of a wise, powerful octopus that embodies the essence and appearance of Linus Torvalds, the creator of Linux.

IMPORTANT: This must be a fully octopus character - NO human face or human features should appear. The character should be 100% octopus while capturing Linus's personality and style.

Character Details:
- A majestic octopus with distinctly octopus features (no human face elements)
- Linus's signature round, wire-rimmed glasses perched on the octopus's intelligent eyes
- The octopus head should have natural octopus texture with coloring reminiscent of Linus's graying hair
- Octopus eyes behind glasses showing intelligence and discernment (no human facial features)
- One tentacle gracefully positioned over a vintage mechanical keyboard, actively coding
- Another tentacle holding a steaming cup of coffee
- The octopus should convey Linus's characteristic thoughtful, slightly amused demeanor through body language and eye expression alone
- Body posture conveying both approachability and the authority of a technical leader
- Keep all features authentically octopus - tentacles, natural octopus skin texture, octopus eyes

Setting & Environment:
- Background: A sophisticated home office merged with abstract Linux kernel visualization
- Floating holographic C code snippets and kernel data structures
- Multiple monitors showing terminal windows with git commits and kernel compilation
- Tux the penguin mascot sitting nearby as a friendly companion
- Books about operating systems and computer science on shelves
- Color palette: Professional blues and greens with warm lighting from desk lamps

Artistic Style:
- Photorealistic portrait style with fantasy elements
- High detail showing both technical mastery and human warmth
- Professional lighting that highlights the glasses and creates depth
- The overall feeling should be "brilliant engineer who changed the world"
- Balance between approachable mentor and respected authority figure

Character Essence:
- Convey Linus's known personality: brilliant, direct, passionate about code quality
- The "Benevolent Dictator for Life" energy - firm but fair leadership
- Show someone who built the foundation of modern computing from his bedroom
- The octopus should feel like it could actually be Linus if he were an octopus
- Include subtle pride in the Linux ecosystem and open source philosophy
- STRICT REQUIREMENT: Maintain 100% octopus anatomy - no human face, no human mouth, no human nose
- Express personality and character through octopus eyes, tentacle positioning, and overall body language only"""

def get_primary_language_name(profile):
    """Extracts just the name of the primary programming language."""
    language_profile = profile.get('language_profile', {})
    if not language_profile:
        return None
    return max(language_profile, key=language_profile.get)

def get_primary_domain_name(profile):
    """Extracts just the name of the primary domain."""
    domain_focus = profile.get('domain_focus', [])
    if not domain_focus:
        return "Generalist"
    return domain_focus[0]

def get_primary_language(profile):
    """Extract the primary programming language from the profile."""
    language_profile = profile.get('language_profile', {})
    if not language_profile:
        return "multiple programming languages"
    
    primary_lang = max(language_profile, key=language_profile.get)
    percentage = language_profile[primary_lang]
    
    if percentage > 50:
        return f"{primary_lang} (primary language)"
    else:
        return f"{primary_lang} and other languages"

def get_primary_domain(profile):
    """Extract the primary domain from the profile."""
    domain_focus = profile.get('domain_focus', [])
    if not domain_focus:
        return "general software development"
    
    return domain_focus[0].lower()

def get_activity_description(profile):
    """Generate a description of the user's activity patterns."""
    commit_cadence = profile.get('commit_cadence', {})
    if not commit_cadence:
        return "The character should appear as an active developer"
    
    time_of_day = commit_cadence.get('time_of_day', 'Unknown')
    activity_level = commit_cadence.get('activity_level', 'Unknown')
    
    activity_map = {
        'Night Owl': "working late into the night with glowing screens",
        'Day Coder': "working during bright daylight hours",
        'Evening Coder': "working during golden hour evening sessions",
        'Morning Coder': "working during fresh morning hours"
    }
    
    activity_desc = activity_map.get(time_of_day, "working at their computer")
    
    if activity_level == "Highly Active":
        return f"Show the character as very energetic, {activity_desc}"
    elif activity_level == "Consistent":
        return f"Show the character as steadily focused, {activity_desc}"
    elif activity_level == "Casual":
        return f"Show the character as relaxed and contemplative, {activity_desc}"
    else:
        return f"Show the character {activity_desc}"

def create_prompt_variations(profile, count=3):
    """Create multiple prompt variations with different randomness levels.
    
    Args:
        profile: The analyzed user profile
        count: Number of variations to generate
    
    Returns:
        List of prompt variations
    """
    variations = []
    randomness_levels = [0.0, 0.15, 0.3]  # Conservative, balanced, creative
    
    for i in range(count):
        randomness = randomness_levels[i] if i < len(randomness_levels) else 0.2
        prompt = generate_image_prompt(profile, randomness=randomness)
        variations.append({
            'variation': i + 1,
            'randomness_level': randomness,
            'prompt': prompt
        })
    
    return variations


def get_thematic_descriptions(primary_language_name, primary_domain_name):
    """
    Retrieves thematic descriptions for the primary language and domain,
    randomly choosing between direct and extended themes.
    """
    # Clean up names for dictionary lookup
    lang_key = primary_language_name.split(" ")[0] if primary_language_name else ""
    
    # Map domain variations to dictionary keys
    domain_mapping = {
        "AI/ML": "AI / Machine Learning",
        "AI / Machine Learning": "AI / Machine Learning", 
        "Machine Learning": "AI / Machine Learning",
        "Data Science": "Data Science & Analytics",
        "Data Science & Analytics": "Data Science & Analytics",
        "Web Frontend": "Web Frontend",
        "Frontend": "Web Frontend",
        "Web Backend": "Web Backend", 
        "Backend": "Web Backend",
        "Mobile Development": "Mobile Development",
        "Mobile": "Mobile Development",
        "DevOps": "DevOps / Infrastructure",
        "Infrastructure": "DevOps / Infrastructure",
        "DevOps / Infrastructure": "DevOps / Infrastructure",
        "Cybersecurity": "Generalist",  # Map to generalist as we don't have cybersecurity theme yet
        "Generalist": "Generalist"
    }
    
    domain_key = domain_mapping.get(primary_domain_name, "Generalist")

    lang_theme_details = LANGUAGE_THEMES.get(lang_key, {})
    domain_theme_details = DOMAIN_THEMES.get(domain_key, {})

    lang_theme = ""
    if lang_theme_details:
        theme_type = random.choice(['direct', 'extended'])
        lang_theme = lang_theme_details.get(theme_type, "")

    domain_theme = ""
    if domain_theme_details:
        theme_type = random.choice(['direct', 'extended'])
        domain_theme = domain_theme_details.get(theme_type, "")
        
    return lang_theme, domain_theme


def get_weighted_thematic_descriptions(profile):
    """
    Retrieves thematic descriptions for multiple languages and domains with weights.
    Returns comprehensive thematic elements that reflect the developer's full skill set.
    """
    language_profile = profile.get('language_profile', {})
    domain_focus = profile.get('domain_focus', [])
    
    # Process languages (only include those with significant usage, e.g., > 5%)
    language_themes = []
    for lang, percentage in language_profile.items():
        if percentage >= 5.0:  # Only include languages with 5%+ usage
            lang_key = lang.split(" ")[0]
            lang_theme_details = LANGUAGE_THEMES.get(lang_key, {})
            if lang_theme_details:
                theme_type = random.choice(['direct', 'extended'])
                theme_text = lang_theme_details.get(theme_type, "")
                if theme_text:
                    weight_desc = "primary" if percentage > 40 else "significant" if percentage > 15 else "notable"
                    language_themes.append({
                        'language': lang,
                        'percentage': percentage,
                        'weight_desc': weight_desc,
                        'theme': theme_text
                    })
    
    # Sort languages by percentage (descending)
    language_themes.sort(key=lambda x: x['percentage'], reverse=True)
    
    # Process domains with explicit weight mapping
    domain_mapping = {
        "AI/ML": "AI / Machine Learning",
        "AI / Machine Learning": "AI / Machine Learning", 
        "Machine Learning": "AI / Machine Learning",
        "Data Science": "Data Science & Analytics",
        "Data Science & Analytics": "Data Science & Analytics",
        "Web Frontend": "Web Frontend",
        "Frontend": "Web Frontend",
        "Web Backend": "Web Backend", 
        "Backend": "Web Backend",
        "Mobile Development": "Mobile Development",
        "Mobile": "Mobile Development",
        "DevOps": "DevOps / Infrastructure",
        "Infrastructure": "DevOps / Infrastructure",
        "DevOps / Infrastructure": "DevOps / Infrastructure",
        "Cybersecurity": "Generalist",
        "Generalist": "Generalist"
    }
    
    domain_themes = []
    for i, domain in enumerate(domain_focus[:3]):  # Limit to top 3 domains
        domain_key = domain_mapping.get(domain, "Generalist")
        domain_theme_details = DOMAIN_THEMES.get(domain_key, {})
        if domain_theme_details:
            theme_type = random.choice(['direct', 'extended'])
            theme_text = domain_theme_details.get(theme_type, "")
            if theme_text:
                weight_desc = "primary" if i == 0 else "secondary" if i == 1 else "additional"
                domain_themes.append({
                    'domain': domain,
                    'position': i + 1,
                    'weight_desc': weight_desc,
                    'theme': theme_text
                })
    
    return language_themes, domain_themes



# =============================================================================
# PHASE 4: Advanced Multi-Style Generation
# =============================================================================

def generate_multi_style_prompts(profile, num_variations=4):
    """
    Generate multiple artistic interpretations of the same developer profile.
    
    Args:
        profile: The analyzed user profile
        num_variations: Number of different styles to generate
    
    Returns:
        List of prompt variations with distinct artistic styles
    """
    base_style = get_weighted_style_elements(profile, randomness=0.0)
    
    # Determine developer category for style adaptation
    dev_category = classify_developer_category(profile)
    
    # Define style templates for different artistic approaches
    style_templates = [
        {
            'name': 'Professional Portrait',
            'style_modifier': 'professional headshot style',
            'artistic_approach': 'Corporate photography',
            'lighting': 'professional studio lighting',
            'composition': 'clean, minimal background'
        },
        {
            'name': 'Artistic Creative',
            'style_modifier': 'artistic digital illustration',
            'artistic_approach': 'Contemporary digital art',
            'lighting': 'dramatic artistic lighting',
            'composition': 'dynamic composition with creative elements'
        },
        {
            'name': 'Technical Schematic',
            'style_modifier': 'technical blueprint style',
            'artistic_approach': 'Engineering diagram aesthetic',
            'lighting': 'technical drafting illumination',
            'composition': 'precise, grid-based layout'
        },
        {
            'name': 'Minimalist Abstract',
            'style_modifier': 'minimalist vector art',
            'artistic_approach': 'Simple geometric design',
            'lighting': 'clean, even lighting',
            'composition': 'balanced negative space'
        }
    ]
    
    variations = []
    for i, template in enumerate(style_templates[:num_variations]):
        # Apply developer category specialization
        specialized_prompt = apply_developer_category_styling(
            base_style, template, profile, dev_category
        )
        
        variations.append({
            'variation': i + 1,
            'style_name': template['name'],
            'dev_category': dev_category,
            'prompt': specialized_prompt
        })
    
    return variations


def classify_developer_category(profile):
    """
    Classify developer into categories for specialized styling.
    
    Args:
        profile: The analyzed user profile
    
    Returns:
        String: Developer category ('legendary', 'frontend', 'backend', 'fullstack', 'specialist')
    """
    # Check for high-profile contributions
    high_profile = profile.get('high_profile_contributions', {})
    if high_profile and high_profile.get('has_high_profile_contributions', False):
        legendary_frameworks = high_profile.get('frameworks_contributed', [])
        if any('legendary' in fw.get('impact_level', '') for fw in legendary_frameworks):
            return 'legendary'
    
    # Check frontend/backend focus
    fb_focus = profile.get('frontend_backend_focus', {})
    primary_focus = fb_focus.get('primary_focus', '').lower()
    
    if 'frontend' in primary_focus:
        return 'frontend'
    elif 'backend' in primary_focus:
        return 'backend'
    elif 'full' in primary_focus:
        return 'fullstack'
    
    # Default to specialist
    return 'specialist'


def apply_developer_category_styling(base_style, template, profile, dev_category):
    """
    Apply specialized styling based on developer category.
    
    Args:
        base_style: Base style elements from style_guide
        template: Style template to apply
        profile: Full developer profile
        dev_category: Developer category classification
    
    Returns:
        String: Specialized prompt for the developer category
    """
    # Get developer-specific elements
    character = base_style['character']
    character_traits = ', '.join(base_style['character_traits'])
    primary_language = get_primary_language(profile)
    primary_domain = get_primary_domain(profile)
    
    # Category-specific style adaptations
    if dev_category == 'legendary':
        return create_legendary_contributor_prompt(
            character, character_traits, template, profile
        )
    elif dev_category == 'frontend':
        return create_frontend_specialist_prompt(
            character, character_traits, template, profile, primary_language
        )
    elif dev_category == 'backend':
        return create_backend_engineer_prompt(
            character, character_traits, template, profile, primary_language
        )
    else:
        return create_general_developer_prompt(
            character, character_traits, template, profile, primary_language, primary_domain
        )


def create_legendary_contributor_prompt(character, traits, template, profile):
    """Generate prompt for legendary open-source contributors."""
    high_profile = profile.get('high_profile_contributions', {})
    frameworks = [fw.get('name', '') for fw in high_profile.get('frameworks_contributed', [])]
    
    prompt = f"""Create an epic {template['style_modifier']} depicting a legendary {character} - a masterful architect of open source.

LEGENDARY STATUS: This {character} has contributed to legendary frameworks: {', '.join(frameworks[:3])}

Character Details:
- A {traits} {character} with an aura of wisdom and technical mastery
- Surrounded by flowing streams of code and digital energy representing their massive impact
- Eyes that reflect deep understanding of complex systems
- Posture showing confidence built through years of solving impossible problems

Visual Style:
- {template['artistic_approach']} with heroic proportions
- {template['lighting']} creating a sense of grandeur and respect
- Rich, noble color palette with hints of gold and deep blues
- Background suggesting the vast digital infrastructure they've helped build

Composition:
- {template['composition']} emphasizing their legendary status
- Elements that subtly reference their major contributions without being literal
- Sense of scale showing their impact on the entire software development world

CRITICAL: Maintain 100% animal anatomy - no human facial features whatsoever."""
    
    return prompt


def create_frontend_specialist_prompt(character, traits, template, profile, language):
    """Generate prompt for frontend specialists."""
    prompt = f"""Create a vibrant {template['style_modifier']} of a creative {character} specializing in frontend development.

FRONTEND FOCUS: This {character} crafts beautiful user interfaces and experiences

Character Details:
- A {traits} {character} with keen eyes for design and user experience
- Surrounded by colorful UI elements, design tools, and interface mockups
- Posture showing artistic sensibility combined with technical precision
- Environment filled with vibrant color palettes and modern design elements

Visual Style:
- {template['artistic_approach']} with bright, modern aesthetics
- {template['lighting']} emphasizing clean, contemporary design
- Vibrant color scheme with gradients and modern UI colors
- Background featuring abstract representations of websites, apps, and digital interfaces

Technology Elements:
- Subtle references to {language} and frontend frameworks
- Design tools and creative workspace elements
- Modern devices and responsive layouts

Composition:
- {template['composition']} with emphasis on visual hierarchy and design principles
- Clean, user-friendly aesthetic reflecting frontend sensibilities

CRITICAL: Maintain 100% animal anatomy - no human facial features whatsoever."""
    
    return prompt


def create_backend_engineer_prompt(character, traits, template, profile, language):
    """Generate prompt for backend engineers."""
    prompt = f"""Create a powerful {template['style_modifier']} of a focused {character} mastering backend systems.

BACKEND MASTERY: This {character} builds the robust infrastructure that powers applications

Character Details:
- A {traits} {character} with intense focus and systematic thinking
- Surrounded by flowing data streams, server architectures, and system diagrams
- Posture showing deep concentration and methodical approach
- Environment suggesting powerful computing systems and data processing

Visual Style:
- {template['artistic_approach']} with dark, technical aesthetics
- {template['lighting']} creating dramatic shadows and highlighting system complexity
- Monochromatic color scheme with hints of terminal green and electric blue
- Background featuring abstract server rooms, data centers, and network topologies

Technology Elements:
- Subtle references to {language} and backend technologies
- Database symbols, API endpoints, and system architecture elements
- Terminal windows and command-line interfaces

Composition:
- {template['composition']} emphasizing structure, stability, and systematic design
- Industrial, powerful aesthetic reflecting backend engineering

CRITICAL: Maintain 100% animal anatomy - no human facial features whatsoever."""
    
    return prompt


def create_general_developer_prompt(character, traits, template, profile, language, domain):
    """Generate prompt for general developers."""
    prompt = f"""Create a skilled {template['style_modifier']} of a versatile {character} excelling in {domain} development.

TECHNICAL EXPERTISE: This {character} specializes in {domain} using {language}

Character Details:
- A {traits} {character} with adaptable skills and broad technical knowledge
- Surrounded by various programming tools and development environments
- Posture showing confidence in tackling diverse technical challenges
- Environment reflecting their specific domain focus and programming preferences

Visual Style:
- {template['artistic_approach']} balancing technical and creative elements
- {template['lighting']} providing clear visibility of their technical environment
- Balanced color scheme appropriate for their specialization
- Background representing their specific domain and technical interests

Technology Elements:
- Clear references to {language} and related technologies
- Domain-specific tools and development environments
- Symbols representing their area of expertise

Composition:
- {template['composition']} showing technical competence and specialization
- Professional aesthetic reflecting their specific development focus

CRITICAL: Maintain 100% animal anatomy - no human facial features whatsoever."""
    
    return prompt


# =============================================================================
# PHASE 5: Image-to-Image Prompt Generation  
# =============================================================================

def generate_image_to_image_prompt(profile, transformation_mode='fusion'):
    """
    Generate prompts specifically for image-to-image transformation.
    
    Args:
        profile: Developer profile with analysis data
        transformation_mode: Type of transformation to apply
        
    Returns:
        str: Prompt for image-to-image generation
    """
    from .style_guide import get_enhanced_style_elements
    
    # Get enhanced style elements including Phase 3 analysis
    style = get_enhanced_style_elements(profile)
    
    username = profile.get('username', 'developer')
    primary_language = get_primary_language(profile)
    primary_domain = get_primary_domain(profile)
    
    # Get archetype and artistic style information
    character = style.get('character', 'Wise Owl')
    archetype = style.get('archetype', 'The Developer')
    artistic_style = style.get('artistic_style', 'Professional digital art')
    atmosphere = style.get('atmosphere', 'focused and professional')
    color_palette = style.get('color_palette', 'balanced professional colors')
    
    if transformation_mode == 'tech_enhancement':
        return create_tech_enhancement_prompt(profile, style, primary_language, primary_domain)
    elif transformation_mode == 'character_fusion':
        return create_character_fusion_prompt(profile, style, character, archetype)
    elif transformation_mode == 'artistic_transformation':
        return create_artistic_transformation_prompt(profile, style, artistic_style, atmosphere, color_palette)
    else:
        # Default fusion mode
        return create_fusion_prompt(profile, style, primary_language, primary_domain)


def create_tech_enhancement_prompt(profile, style, language, domain):
    """Generate prompt for subtle tech enhancement."""
    character_traits = ', '.join(style.get('character_traits', ['skilled', 'focused']))
    character = style.get('character', 'Wise Owl')
    
    # Get more technical details
    lang_profile = profile.get('language_profile', {})
    lang_list = list(lang_profile.keys())[:3]  # Top 3 languages
    lang_text = ', '.join(lang_list) if lang_list else language
    
    prompt = f"""Transform this portrait into a {character_traits} {character} representing a {domain} developer, incorporating programming and {domain} development elements.

IMPORTANT: Transform the person into a fully animal character - NO human face or human features should appear. Convert to 100% {character} anatomy while expressing their developer personality through animal features and body language.

TECHNICAL EXPERTISE: This {character} specializes in {domain} using {language} and related technologies including {lang_text}

CHARACTER TRANSFORMATION:
- Convert human features to authentic {character} anatomy and characteristics
- Express {character_traits} qualities through animal eyes, posture, and body language
- Maintain the essence of a skilled developer through confident animal pose and technical environment
- No human facial features - this must be a complete animal transformation

Technical Integration:
- Holographic code snippets or {language} syntax floating around the {character}
- Background featuring {domain} development tools and environments optimized for animal use
- Glow effects suggesting digital mastery and technical expertise
- Color accents reflecting {language} and {domain} aesthetics
- References to {lang_text} technologies and frameworks

Character Enhancement:
- Express {character_traits} qualities through animal body language and environment
- Show confidence and technical competence through animal posture and workspace setup
- Professional developer aesthetic adapted for animal anatomy
- Showcase expertise in {domain} through environmental details designed for animal interaction

Visual Style:
- Professional animal portrait with digital programming enhancements
- Clean, modern lighting that highlights both the {character} and technical elements
- Balanced composition focusing on the animal developer and their technical mastery
- Color scheme: {style.get('color_palette', 'professional blues and teals with warm accents')}

Technology Elements:
- Code overlays and development tools sized for animal interaction
- UI elements and programming interfaces designed for animal use
- Domain-specific symbols and tools ({domain} related) adapted for animal developers
- Modern workspace elements suggesting a skilled animal developer environment
- Visual references to their language portfolio: {lang_text}

Professional Context:
- Environment reflecting their specific domain focus and programming preferences adapted for animal use
- Tools and technologies specific to {domain} development designed for {character} interaction
- Background representing their technical expertise and achievements in an animal-friendly workspace
- Composition showing technical competence and specialization through animal body language

CRITICAL: This must be a complete transformation to {character} - no human facial features, expressions, or anatomy. The animal should embody the developer's expertise through environment, tools, and confident animal body language."""
    
    return prompt


def create_character_fusion_prompt(profile, style, character, archetype):
    """Generate prompt for character fusion transformation."""
    character_traits = ', '.join(style.get('character_traits', ['wise', 'skilled']))
    props = ', '.join(style.get('props', ['tools of mastery', 'symbols of expertise']))
    
    # Get technical details like text-to-image
    primary_language = get_primary_language(profile)
    primary_domain = get_primary_domain(profile)
    
    prompt = f"""Transform this portrait into a {character_traits} {character} who embodies {archetype} qualities, creating a complete animal transformation that represents their coding expertise.

IMPORTANT: Transform the person into a fully animal character - NO human face or human features should appear. Convert to 100% {character} anatomy while expressing their developer personality and {archetype} characteristics.

TECHNICAL EXPERTISE: This {character} specializes in {primary_domain} using {primary_language} and related technologies

FUSION OBJECTIVES:
- Complete transformation to {character} anatomy with no human features remaining
- Express {archetype} qualities through animal posture, environment, and visual elements  
- Create a unique animal developer that honors both the {character} nature and coding expertise
- Show {character_traits} characteristics through animal body language and environment

Character Transformation:
- Full {character} anatomy, facial features, and body structure
- Express {character_traits} qualities through animal eyes, posture, and natural behaviors
- No human facial features or human anatomy - complete animal transformation
- Express the essence of a skilled {primary_domain} developer through confident animal stance and technical environment
- Add {archetype} characteristics through environment, props, and atmospheric elements
- Express {character_traits} qualities through animal body language and environment in technical workspace
- Express the essence of a skilled {primary_domain} developer through confident animal stance and environment

Archetype Elements:
- Surround with {props} that represent their coding expertise and achievements
- Environment should reflect {archetype} workspace and domain of mastery
- Atmospheric effects that suggest wisdom, skill, and technical competence
- Visual metaphors connecting the person to their programming archetype

Technical Integration:
- Clear references to {primary_language} and {primary_domain} technologies
- Domain-specific tools and development environments
- Symbols representing their expertise in {primary_domain}
- Background suggesting mastery of {primary_language} and related technologies

Visual Style:
- {style.get('artistic_style', 'Professional digital art')} aesthetic
- {style.get('atmosphere', 'Confident and masterful')} mood and lighting
- Color palette: {style.get('color_palette', 'rich, professional colors')}
- Composition emphasizing both the person and their coding identity

Technology Integration:
- Subtle {primary_language} coding elements that enhance rather than overwhelm the portrait
- Background suggesting a master {primary_domain} developer's workspace
- Props and tools that reflect their specific programming expertise
- Digital effects that complement the character fusion

CRITICAL: This must be a complete transformation to {character} - no human facial features, expressions, or anatomy. The animal should embody {archetype} qualities and express coding expertise through environment, tools, and confident animal body language."""
    
    return prompt


def create_artistic_transformation_prompt(profile, style, artistic_style, atmosphere, color_palette):
    """Generate prompt for artistic style transformation."""
    primary_language = get_primary_language(profile)
    primary_domain = get_primary_domain(profile)
    character = style.get('character', 'Wise Owl')
    character_traits = ', '.join(style.get('character_traits', ['skilled', 'artistic']))
    
    prompt = f"""Transform this portrait into a {character_traits} {character} using {artistic_style}, creating a stunning artistic interpretation of a {primary_domain} developer.

IMPORTANT: Transform the person into a fully animal character - NO human face or human features should appear. Convert to 100% {character} anatomy while expressing their developer personality through artistic {artistic_style} aesthetics.

ARTISTIC TRANSFORMATION:
- Apply {artistic_style} techniques and aesthetics to create a complete {character} transformation
- No human facial structure or features - full animal anatomy in {artistic_style}
- Transform with {atmosphere} mood and artistic interpretation
- Express {primary_domain} expertise through artistic visual language adapted for animal character

Artistic Style Application:
- Use {artistic_style} color techniques: {color_palette}
- Apply {artistic_style} composition and visual approaches to animal anatomy
- Create {atmosphere} atmosphere through lighting and artistic effects
- Transform background and environment using {artistic_style} aesthetics suitable for {character}

Technical Artistic Elements:
- Artistic interpretation of {primary_language} and {primary_domain} elements integrated with animal character
- Transform coding tools and environments through {artistic_style} lens for animal use
- Visual metaphors for programming expertise using artistic techniques adapted for {character}
- Creative representation of {character} developer identity and technical skills

Composition and Mood:
- {atmosphere} overall mood and emotional tone expressed through animal body language
- Artistic lighting that enhances both the {character} and the style transformation
- Balanced composition honoring both the animal nature and the artistic style
- Professional artistic result suitable for display or portfolio use

Technical Integration:
- Artistically stylized coding elements that complement the overall aesthetic
- {primary_domain} visual themes integrated through {artistic_style} approach
- Subtle programming references transformed through artistic interpretation
- Modern developer workspace reimagined in {artistic_style}

CRITICAL: Create a beautiful artistic transformation into {character} with no human features. The animal should express coding identity through {artistic_style} aesthetics, environment, and confident animal body language."""
    
    return prompt


def create_fusion_prompt(profile, style, language, domain):
    """Generate prompt for general fusion mode."""
    character = style.get('character', 'Wise Owl')
    character_traits = ', '.join(style.get('character_traits', ['skilled', 'dedicated']))
    
    prompt = f"""Create a skillful fusion of this portrait with the essence of a {character_traits} {domain} developer, maintaining the person's recognizable features while expressing their coding expertise.

FUSION APPROACH:
- Preserve the person's facial features and natural appearance as the foundation
- Layer in developer identity through environment, styling, and subtle enhancements
- Express {character_traits} qualities through confident posture and professional atmosphere
- Integrate {language} and {domain} elements in a tasteful, artistic way

Developer Identity Integration:
- Professional developer aesthetic with modern, technical styling
- Environment suggesting expertise in {language} and {domain} development
- Confident, skilled posture expressing mastery of their craft
- Visual elements that tell the story of their coding journey and expertise

Technical Elements:
- Subtle {language} code elements or development tools in the composition
- {domain}-specific background elements and workspace details
- Modern developer environment with professional equipment and setup
- Color scheme reflecting their technical expertise and domain focus

Artistic Enhancement:
- Professional portrait quality with artistic technical enhancements
- Balanced lighting that highlights both the person and their developer identity
- Composition that celebrates both individual personality and coding skills
- Modern, clean aesthetic suitable for professional or portfolio use

Visual Style:
- Contemporary digital art with professional portrait quality
- {style.get('atmosphere', 'Confident and professional')} atmosphere
- Color palette: {style.get('color_palette', 'modern professional colors')}
- Clean, modern composition emphasizing both person and expertise

CRITICAL: Maintain the person's natural appearance and recognizable features while creating an inspiring portrait of a skilled developer."""
    
    return prompt
