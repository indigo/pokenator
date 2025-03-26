import json
import os
from pathlib import Path
from google import genai
import PIL.Image
from dotenv import load_dotenv

# Predefined visual attributes
VISUAL_ATTRIBUTES = {
    'primary_color': ['red', 'blue', 'green', 'yellow', 'purple', 'brown', 'gray', 'pink', 'white', 'black', 'orange'],
    'body_type': ['bipedal', 'quadrupedal', 'serpentine', 'winged', 'round', 'humanoid', 'fish-like', 'amorphous'],
    'size_appearance': ['tiny', 'small', 'medium', 'large', 'massive'],
    'texture': ['smooth', 'rough', 'scaly', 'furry', 'spiky', 'rocky', 'metallic', 'feathered'],
    'notable_features': ['horns', 'wings', 'tail', 'claws', 'fangs', 'shell', 'fins', 'ears', 'spikes']
}

def load_pokemon_data(file_path):
    """Load Pokemon dataset from JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_pokemon_data(data, file_path):
    """Save Pokemon dataset to JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def analyze_pokemon_image(client, image_path, pokemon_name):
    """Analyze Pokemon image using Gemini Vision API to extract specific visual attributes."""
    try:
        image = PIL.Image.open(image_path)
        
        # Craft a specific prompt for controlled attribute extraction
        attributes_list = "\n".join(
            f"- {attr.replace('_', ' ').title()}: {', '.join(options)}"
            for attr, options in VISUAL_ATTRIBUTES.items()
        )
        
        prompt = f"""Analyze this image of the Pokemon {pokemon_name}.
For each category below, select ONLY ONE option that best matches the Pokemon's appearance:
{attributes_list}

Format your response exactly like this example:
primary_color: blue
body_type: bipedal
size_appearance: medium
texture: smooth
notable_features: wings"""
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt, image]
        )
        
        # Parse response into structured attributes
        attributes = {}
        for line in response.text.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().lower()
                if key in VISUAL_ATTRIBUTES and value in VISUAL_ATTRIBUTES[key]:
                    attributes[key] = value
        
        # Ensure all attributes are present
        for attr in VISUAL_ATTRIBUTES:
            if attr not in attributes:
                attributes[attr] = 'unknown'
        
        return attributes
    except Exception as e:
        print(f"Error analyzing {pokemon_name}: {str(e)}")
        return {attr: 'unknown' for attr in VISUAL_ATTRIBUTES}

def main():
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    # Initialize Gemini client
    client = genai.Client(api_key=api_key)
    
    # Setup paths
    base_dir = Path(__file__).parent.parent
    dataset_path = base_dir / 'data' / 'pokemon_gen1_dataset_with_images.json'
    output_path = base_dir / 'data' / 'pokemon_gen1_dataset_with_attributes.json'
    images_dir = base_dir / 'assets' / 'pokemon'
    
    # Load Pokemon data
    pokemon_data = load_pokemon_data(dataset_path)
    
    # Process each Pokemon
    for pokemon in pokemon_data:
        if pokemon['id'] != 1:  # Only process Bulbizarre for testing
            continue
        print(f"Analyzing {pokemon['nom']}...")
        image_path = images_dir / f"{pokemon['id']}.png"
        
        if image_path.exists():
            attributes = analyze_pokemon_image(client, image_path, pokemon['nom'])
            pokemon['visual_attributes'] = attributes
            print(f"Generated attributes: {attributes}")
        else:
            print(f"Image not found for {pokemon['nom']}")
    
    # Save updated dataset
    save_pokemon_data(pokemon_data, output_path)
    print(f"Updated dataset saved to: {output_path}")

if __name__ == '__main__':
    main()
