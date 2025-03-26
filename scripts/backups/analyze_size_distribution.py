import json
from pathlib import Path
import numpy as np
from typing import List, Dict, Any
import matplotlib.pyplot as plt

def load_dataset() -> List[Dict[str, Any]]:
    """Load the Pokemon dataset"""
    with open('data/pokemon_gen1_dataset.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_distribution(values: List[float], title: str, unit: str) -> tuple:
    """Analyze the distribution of values and suggest brackets"""
    # Calculate quartiles and other statistics
    q1, median, q3 = np.percentile(values, [25, 50, 75])
    min_val, max_val = min(values), max(values)
    
    # Print statistics
    print(f"\n{title} Distribution Analysis:")
    print(f"Min: {min_val:.2f} {unit}")
    print(f"Q1 (25th percentile): {q1:.2f} {unit}")
    print(f"Median: {median:.2f} {unit}")
    print(f"Q3 (75th percentile): {q3:.2f} {unit}")
    print(f"Max: {max_val:.2f} {unit}")
    
    # Create histogram
    plt.figure(figsize=(10, 6))
    plt.hist(values, bins=20, edgecolor='black')
    plt.title(f'Distribution of Pokemon {title}')
    plt.xlabel(f'{title} ({unit})')
    plt.ylabel('Number of Pokemon')
    
    # Add vertical lines for quartiles
    plt.axvline(q1, color='r', linestyle='--', label='Q1')
    plt.axvline(median, color='g', linestyle='--', label='Median')
    plt.axvline(q3, color='b', linestyle='--', label='Q3')
    plt.legend()
    
    # Save plot
    plt.savefig(f'data/{title.lower()}_distribution.png')
    plt.close()
    
    return q1, median, q3

def get_size_category(value: float, q1: float, q3: float) -> str:
    """Categorize a value as small, medium, or large based on quartiles"""
    if value <= q1:
        return "small"
    elif value <= q3:
        return "medium"
    else:
        return "large"

def main():
    dataset = load_dataset()
    
    # Extract heights and weights
    heights = [pokemon['taille'] for pokemon in dataset]
    weights = [pokemon['poids'] for pokemon in dataset]
    
    # Analyze height distribution
    height_q1, height_median, height_q3 = analyze_distribution(heights, "Height", "m")
    
    # Analyze weight distribution
    weight_q1, weight_median, weight_q3 = analyze_distribution(weights, "Weight", "kg")
    
    # Print suggested brackets
    print("\nSuggested Size Brackets:")
    print(f"Height (meters):")
    print(f"- Small: ≤ {height_q1:.2f}m")
    print(f"- Medium: {height_q1:.2f}m - {height_q3:.2f}m")
    print(f"- Large: > {height_q3:.2f}m")
    
    print(f"\nWeight (kilograms):")
    print(f"- Light: ≤ {weight_q1:.2f}kg")
    print(f"- Medium: {weight_q1:.2f}kg - {weight_q3:.2f}kg")
    print(f"- Heavy: > {weight_q3:.2f}kg")
    
    # Show some examples
    print("\nExample Classifications:")
    example_pokemon = [
        "Pikachu", "Ronflex", "Salamèche", "Dracolosse", "Métamorph"
    ]
    
    print("\nPokemon Size Classifications:")
    for name in example_pokemon:
        for pokemon in dataset:
            if pokemon['nom'] == name:
                height_cat = get_size_category(pokemon['taille'], height_q1, height_q3)
                weight_cat = get_size_category(pokemon['poids'], weight_q1, weight_q3)
                print(f"\n{name}:")
                print(f"Height: {pokemon['taille']}m ({height_cat})")
                print(f"Weight: {pokemon['poids']}kg ({weight_cat})")
                break

if __name__ == "__main__":
    main()
