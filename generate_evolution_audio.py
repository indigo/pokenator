#!/usr/bin/env python3
"""Script to generate audio files for evolution questions."""
import os
from pathlib import Path
import hashlib
import re
from gtts import gTTS

from pokenator.language import generate_evolution_question

def get_audio_path(text: str, audio_dir: Path, language: str = 'fr') -> Path:
    """Generate a deterministic filename based on the text content."""
    text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
    prefix = re.sub(r'[^a-zA-Z0-9]', '_', text[:30].lower())
    filename = f"{prefix}_{text_hash[:8]}.mp3"
    return audio_dir / language / filename

def generate_audio_file(text: str, audio_path: Path, language: str = 'fr') -> None:
    """Generate an audio file for the given text."""
    print(f"Generating audio for: {text}")
    tts = gTTS(text=text, lang=language, slow=False)
    
    # Create directory if it doesn't exist
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save the audio file
    tts.save(str(audio_path))
    print(f"Saved audio to: {audio_path}")

def main():
    """Generate audio files for evolution questions."""
    # Set up paths
    audio_dir = Path(__file__).parent / 'audio'
    
    # Generate evolution questions
    evolution_questions = [
        generate_evolution_question(True),   # Can evolve
        generate_evolution_question(False),  # Cannot evolve
    ]
    
    # Generate audio files
    for question in evolution_questions:
        audio_path = get_audio_path(question, audio_dir)
        if not audio_path.exists():
            generate_audio_file(question, audio_path)
        else:
            print(f"Audio file already exists: {audio_path}")

if __name__ == "__main__":
    main()
