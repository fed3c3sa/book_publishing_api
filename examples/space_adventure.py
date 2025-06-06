# Example Book Configuration: Space Adventure

# Book Configuration
BOOK_TITLE = "Zara's Space Adventure"
STORY_IDEA = """
Zara is a young astronaut who discovers a friendly alien on a distant planet. 
Together, they explore colorful crystal caves and learn about different cultures. 
When Zara's spaceship breaks down, her new alien friend helps her fix it, 
teaching her about friendship across the stars.
"""
NUM_PAGES = 10
AGE_GROUP = "6-8"
LANGUAGE = "English"
ART_STYLE = "space adventure illustration, cosmic colors, friendly aliens, bright stars"

# Character Configuration
CHARACTERS = [
    {
        "type": "text",
        "name": "Zara",
        "character_type": "main",
        "content": """
        Zara is a brave 8-year-old girl with curly brown hair and bright brown eyes. 
        She wears a silver space suit with blue trim and a clear helmet. 
        She has a curious smile and carries a small space tool kit. 
        She's adventurous, kind, and loves learning about new places.
        """,
        "additional_description": ""
    },
    {
        "type": "text",
        "name": "Glimmer",
        "character_type": "main",
        "content": """
        Glimmer is a friendly alien with soft purple skin and large, kind golden eyes. 
        They have three arms and move gracefully on tentacle-like legs. 
        Their body shimmers with tiny sparkles like stars. They have a gentle voice 
        and love showing visitors around their crystal planet.
        """,
        "additional_description": ""
    },
    {
        "type": "text",
        "name": "Crystal Creatures",
        "character_type": "background",
        "content": """
        Small, gem-like creatures that live in the crystal caves. They come in various 
        colors - ruby red, sapphire blue, emerald green. They're about the size of 
        butterflies and make musical chiming sounds when they move.
        """,
        "additional_description": ""
    }
]

# Advanced Configuration
THEMES = ["friendship", "exploration", "cultural diversity", "problem-solving"]
INCLUDE_COVER = True
GENERATE_HTML = True

