"""Add size categories to the Pokemon dataset"""
import json
from pathlib import Path
from pokenator.main import get_height_category, get_weight_category

def main():
    # Load the dataset
    data_path = Path(__file__).parent.parent / "data" / "pokemon_gen1_dataset_with_colors.json"
    with open(data_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    # Add categories to each Pokemon
    for pokemon in dataset:
        pokemon['size_categories'] = {
            'height': get_height_category(pokemon['taille']),
            'weight': get_weight_category(pokemon['poids'])
        }
    
    # Save the updated dataset
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    print("✅ Added size categories to dataset")

if __name__ == "__main__":
    main()
