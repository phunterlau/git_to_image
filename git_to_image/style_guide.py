# git_to_image/style_guide.py
# Configuration for artistic mappings

import random

# Animal Characters (non-human, non-offensive)
ANIMAL_CHARACTERS = [
    "Majestic Bear", "Wise Owl", "Industrious Beaver", "Cunning Fox", 
    "Agile Octopus", "Loyal Wolf", "Meticulous Hummingbird", "Playful Otter",
    "GitHub Octopus", "Elegant Cat", "Curious Raccoon", "Noble Eagle"
]

# Drawing Styles
DRAWING_STYLES = [
    "1980s retro wave", "Futuristic cyberpunk", "Chinese ink wash painting", 
    "Steampunk mechanical", "Minimalist line art", "Vibrant pop art", 
    "Dark fantasy concept art", "Blueprint schematic", "Watercolor illustration",
    "Digital pixel art"
]

# Background Environments
BACKGROUND_ENVIRONMENTS = [
    "A server room with glowing racks", "A digital forest with flowing data streams",
    "A library of ancient code scrolls", "A futuristic city skyline",
    "A workshop filled with gears and circuits", "An abstract representation of a neural network",
    "A cozy home office with multiple monitors", "A minimalist workspace with clean lines",
    "A cyberpunk alleyway with neon signs", "A peaceful garden with geometric patterns"
]

# Language to Style Mappings
LANGUAGE_STYLE_MAP = {
    "Python": ["Futuristic cyberpunk", "Minimalist line art", "Digital pixel art"],
    "JavaScript": ["Vibrant pop art", "1980s retro wave", "Blueprint schematic"],
    "Java": ["Steampunk mechanical", "Blueprint schematic", "Dark fantasy concept art"],
    "C": ["1980s retro wave", "Blueprint schematic", "Steampunk mechanical"],
    "C++": ["Dark fantasy concept art", "Steampunk mechanical", "Blueprint schematic"],
    "Rust": ["Steampunk mechanical", "Dark fantasy concept art", "Futuristic cyberpunk"],
    "Go": ["Minimalist line art", "Blueprint schematic", "Futuristic cyberpunk"],
    "TypeScript": ["Vibrant pop art", "Futuristic cyberpunk", "Minimalist line art"],
    "Ruby": ["Watercolor illustration", "Vibrant pop art", "Chinese ink wash painting"],
    "Swift": ["Minimalist line art", "Futuristic cyberpunk", "Vibrant pop art"],
    "Kotlin": ["Vibrant pop art", "Futuristic cyberpunk", "Digital pixel art"],
    "PHP": ["1980s retro wave", "Watercolor illustration", "Vibrant pop art"],
    "R": ["Chinese ink wash painting", "Watercolor illustration", "Minimalist line art"],
    "MATLAB": ["Blueprint schematic", "Minimalist line art", "Futuristic cyberpunk"],
    "Jupyter Notebook": ["Futuristic cyberpunk", "Digital pixel art", "Minimalist line art"]
}

# Domain to Background Mappings
DOMAIN_BACKGROUND_MAP = {
    "AI/ML": ["An abstract representation of a neural network", "A futuristic city skyline", "A digital forest with flowing data streams"],
    "Web Frontend": ["A cozy home office with multiple monitors", "A vibrant digital workspace", "A minimalist workspace with clean lines"],
    "Web Backend": ["A server room with glowing racks", "A workshop filled with gears and circuits", "A cyberpunk alleyway with neon signs"],
    "Game Development": ["A dark fantasy realm", "A cyberpunk alleyway with neon signs", "A workshop filled with gears and circuits"],
    "Data Science": ["A library of ancient code scrolls", "An abstract representation of a neural network", "A peaceful garden with geometric patterns"],
    "DevOps/Infra": ["A server room with glowing racks", "A workshop filled with gears and circuits", "A futuristic city skyline"],
    "Mobile": ["A minimalist workspace with clean lines", "A cozy home office with multiple monitors", "A futuristic city skyline"],
    "Cybersecurity": ["A dark fantasy realm", "A cyberpunk alleyway with neon signs", "A server room with glowing racks"]
}

# Contribution Style to Character Mappings
CONTRIBUTION_CHARACTER_MAP = {
    "Solo Creator": ["Wise Owl", "Majestic Bear", "Noble Eagle"],
    "Collaborator": ["Playful Otter", "Loyal Wolf", "GitHub Octopus"],
    "Architect": ["Industrious Beaver", "Wise Owl", "Meticulous Hummingbird"],
    "Refined Developer": ["Elegant Cat", "Meticulous Hummingbird", "Curious Raccoon"]
}

# Time of Day to Style Modifiers
TIME_STYLE_MAP = {
    "Night Owl": {
        "lighting": "moonlit with dark shadows",
        "color_scheme": "dark blues and purples with neon highlights",
        "atmosphere": "mysterious and focused"
    },
    "Day Coder": {
        "lighting": "bright natural sunlight",
        "color_scheme": "warm yellows and bright colors",
        "atmosphere": "energetic and vibrant"
    },
    "Evening Coder": {
        "lighting": "golden hour with warm shadows",
        "color_scheme": "orange and warm tones",
        "atmosphere": "calm and productive"
    },
    "Morning Coder": {
        "lighting": "soft morning light",
        "color_scheme": "soft pastels and fresh colors",
        "atmosphere": "fresh and optimistic"
    }
}

# Activity Level to Character Traits
ACTIVITY_CHARACTER_MAP = {
    "Highly Active": ["energetic", "dynamic", "powerful"],
    "Consistent": ["steady", "reliable", "focused"],
    "Casual": ["relaxed", "contemplative", "peaceful"],
    "Sporadic": ["mysterious", "spontaneous", "creative"]
}

def get_weighted_style_elements(profile, randomness=0.1):
    """
    Generate weighted style elements based on the user's profile.
    
    Args:
        profile: The user's analyzed profile
        randomness: Float 0-1, amount of randomness to inject (default 0.1 for 10%)
    
    Returns:
        Dictionary with selected style elements
    """
    
    # Initialize style elements
    style_elements = {
        "character": None,
        "drawing_style": None,
        "background": None,
        "lighting": "natural lighting",
        "color_scheme": "balanced colors",
        "atmosphere": "focused",
        "character_traits": []
    }
    
    # Select character based on contribution style
    contribution_style = profile.get('contribution_style', {}).get('primary_style')
    if contribution_style and contribution_style in CONTRIBUTION_CHARACTER_MAP:
        character_options = CONTRIBUTION_CHARACTER_MAP[contribution_style]
        style_elements["character"] = random.choice(character_options)
    else:
        style_elements["character"] = random.choice(ANIMAL_CHARACTERS)
    
    # Select drawing style based on primary language
    language_profile = profile.get('language_profile', {})
    if language_profile:
        primary_language = max(language_profile, key=language_profile.get)
        if primary_language in LANGUAGE_STYLE_MAP:
            style_options = LANGUAGE_STYLE_MAP[primary_language]
            style_elements["drawing_style"] = random.choice(style_options)
        else:
            style_elements["drawing_style"] = random.choice(DRAWING_STYLES)
    else:
        style_elements["drawing_style"] = random.choice(DRAWING_STYLES)
    
    # Select background based on domain focus
    domain_focus = profile.get('domain_focus', [])
    if domain_focus and domain_focus[0] in DOMAIN_BACKGROUND_MAP:
        background_options = DOMAIN_BACKGROUND_MAP[domain_focus[0]]
        style_elements["background"] = random.choice(background_options)
    else:
        style_elements["background"] = random.choice(BACKGROUND_ENVIRONMENTS)
    
    # Apply time-of-day modifiers
    time_of_day = profile.get('commit_cadence', {}).get('time_of_day')
    if time_of_day and time_of_day in TIME_STYLE_MAP:
        time_modifiers = TIME_STYLE_MAP[time_of_day]
        style_elements.update(time_modifiers)
    
    # Add character traits based on activity level
    activity_level = profile.get('commit_cadence', {}).get('activity_level')
    if activity_level and activity_level in ACTIVITY_CHARACTER_MAP:
        style_elements["character_traits"] = ACTIVITY_CHARACTER_MAP[activity_level]
    
    # Apply randomness (I feel lucky factor)
    if random.random() < randomness:
        # Randomly modify one element
        random_element = random.choice(['character', 'drawing_style', 'background'])
        if random_element == 'character':
            style_elements["character"] = random.choice(ANIMAL_CHARACTERS)
        elif random_element == 'drawing_style':
            style_elements["drawing_style"] = random.choice(DRAWING_STYLES)
        elif random_element == 'background':
            style_elements["background"] = random.choice(BACKGROUND_ENVIRONMENTS)
    
    return style_elements


# =============================================================================
# PHASE 3: Advanced Archetype & Artistic Style Mappings
# =============================================================================

# Archetype mappings based on contribution patterns
ARCHETYPE_MAPPING = {
    'feature_creator': {
        'archetype': 'The Architect', 
        'props': ['architectural blueprints', 'a glowing cube of innovation', 'drafting tools'],
        'character_traits': ['visionary', 'creative', 'builder'],
        'pose': 'designing and constructing'
    },
    'bug_fixer': {
        'archetype': 'The Detective', 
        'props': ['a magnifying glass', 'a lantern illuminating dark code', 'investigation tools'],
        'character_traits': ['analytical', 'persistent', 'problem-solver'],
        'pose': 'investigating and solving mysteries'
    },
    'doc_writer': {
        'archetype': 'The Scribe', 
        'props': ['an ancient scroll', 'a glowing quill', 'illuminated manuscripts'],
        'character_traits': ['articulate', 'helpful', 'knowledge-keeper'],
        'pose': 'writing and documenting wisdom'
    },
    'mentor': {
        'archetype': 'The Sage', 
        'props': ['a staff of wisdom', 'floating knowledge orbs', 'teaching tools'],
        'character_traits': ['wise', 'patient', 'guiding'],
        'pose': 'sharing knowledge and mentoring'
    },
    'leader': {
        'archetype': 'The Commander', 
        'props': ['a crown of circuits', 'a scepter of leadership', 'command insignia'],
        'character_traits': ['authoritative', 'decisive', 'inspiring'],
        'pose': 'leading and directing with authority'
    }
}

# Artistic style mappings based on code analysis
ARTISTIC_STYLE_MAPPING = {
    'elegant_minimalist': {
        'style': 'Chinese Ink Wash painting (Shuimohua)',
        'atmosphere': 'serene and balanced',
        'color_palette': 'monochromatic blacks and grays with subtle color accents',
        'composition': 'plenty of negative space, clean lines, essential elements only',
        'philosophy': 'expressing the most with the least'
    },
    'dense_algorithmic': {
        'style': 'Steampunk mechanical illustration',
        'atmosphere': 'intricate and precise',
        'color_palette': 'brass, copper, and steel tones with mechanical details',
        'composition': 'complex interconnected systems, gears and clockwork',
        'philosophy': 'celebrating complexity and mechanical precision'
    },
    'experimental_cutting_edge': {
        'style': 'Cyberpunk glitch art',
        'atmosphere': 'chaotic and futuristic',
        'color_palette': 'neon blues, electric greens, and digital artifacts',
        'composition': 'fragmented reality, digital distortions, bleeding edges',
        'philosophy': 'pushing boundaries and embracing digital chaos'
    },
    'robust_foundational': {
        'style': 'Brutalist architecture art',
        'atmosphere': 'solid and imposing',
        'color_palette': 'concrete grays, industrial metals, earth tones',
        'composition': 'massive geometric forms, structural emphasis, enduring strength',
        'philosophy': 'building solid foundations that last'
    }
}

# Props for legendary contributors (Phase 4 enhancement)
LEGENDARY_PROPS = [
    'a glowing Holy Grail containing their project logo',
    'a radiant crown of flowing code',
    'a scepter topped with their framework symbol', 
    'a throne constructed from server racks',
    'an aura of digital energy and mastery',
    'floating testimonials from grateful developers',
    'a cape woven from commit history'
]

# Enhanced character traits for different developer types
ENHANCED_CHARACTER_TRAITS = {
    'solo_creator': ['independent', 'self-reliant', 'innovative', 'focused'],
    'team_player': ['collaborative', 'supportive', 'communicative', 'adaptable'],
    'mentor_figure': ['wise', 'patient', 'nurturing', 'experienced'],
    'perfectionist': ['meticulous', 'detail-oriented', 'quality-focused', 'precise'],
    'pioneer': ['trailblazing', 'experimental', 'bold', 'risk-taking'],
    'maintainer': ['reliable', 'steady', 'responsible', 'committed']
}


def get_enhanced_style_elements(profile, randomness=0.1):
    """
    Enhanced version that incorporates Phase 3 collaboration and code style analysis.
    
    Args:
        profile: Complete user profile including collaboration_profile and code_style_profile
        randomness: Amount of randomness to inject (0.0 to 1.0)
        
    Returns:
        dict: Enhanced style elements with archetype, artistic style, and props
    """
    # Start with base style elements
    style_elements = get_weighted_style_elements(profile, randomness)
    
    # Phase 3 Enhancement: Apply collaboration-based archetype
    collaboration_profile = profile.get('collaboration_profile', {})
    archetype_indicators = collaboration_profile.get('archetype_indicators', [])
    
    if archetype_indicators:
        # Use the most prominent archetype
        primary_archetype = archetype_indicators[0]
        if primary_archetype in ARCHETYPE_MAPPING:
            archetype_data = ARCHETYPE_MAPPING[primary_archetype]
            style_elements['archetype'] = archetype_data['archetype']
            style_elements['props'] = archetype_data['props']
            style_elements['character_traits'] = archetype_data['character_traits']
            style_elements['pose'] = archetype_data['pose']
    else:
        # Fallback: Use default archetype based on contribution style or domain
        contribution_style = profile.get('contribution_style', {})
        primary_style = contribution_style.get('primary_style', 'Refined Developer')
        
        # Default archetype mapping for users without specific collaboration data
        default_archetype_map = {
            'Solo Creator': 'feature_creator',
            'Collaborator': 'mentor', 
            'Architect': 'feature_creator',
            'Refined Developer': 'feature_creator'
        }
        
        default_archetype = default_archetype_map.get(primary_style, 'feature_creator')
        if default_archetype in ARCHETYPE_MAPPING:
            archetype_data = ARCHETYPE_MAPPING[default_archetype]
            style_elements['archetype'] = archetype_data['archetype']
            style_elements['props'] = archetype_data['props']
            style_elements['character_traits'] = archetype_data['character_traits']
            style_elements['pose'] = archetype_data['pose']
    
    # Phase 3 Enhancement: Apply code style-based artistic style
    code_style_profile = profile.get('code_style_profile', {})
    style_classification = code_style_profile.get('style_classification', 'robust_foundational')
    
    if style_classification in ARTISTIC_STYLE_MAPPING:
        artistic_style = ARTISTIC_STYLE_MAPPING[style_classification]
        style_elements['artistic_style'] = artistic_style['style']
        style_elements['atmosphere'] = artistic_style['atmosphere'] 
        style_elements['color_palette'] = artistic_style['color_palette']
        style_elements['composition'] = artistic_style['composition']
        style_elements['philosophy'] = artistic_style['philosophy']
    
    # Add legendary props for high-profile contributors
    high_profile = profile.get('high_profile_contributions', {})
    if high_profile.get('has_high_profile_contributions'):
        style_elements['legendary_props'] = random.choice(LEGENDARY_PROPS)
    
    return style_elements
