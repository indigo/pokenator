import json
import os

def add_image_urls(input_file, output_file):
    """Add official artwork URLs to Pokemon dataset."""
    with open(input_file, 'r', encoding='utf-8') as f:
        pokemon_data = json.load(f)
    
    # Add image URLs for each Pokemon
    for pokemon in pokemon_data:
        pokemon_id = pokemon['id']
        # Use official artwork URL from PokeAPI
        pokemon['image_url'] = f'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{pokemon_id}.png'
        # Add local path for future use
        pokemon['local_image'] = f'assets/pokemon/{pokemon_id}.png'
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Save updated dataset
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(pokemon_data, f, ensure_ascii=False, indent=2)

def download_images(input_file, output_dir):
    """Download Pokemon images locally."""
    import requests
    from pathlib import Path
    
    with open(input_file, 'r', encoding='utf-8') as f:
        pokemon_data = json.load(f)
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    for pokemon in pokemon_data:
        image_url = pokemon['image_url']
        local_path = Path(output_dir) / f"{pokemon['id']}.png"
        
        if not local_path.exists():
            print(f"Downloading {pokemon['nom']}...")
            response = requests.get(image_url)
            if response.status_code == 200:
                with open(local_path, 'wb') as f:
                    f.write(response.content)
            else:
                print(f"Failed to download {pokemon['nom']}")

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_file = os.path.join(base_dir, 'data', 'pokemon_gen1_dataset.json')
    output_file = os.path.join(base_dir, 'data', 'pokemon_gen1_dataset_with_images.json')
    assets_dir = os.path.join(base_dir, 'assets', 'pokemon')
    
    # Add URLs to dataset
    add_image_urls(input_file, output_file)
    print(f"Added image URLs to dataset: {output_file}")
    
    # Download images
    download_images(output_file, assets_dir)
    print(f"Images downloaded to: {assets_dir}")
