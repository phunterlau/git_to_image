"""
A style guide for generating creative and thematic elements in images based on
developer profiles. This includes mappings for programming languages and technical
domains to specific objects, concepts, and narrative themes.
"""

# Describes representative objects, mascots, and thematic concepts for various
# programming languages. The "direct" theme is a literal or common representation,
# while the "extended" theme offers a more narrative or metaphorical interpretation.
LANGUAGE_THEMES = {
    "Python": {
        "direct": "A wise, friendly green python snake, often coiled around a glowing staff or a book titled 'Zen of Python'.",
        "extended": "A wizard's workshop filled with bubbling potions and enchanted brooms (for automation and 'magic'), with a Monty Python-style foot occasionally appearing in the background."
    },
    "JavaScript": {
        "direct": "A dynamic chameleon that changes colors and patterns, representing adaptability.",
        "extended": "A bustling, neon-lit cyberpunk city street at night, representing the vibrant, ever-changing web."
    },
    "TypeScript": {
        "direct": "A dynamic chameleon wearing a set of lightweight, glowing armor or a shield.",
        "extended": "A bustling, neon-lit cyberpunk city with organized, holographic traffic control systems floating above the chaos."
    },
    "Java": {
        "direct": "A sturdy, steaming ceramic coffee mug on an oak table.",
        "extended": "The engine room of a massive starship or an industrial factory with robotic arms assembling complex machinery."
    },
    "C++": {
        "direct": "A high-performance race car engine, gleaming and powerful, with visible, interlocking gears.",
        "extended": "A blacksmith's forge, where the character is crafting a powerful, glowing sword or intricate mechanical device from raw metal."
    },
    "C#": {
        "direct": "A beautifully crafted, multi-paned window looking out onto a serene landscape.",
        "extended": "A set of magical, interlocking building blocks (like LEGOs) that can form any structure, from a castle to a spaceship."
    },
    "Go": {
        "direct": "The friendly, buck-toothed Gopher mascot, often depicted as a busy construction worker or a logistics manager.",
        "extended": "A massive, automated shipping port with cranes efficiently moving containers, or a minimalist Zen garden with perfectly placed stones."
    },
    "Rust": {
        "direct": "Ferris, the friendly crab mascot, polishing a gear until it's rust-free and stronger than new.",
        "extended": "A character wearing advanced climbing gear and a safety harness while scaling a treacherous cliff."
    },
    "Ruby": {
        "direct": "A large, perfectly cut, sparkling ruby gem that refracts light into beautiful patterns.",
        "extended": "An elegant jewelry maker's workbench with exquisite, specialized tools, emphasizing craft and convention ('Rails')."
    },
    # Add other languages as needed
}

# Describes representative objects, environments, and thematic concepts for various
# technical domains. The "direct" theme is a straightforward representation, while
# the "extended" theme provides a more imaginative or story-driven context.
DOMAIN_THEMES = {
    "Web Frontend": {
        "direct": "An artist's palette and easel, where the painting on the canvas comes to life.",
        "extended": "A magical theater stage where the character can instantly change sets, costumes, and lighting. In the audience, viewers hold everything from Nokia flip phones to futuristic transparent tablets."
    },
    "Web Backend": {
        "direct": "The central nervous system of a giant, sleeping creature, with pulses of light traveling along neural pathways.",
        "extended": "The master kitchen of a world-class restaurant during peak service, with the character as the head chef calmly directing a flurry of activity."
    },
    "AI / Machine Learning": {
        "direct": "A glowing, holographic brain that the character is interacting with.",
        "extended": "An ancient observatory where the character uses a telescope to find new constellations, while an abacus and a quantum computer float side-by-side."
    },
    "Data Science & Analytics": {
        "direct": "A detective's office from the 1940s; the character uses a magnifying glass to inspect charts and maps, uncovering hidden clues.",
        "extended": "An ancient library where the character translates forgotten languages from dusty scrolls, assisted by a mechanical calculator and a talking abacus."
    },
    "Mobile Development": {
        "direct": "A timeline of communication devices: a rotary phone, a Nokia 'brick' phone, a flip phone, and a modern smartphone, all displaying notifications for the character.",
        "extended": "The character is a park ranger in a vast national park, using a multi-tool Swiss Army knife to solve various challenges for animal visitors."
    },
    "DevOps / Infrastructure": {
        "direct": "A master gardener tending to the intricate root system of a colossal, continent-sized tree.",
        "extended": "The character is the conductor of a magical train system, where tracks are laid down instantly in front of the train and carriages (containers) can be swapped on the fly."
    },
    "Generalist": {
        "direct": "A workshop filled with a vast array of tools for every trade, from soldering irons to wood-carving knives.",
        "extended": "A character who is a legendary explorer and collector of rare artifacts, with a backpack that contains a solution for every problem."
    },
    # Add other domains as needed
}
