"""Extract primary colors from Pokemon images using Gemini Flash 2.0"""
import os
import json
import time
import argparse
from pathlib import Path
from PIL import Image
from dotenv import load_dotenv
from google import genai

# Define valid colors as a constant
VALID_COLORS = {'red', 'blue', 'green', 'yellow', 'brown', 'purple', 'pink', 'gray', 'white', 'black'}

def get_primary_color(image_path):
    """Get primary color from image using Gemini Flash 2.0"""
    try:
        # Load API key from .env
        load_dotenv()
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")

        # Load image
        image = Image.open(image_path)
        
        # Initialize Gemini client
        client = genai.Client(api_key=api_key)
        
        # Make request with a very specific prompt
        prompt = f"""Analyze this Pokemon's primary color.
Choose EXACTLY ONE color from this list: {', '.join(sorted(VALID_COLORS))}
Rules:
1. Pick the most dominant color in the Pokemon's body
2. Ignore small details, patterns, or markings
3. Respond with just the color name in lowercase, nothing else
4. You must choose one of the listed colors, no other colors are allowed"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt, image]
        )
        
        # Get color from response
        color = response.text.lower().strip()
        
        # Validate color
        return color if color in VALID_COLORS else 'unknown'
            
    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")
        return 'unknown'

def load_dataset(data_path, colors_path):
    """Load the dataset, preferring the colors dataset if it exists"""
    try:
        # Try to load the colors dataset first
        if colors_path.exists():
            print(f"Loading existing dataset with colors from: {colors_path}")
            with open(colors_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading colors dataset: {e}")
    
    # Fall back to the attributes dataset
    print(f"Loading base dataset from: {data_path}")
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_dataset(dataset, output_path):
    """Save the updated dataset to a file"""
    # Sort dataset by ID before saving
    dataset.sort(key=lambda x: x['id'])
    
    # Clean up any root-level primary_color fields
    for pokemon in dataset:
        if 'primary_color' in pokemon:
            del pokemon['primary_color']
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    print(f"Dataset saved to: {output_path}")

def process_pokemon(pokemon_id, assets_dir, dataset, output_path=None, delay=5):
    """Process a single Pokemon and update its color in the dataset"""
    image_path = assets_dir / f"{pokemon_id}.png"
    
    if not image_path.exists():
        print(f"Image not found for Pokemon #{pokemon_id}")
        return False
    
    # Find Pokemon in dataset
    pokemon = next((p for p in dataset if p['id'] == pokemon_id), None)
    if not pokemon:
        print(f"Pokemon #{pokemon_id} not found in dataset")
        return False
    
    print(f"Processing {pokemon['nom']} (#{pokemon_id})...")
    color = get_primary_color(image_path)
    
    # Update only in visual_attributes
    if 'visual_attributes' not in pokemon:
        pokemon['visual_attributes'] = {}
    pokemon['visual_attributes']['primary_color'] = color
    
    print(f"{pokemon['nom']}'s primary color: {color}")
    
    # Save after each Pokemon if output_path is provided
    if output_path:
        save_dataset(dataset, output_path)
    
    # Wait before next request to avoid rate limiting
    if delay > 0:
        print(f"Waiting {delay} seconds before next request...")
        time.sleep(delay)
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Extract primary colors from Pokemon images')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--id', type=int, help='Process a specific Pokemon ID')
    group.add_argument('--range', type=str, help='Process a range of Pokemon IDs (e.g., 1-151)')
    parser.add_argument('--save', action='store_true', help='Save changes to the dataset')
    parser.add_argument('--delay', type=int, default=5, help='Delay in seconds between requests (default: 5)')
    args = parser.parse_args()

    # Setup paths
    base_dir = Path(__file__).parent.parent
    assets_dir = base_dir / 'assets' / 'pokemon'
    data_path = base_dir / 'data' / 'pokemon_gen1_dataset_with_attributes.json'
    output_path = data_path.parent / 'pokemon_gen1_dataset_with_colors.json'
    
    # Load dataset (preferring the colors dataset if it exists)
    dataset = load_dataset(data_path, output_path)
    
    # Process Pokemon based on arguments
    modified_count = 0
    save_path = output_path if args.save else None
    
    if args.id:
        if process_pokemon(args.id, assets_dir, dataset, save_path, args.delay):
            modified_count += 1
    else:
        start_id, end_id = map(int, args.range.split('-'))
        for pokemon_id in range(start_id, end_id + 1):
            if process_pokemon(pokemon_id, assets_dir, dataset, save_path, args.delay):
                modified_count += 1
    
    print(f"\nProcessed {modified_count} Pokemon")

if __name__ == '__main__':
    main()
