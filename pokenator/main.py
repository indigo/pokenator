"""Main module for the Pokenator game

This file now serves as a compatibility layer to maintain backward compatibility
while using the new modular structure. It re-exports all the symbols from the
models and language modules.
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple, Union
from collections import Counter, defaultdict
import unicodedata
import traceback

# Import everything from the new modules
from .models import (
    QuestionGenerator, load_dataset, get_height_category, get_weight_category,
    can_evolve, preprocess_pokemon_dataset, get_type_combinations, get_type_groups
)

from .language import (
    normalize_letter, get_first_letter, HEIGHT_BRACKETS, WEIGHT_BRACKETS,
    COLOR_TRANSLATIONS, HEIGHT_TRANSLATIONS, WEIGHT_TRANSLATIONS,
    ATTRIBUTE_TRANSLATIONS, generate_question, generate_final_guess_question,
    generate_error_message
)

# Define DATA_DIR here for backward compatibility
DATA_DIR = Path(__file__).parent.parent / 'data'

# Re-export all the imported symbols to maintain backward compatibility
__all__ = [
    'QuestionGenerator', 'load_dataset', 'get_height_category', 'get_weight_category',
    'can_evolve', 'preprocess_pokemon_dataset', 'get_type_combinations', 'get_type_groups',
    'normalize_letter', 'get_first_letter', 'HEIGHT_BRACKETS', 'WEIGHT_BRACKETS',
    'COLOR_TRANSLATIONS', 'HEIGHT_TRANSLATIONS', 'WEIGHT_TRANSLATIONS',
    'ATTRIBUTE_TRANSLATIONS', 'DATA_DIR'
]
