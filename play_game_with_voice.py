#!/usr/bin/env python3
"""Command-line interface for the Pokenator game with voice support.

This module provides a CLI for playing the Pokenator game with voice output.
It extends the original play_game.py with voice functionality.
"""

import json
import sys
import time
from pathlib import Path

# Add the project root to the Python path if needed
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from pokenator.models import QuestionGenerator, load_dataset
from pokenator.voice import enable_voice, disable_voice, speak, is_voice_enabled, VoiceEngine

def main():
    """Main game loop for the Pokenator game with voice support."""
    # Enable voice output
    enable_voice()
    
    # Create a voice engine to help with filename generation
    audio_dir = Path("audio")
    language = "fr"
    voice_engine = VoiceEngine(enabled=True, language=language, audio_dir=audio_dir)
    
    # Welcome message
    welcome_msg = "Bienvenue dans Pokenator! Pensez à un Pokémon de la première génération, et je vais essayer de le deviner!"
    print("\n🎮 " + welcome_msg + " 🎮")
    speak(welcome_msg)
    
    instructions = "Répondez par 'o' (oui) ou 'n' (non) aux questions."
    print(instructions + "\n")
    speak("Répondez par 'oui' ou 'non' aux questions.")
    
    # Load dataset
    print("Chargement des données...")
    dataset = load_dataset()
    if not dataset:
        error_msg = "Erreur lors du chargement des données!"
        print(error_msg)
        speak(error_msg)
        return
    
    # Create question generator
    qg = QuestionGenerator(dataset)
    
    # Main game loop
    while True:
        # Generate a question
        thinking_msg = "Réfléchissons..."
        print("\n" + thinking_msg)
        speak(thinking_msg)
        
        question, attr_value = qg.generate_question()
        attribute, value = attr_value
        
        # Handle final guess or error
        if attribute == 'final_guess':
            # Use the base phrase which we know exists
            base_msg = "J'ai trouvé! Votre Pokémon est"
            final_msg = f"{base_msg} {value}!"
            print(final_msg)
            
            # Speak the base phrase first, then the Pokémon name
            speak(base_msg)
            time.sleep(0.5)  # Brief pause
            
            # Try to speak the Pokémon name directly
            # Check for Pokémon name audio file using simple naming convention
            pokemon_audio_path = audio_dir / language / f"{value.lower()}_audio.mp3"
            if pokemon_audio_path.exists():
                # Use the custom audio file directly
                import pygame
                try:
                    pygame.mixer.init()
                    pygame.mixer.music.load(str(pokemon_audio_path))
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)
                except Exception as e:
                    print(f"[VOICE] Error playing Pokémon name audio: {e}")
                    # Fall back to text output
                    print(f"[VOICE] Text: {value}")
            else:
                # Fall back to regular speak function
                speak(value)
            break
        elif attribute == 'error':
            error_msg = "Je ne trouve pas de Pokémon correspondant à vos réponses!"
            print(error_msg)
            speak(error_msg)
            break
        
        # Display remaining Pokémon count
        remaining = qg.get_remaining_count()
        print(f"\nIl reste {remaining} Pokémon possibles...\n")
        
        # Ask the question
        print(question)
        speak(question)
        
        # Get user input
        while True:
            user_input = input("(o/n) > ").strip().lower()
            if user_input in ['o', 'oui', 'y', 'yes']:
                answer = True
                speak("Oui")
                break
            elif user_input in ['n', 'non', 'no']:
                answer = False
                speak("Non")
                break
            else:
                print("Veuillez répondre par 'o' (oui) ou 'n' (non).")
                # Just use text output for this message
                print("Je ne comprends pas. Veuillez répondre par oui ou non.")
        
        # Update the Pokémon set based on the answer
        qg.update_pokemon_set(attribute, value, answer)
    
    # Ask if the user wants to play again
    print("\nVoulez-vous jouer à nouveau? (o/n)")
    # Just use text output for this message
    print("Voulez-vous jouer à nouveau?")
    
    user_input = input("> ").strip().lower()
    if user_input in ['o', 'oui', 'y', 'yes']:
        main()  # Restart the game
    else:
        print("Merci d'avoir joué à Pokenator!")
        # Just use text output for this message
        print("Merci d'avoir joué à Pokenator!")

if __name__ == '__main__':
    main()
