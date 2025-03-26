"""Command-line interface for the Pokenator game.

This module provides a simple CLI for playing the Pokenator game. It handles:
- Loading the Pokémon dataset
- Running the main game loop
- Processing user input
- Displaying game state and results
"""

import json
from pathlib import Path
from pokenator.main import QuestionGenerator, get_height_category, get_weight_category, preprocess_pokemon_dataset

def main():
    """Main game loop for the Pokenator game."""
    print("\n🎮 Bienvenue dans Pokenator! 🎮")
    print("Pensez à un Pokémon de la première génération, et je vais essayer de le deviner!")
    print("Répondez par 'o' (oui) ou 'n' (non) aux questions.\n")
    
    # Load dataset with simple preprocessing
    data_path = Path(__file__).parent / 'data' / 'pokemon_gen1_dataset_with_colors.json'
    with open(data_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    # Preprocess the dataset using the shared function
    dataset = preprocess_pokemon_dataset(dataset, verbose=False)
    
    # Initialize game
    game = QuestionGenerator(dataset)
    
    while True:
        # Get question
        result = game.generate_question()
        if not isinstance(result, tuple):
            print("Erreur: format de question invalide")
            break
            
        question, (attribute, value) = result
        
        # Display game state
        print(f"\nIl reste {len(game.current_pokemon_set)} Pokémon possibles...")
        if len(game.current_pokemon_set) <= 5:  # Show remaining Pokemon if 5 or fewer
            print(f"Il reste: {', '.join(p['nom'] for p in game.current_pokemon_set)}")
        print(f"\n{question}")
        
        # Handle special question types
        if attribute == 'error':
            print("\nDésolé, je n'arrive pas à deviner votre Pokémon! 😕")
            break
        elif attribute == 'final_guess':
            answer = input("(o/n) > ").lower().strip()
            if answer in ['o', 'oui', 'y', 'yes']:
                print("\n🎉 Super! J'ai trouvé! 🎉")
            else:
                print("\nAh, je me suis trompé! 😢")
            break
        
        # Handle normal questions
        while True:
            answer = input("(o/n) > ").lower().strip()
            if answer in ['o', 'oui', 'y', 'yes']:
                game.update_pokemon_set(attribute, value, True)
                break
            elif answer in ['n', 'non', 'no']:
                game.update_pokemon_set(attribute, value, False)
                break
            else:
                print("Je n'ai pas compris votre réponse. Utilisez 'o' pour oui ou 'n' pour non.")

if __name__ == '__main__':
    main()
