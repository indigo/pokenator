"""Language module for the Pokenator game.

This module handles text generation, translations, and language-specific content.
It provides functions for generating questions and formatting text in different languages.
"""
import unicodedata
import os
import csv
from typing import Dict, Any

class LocalizationManager:
    def __init__(self, language: str = 'fr'):
        self.language = language
        self.translations: Dict[str, str] = {}
        self._load_translations()
    
    def _load_translations(self):
        """Load translations from the CSV file."""
        csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'locals.csv')
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.translations[row['key']] = row[self.language]
    
    def get_text(self, key: str, **kwargs) -> str:
        """Get translated text with optional format arguments."""
        text = self.translations.get(key, key)
        if kwargs:
            return text.format(**kwargs)
        return text

# Global instance
localization = LocalizationManager()

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
    return localization.get_text('type_question', type=type_value)

def generate_color_question(color_value: str) -> str:
    """Generate a question about a Pokémon's primary color in French."""
    return localization.get_text('color_question', color=color_value)

def generate_height_question(height_value: str) -> str:
    """Generate a question about a Pokémon's height category in French."""
    return localization.get_text(f'height_{height_value}')

def generate_weight_question(weight_value: str) -> str:
    """Generate a question about a Pokémon's weight category in French."""
    return localization.get_text(f'weight_{weight_value}')

def generate_evolution_question(can_evolve: bool) -> str:
    """Generate a question about a Pokémon's evolution capability in French."""
    key = 'evolution_can' if can_evolve else 'evolution_final'
    return localization.get_text(key)

def generate_final_guess_question(pokemon_name: str) -> str:
    """Generate a final guess question in French."""
    return localization.get_text('final_guess', pokemon=pokemon_name)

def generate_error_message() -> str:
    """Generate an error message in French when no Pokémon matches the criteria."""
    return localization.get_text('error_understanding')

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
        return localization.get_text('default_question', attribute=attribute, value=value)
