#!/usr/bin/env python3
"""Script to generate voice files for Pokenator using Google Text-to-Speech (gTTS).

This script extracts all possible questions and responses from the game
and generates audio files using the gTTS library, which provides high-quality
speech synthesis in multiple languages.
"""

import sys
import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Set
import hashlib
import re
import time

# Add the project root to the Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# Import Pokenator modules
from pokenator.models import load_dataset, QuestionGenerator
from pokenator.language import (
    generate_type_question, generate_color_question, 
    generate_height_question, generate_weight_question,
    generate_final_guess_question, generate_error_message,
    COLOR_TRANSLATIONS, HEIGHT_TRANSLATIONS, WEIGHT_TRANSLATIONS
)
from pokenator.voice import VoiceEngine

# Try to import gTTS
try:
    from gtts import gTTS
    HAS_TTS = True
    print("gTTS library found. Audio files will be generated.")
except ImportError:
    HAS_TTS = False
    print("gTTS library not found. Install it with: pip install gtts")

def extract_all_questions(dataset: List[Dict[str, Any]]) -> Set[str]:
    """Extract all possible questions from the dataset.
    
    Args:
        dataset: List of dictionaries containing Pokémon data
        
    Returns:
        Set of all possible question strings
    """
    print("Extracting all possible questions...")
    questions = set()
    
    # Create a QuestionGenerator to help with question generation
    qg = QuestionGenerator(dataset)
    
    # Add type questions
    print("Generating type questions...")
    all_types = set()
    for pokemon in dataset:
        all_types.update(pokemon['types'])
    
    for type_value in all_types:
        questions.add(generate_type_question(type_value))
    
    # Add color questions
    print("Generating color questions...")
    all_colors = set()
    for pokemon in dataset:
        if 'visual_primary_color' in pokemon and pokemon['visual_primary_color'] != 'unknown':
            all_colors.add(pokemon['visual_primary_color'])
    
    for color in all_colors:
        questions.add(generate_color_question(color))
    
    # Add height questions
    print("Generating height questions...")
    for height in ['small', 'large']:  # Skip 'medium' as it's not used in questions
        questions.add(generate_height_question(height))
    
    # Add weight questions
    print("Generating weight questions...")
    for weight in ['light', 'heavy']:  # Skip 'medium' as it's not used in questions
        questions.add(generate_weight_question(weight))
    
    # Add final guess questions for all Pokémon
    print("Generating final guess questions...")
    for pokemon in dataset:
        questions.add(generate_final_guess_question(pokemon['nom']))
        # Also add the complete final guess message for each Pokémon
        questions.add(f"J'ai trouvé! Votre Pokémon est {pokemon['nom']}!")
    
    # Add error message
    questions.add(generate_error_message())
    
    # Add yes/no responses
    questions.add("Oui")
    questions.add("Non")
    questions.add("Je ne sais pas")
    
    # Add welcome messages and other game text
    questions.add("Bienvenue dans Pokenator! Pensez à un Pokémon de la première génération, et je vais essayer de le deviner!")
    questions.add("Répondez par 'oui' ou 'non' aux questions.")
    questions.add("Réfléchissons...")
    questions.add("Analysons les possibilités...")
    questions.add("J'ai trouvé! Votre Pokémon est")
    questions.add("Je n'ai pas réussi à deviner votre Pokémon. Essayons encore!")
    questions.add("Voulez-vous jouer à nouveau?")
    questions.add("Merci d'avoir joué à Pokenator!")
    questions.add("Je ne comprends pas. Veuillez répondre par oui ou non.")
    
    print(f"Extracted {len(questions)} unique questions and responses")
    return questions

def generate_audio_file_with_gtts(text: str, output_path: Path, language: str = 'fr') -> bool:
    """Generate an audio file using gTTS.
    
    Args:
        text: Text to convert to speech
        output_path: Path to save the audio file
        language: Language code (e.g., 'fr' for French)
        
    Returns:
        True if generation was successful, False otherwise
    """
    try:
        # Create the gTTS object
        tts = gTTS(text=text, lang=language, slow=False)
        
        # Save the audio file
        tts.save(str(output_path))
        return True
    except Exception as e:
        print(f"Error generating audio file: {e}")
        return False

def generate_audio_files(questions: Set[str], output_dir: Path, language: str = 'fr', force: bool = False) -> None:
    """Generate audio files for all questions using gTTS.
    
    Args:
        questions: Set of question strings to generate audio for
        output_dir: Directory to save audio files
        language: Language code (e.g., 'fr' for French)
        force: Whether to force regeneration of existing files
    """
    if not HAS_TTS:
        print("gTTS library not available. Cannot generate audio files.")
        print("Install it with: pip install gtts")
        print("Here's what would be generated:")
        for i, question in enumerate(sorted(questions)):
            print(f"{i+1}. {question}")
        return
    
    # Create a voice engine for file path generation
    voice_engine = VoiceEngine(enabled=True, language=language, audio_dir=output_dir)
    
    # Generate audio files
    print(f"Generating {len(questions)} audio files in {output_dir}/{language}/...")
    
    # Create the output directory
    lang_dir = output_dir / language
    lang_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate audio files with progress tracking
    total = len(questions)
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for i, question in enumerate(sorted(questions)):
        # Get the audio path
        audio_path = voice_engine._get_audio_path(question)
        
        # Skip if the file already exists and we're not forcing regeneration
        if not force and audio_path.exists():
            print(f"[{i+1}/{total}] Skipping existing file: {audio_path.name}")
            skip_count += 1
            continue
        
        # Generate the audio file
        print(f"[{i+1}/{total}] Generating: {question}")
        
        # Create the directory if it doesn't exist
        audio_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate the audio file using gTTS
        if generate_audio_file_with_gtts(question, audio_path, language):
            success_count += 1
        else:
            error_count += 1
        
        # Sleep briefly to avoid rate limiting
        time.sleep(0.5)
    
    print(f"\nGeneration complete:")
    print(f"- Generated: {success_count}")
    print(f"- Skipped: {skip_count}")
    print(f"- Errors: {error_count}")
    print(f"- Total: {total}")
    print(f"Audio files saved in {output_dir}/{language}/")

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Generate voice files for Pokenator using gTTS")
    parser.add_argument("--output-dir", type=str, default="audio",
                        help="Directory to save audio files (default: audio)")
    parser.add_argument("--language", type=str, default="fr",
                        help="Language code (default: fr)")
    parser.add_argument("--force", action="store_true",
                        help="Force regeneration of existing files")
    args = parser.parse_args()
    
    # Load the dataset
    print("Loading Pokémon dataset...")
    dataset = load_dataset()
    if not dataset:
        print("Failed to load dataset")
        return 1
    
    # Extract all questions
    questions = extract_all_questions(dataset)
    
    # Generate audio files
    output_dir = Path(args.output_dir)
    generate_audio_files(questions, output_dir, args.language, args.force)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
