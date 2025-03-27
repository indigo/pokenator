"""Language module for the Pokenator game.

This module handles text generation, translations, and language-specific content.
It provides functions for generating questions and formatting text in different languages.
"""
import unicodedata
from typing import Dict, Any, List, Tuple

# Translation dictionaries for attributes
ATTRIBUTE_TRANSLATIONS = {
    "type": "type",
    "primary_color": "primary color",
    "height_category": "height",
    "weight_category": "weight",
    "can_evolve": "evolution"
}

# Translation dictionaries for colors
COLOR_TRANSLATIONS = {
    "red": "rouge",
    "blue": "bleu",
    "green": "vert",
    "yellow": "jaune",
    "brown": "marron",
    "purple": "violet",
    "pink": "rose",
    "gray": "gris",
    "black": "noir",
    "white": "blanc",
    "orange": "orange"
}

# Translation dictionaries for height categories
HEIGHT_TRANSLATIONS = {
    "small": "petit",
    "medium": "moyen",
    "large": "grand"
}

# Translation dictionaries for weight categories
WEIGHT_TRANSLATIONS = {
    "light": "léger",
    "medium": "moyen",
    "heavy": "lourd"
}

# Translation dictionaries for evolution
EVOLUTION_TRANSLATIONS = {
    True: "peut évoluer",
    False: "ne peut pas évoluer"
}

# Size classification brackets based on statistical analysis
HEIGHT_BRACKETS = {
    'small': 0.70,  # ≤ 0.70m
    'medium': 1.50,  # 0.70m - 1.50m
    # large: > 1.50m
}

WEIGHT_BRACKETS = {
    'light': 9.90,   # ≤ 9.90kg
    'medium': 56.25,  # 9.90kg - 56.25kg
    # heavy: > 56.25kg
}

def normalize_letter(letter: str) -> str:
    """Normalize a letter by removing accents and converting to lowercase.
    
    This is used to handle French accents in Pokémon names (e.g., é -> e).
    
    Args:
        letter: Single character to normalize
        
    Returns:
        Normalized character in lowercase
    """
    return unicodedata.normalize('NFKD', letter).encode('ASCII', 'ignore').decode().lower()

def get_first_letter(name: str) -> str:
    """Get the normalized first letter of a name"""
    return normalize_letter(name[0])

def generate_type_question(type_value: str) -> str:
    """Generate a question about a Pokémon's type in French."""
    return f"Est-ce que votre Pokémon est de type {type_value}?"

def generate_color_question(color_value: str) -> str:
    """Generate a question about a Pokémon's primary color in French."""
    french_color = COLOR_TRANSLATIONS.get(color_value, color_value)
    return f"Est-ce que votre Pokémon est principalement {french_color}?"

def generate_height_question(height_value: str) -> str:
    """Generate a question about a Pokémon's height category in French."""
    french_height = HEIGHT_TRANSLATIONS.get(height_value, height_value)
    
    # Add examples for extremes to make questions clearer
    if height_value == 'small':
        return f"Est-ce que votre Pokémon est {french_height} (moins de 0.70m)?"
    elif height_value == 'large':
        return f"Est-ce que votre Pokémon est {french_height} (plus de 1.50m)?"
    else:
        return f"Est-ce que votre Pokémon est {french_height} (en taille)?"

def generate_weight_question(weight_value: str) -> str:
    """Generate a question about a Pokémon's weight category in French."""
    french_weight = WEIGHT_TRANSLATIONS.get(weight_value, weight_value)
    
    # Add examples for extremes to make questions clearer
    if weight_value == 'light':
        return f"Est-ce que votre Pokémon est {french_weight} (moins de 9.90kg)?"
    elif weight_value == 'heavy':
        return f"Est-ce que votre Pokémon est {french_weight} (plus de 56.25kg)?"
    else:
        return f"Est-ce que votre Pokémon est {french_weight} (en poids)?"

def generate_evolution_question(can_evolve: bool) -> str:
    """Generate a question about a Pokémon's evolution capability in French.
    
    Args:
        can_evolve: True to ask if it can evolve, False to ask if it's in final form
        
    Returns:
        A formatted question string in French
    """
    if not can_evolve:  # Asking about final form
        return "Est-ce que votre Pokémon est à sa forme finale? (comme Dracaufeu, Papilusion, etc.)"
    else:  # Asking about ability to evolve
        return "Est-ce que votre Pokémon peut encore évoluer? (comme Salamèche, Carapuce, etc.)"

def generate_final_guess_question(pokemon_name: str) -> str:
    """Generate a final guess question in French."""
    return f"Est-ce que c'est {pokemon_name}?"

def generate_error_message() -> str:
    """Generate an error message in French when no Pokémon matches the criteria."""
    return "Je ne trouve pas de Pokémon correspondant à vos réponses!"

def generate_question(attribute: str, value: Any) -> str:
    """Generate a question based on the attribute and value.
    
    Args:
        attribute: The attribute to ask about (type, primary_color, etc.)
        value: The specific value to ask about
        
    Returns:
        A formatted question string in French
    """
    if attribute == 'type':
        return generate_type_question(value)
    elif attribute == 'primary_color':
        return generate_color_question(value)
    elif attribute == 'height_category':
        return generate_height_question(value)
    elif attribute == 'weight_category':
        return generate_weight_question(value)
    elif attribute == 'can_evolve':
        return generate_evolution_question(value)
    else:
        # Default format for other attributes
        return f"Est-ce que votre Pokémon a {attribute} = {value}?"
