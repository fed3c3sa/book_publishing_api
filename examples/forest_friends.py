# Example Book Configuration: Forest Friends

# Book Configuration
BOOK_TITLE = "The Secret of Whispering Woods"
STORY_IDEA = """
Benny the bear cub gets lost in the forest during his first solo adventure. 
He meets various forest animals who each teach him something important about nature. 
A wise old owl helps him find his way home, but not before Benny discovers 
a beautiful hidden waterfall and learns that being lost can lead to wonderful discoveries.
"""
NUM_PAGES = 12
AGE_GROUP = "3-6"
LANGUAGE = "English"
ART_STYLE = "forest illustration, natural colors, cute animals, magical woodland atmosphere"

# Character Configuration
CHARACTERS = [
    {
        "type": "text",
        "name": "Benny",
        "character_type": "main",
        "content": """
        Benny is a small, fluffy brown bear cub with a round belly and tiny paws. 
        He has warm brown fur, small round ears, and bright curious eyes. 
        He's playful but sometimes gets scared when alone. He has a red bandana 
        around his neck that his mama gave him.
        """,
        "additional_description": ""
    },
    {
        "type": "text",
        "name": "Sage",
        "character_type": "secondary",
        "content": """
        Sage is a wise old owl with beautiful brown and white feathers. 
        She has large, knowing amber eyes and sits on a high branch. 
        Her feathers have intricate patterns and she speaks in a gentle, 
        calming voice. She's patient and kind to all forest creatures.
        """,
        "additional_description": ""
    },
    {
        "type": "text",
        "name": "Pip",
        "character_type": "secondary",
        "content": """
        Pip is an energetic red squirrel with a bushy tail and bright eyes. 
        He's always moving and loves to chatter. His fur is reddish-brown 
        and he often holds acorns in his tiny paws. He's helpful but sometimes 
        talks too fast when he's excited.
        """,
        "additional_description": ""
    },
    {
        "type": "text",
        "name": "Luna",
        "character_type": "secondary",
        "content": """
        Luna is a gentle white rabbit with long ears and a pink nose. 
        She has soft white fur and moves quietly through the forest. 
        She's shy but brave when her friends need help. She knows all 
        the secret paths through the woods.
        """,
        "additional_description": ""
    }
]

# Advanced Configuration
THEMES = ["courage", "friendship", "nature appreciation", "finding your way"]
INCLUDE_COVER = True
GENERATE_HTML = True

