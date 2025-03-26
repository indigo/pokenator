"""Main module for the Pokenator game"""
import json
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple, Union
from collections import Counter, defaultdict
import unicodedata
import traceback

# Size classification brackets based on statistical analysis
HEIGHT_BRACKETS = {
    'small': 0.70,  # ≤ 0.70m
    'medium': 1.50,  # 0.70m - 1.50m
    # large: > 1.50m
}

WEIGHT_BRACKETS = {
    'light': 9.90,   # ≤ 9.90kg
    'medium': 56.25,  # 9.90kg - 56.25kg
    # heavy: > 56.25kg
}

# Translation dictionary for colors and sizes
TRANSLATIONS = {
    'green': 'vert',
    'blue': 'bleu',
    'red': 'rouge',
    'brown': 'marron',
    'purple': 'violet',
    'yellow': 'jaune',
    'pink': 'rose',
    'gray': 'gris',
    'black': 'noir',
    'white': 'blanc',
    'small': 'petit',
    'medium': 'moyen',
    'large': 'grand',
    'light': 'léger',
    'heavy': 'lourd'
}

DATA_DIR = Path(__file__).parent.parent / 'data'

def get_height_category(height: float) -> str:
    """Categorize a Pokémon's height."""
    if height <= HEIGHT_BRACKETS['small']:
        return 'small'
    elif height <= HEIGHT_BRACKETS['medium']:
        return 'medium'
    else:
        return 'large'

def get_weight_category(weight: float) -> str:
    """Classify a Pokemon's weight into light, medium, or heavy"""
    if weight <= 9.90:
        return 'light'
    elif weight <= 56.25:
        return 'medium'
    else:
        return 'heavy'

def normalize_letter(letter: str) -> str:
    """Normalize a letter by removing accents and converting to lowercase.
    
    This is used to handle French accents in Pokémon names (e.g., é -> e).
    
    Args:
        letter: Single character to normalize
        
    Returns:
        Normalized character in lowercase
    """
    return unicodedata.normalize('NFKD', letter).encode('ASCII', 'ignore').decode().lower()

def get_first_letter(name: str) -> str:
    """Get the normalized first letter of a name"""
    return normalize_letter(name[0])

def can_evolve(evolution: List[Any], id: int) -> bool:
    """Check if a Pokemon can evolve based on its evolution chain"""
    if not evolution or not isinstance(evolution, list):
        return False
    return id != evolution[-1]

def preprocess_pokemon_dataset(dataset: List[Dict[str, Any]], verbose: bool = False) -> List[Dict[str, Any]]:
    """Preprocess the Pokémon dataset by adding derived attributes.
    
    Args:
        dataset: List of dictionaries containing raw Pokémon data
        verbose: Whether to print debug information during preprocessing
        
    Returns:
        The processed dataset with added attributes
    """
    visual_color_count = 0
    missing_color_count = 0
    height_count = 0
    missing_height_count = 0
    
    # Debug: Print first 3 Pokémon before preprocessing if verbose
    if verbose:
        for i, pokemon in enumerate(dataset[:3]):
            print(f"[DEBUG] Pokemon {i+1}: {pokemon['nom']}")
            print(f"[DEBUG] Raw data:")
            print(f"  - taille: {pokemon.get('taille', 'missing')}")
            
            if 'visual_attributes' in pokemon:
                print(f"  - visual_attributes: {pokemon['visual_attributes']}")
                if isinstance(pokemon['visual_attributes'], dict) and 'primary_color' in pokemon['visual_attributes']:
                    print(f"  - primary_color: {pokemon['visual_attributes']['primary_color']}")
    
    for pokemon in dataset:
        # Add visual_primary_color
        if ('visual_attributes' in pokemon and 
            isinstance(pokemon['visual_attributes'], dict) and 
            'primary_color' in pokemon['visual_attributes'] and
            pokemon['visual_attributes']['primary_color']):
            
            color = pokemon['visual_attributes']['primary_color']
            if isinstance(color, str):
                pokemon['visual_primary_color'] = color.lower()
                visual_color_count += 1
            else:
                pokemon['visual_primary_color'] = 'unknown'
                missing_color_count += 1
        else:
            pokemon['visual_primary_color'] = 'unknown'
            missing_color_count += 1
        
        # Add height category
        if 'taille' in pokemon and pokemon['taille'] is not None:
            height = pokemon['taille']
            if isinstance(height, (int, float)):
                pokemon['height_category'] = get_height_category(height)
                height_count += 1
            else:
                pokemon['height_category'] = 'unknown'
                missing_height_count += 1
        else:
            pokemon['height_category'] = 'unknown'
            missing_height_count += 1
        
        # Add weight category
        if 'poids' in pokemon and pokemon['poids'] is not None:
            weight = pokemon['poids']
            if isinstance(weight, (int, float)):
                pokemon['weight_category'] = get_weight_category(weight)
            else:
                pokemon['weight_category'] = 'unknown'
        else:
            pokemon['weight_category'] = 'unknown'
            
        # Add evolution capability
        if 'evolution' in pokemon:
            pokemon['can_evolve'] = can_evolve(pokemon['evolution'], pokemon['id'])
    
    if verbose:
        print(f"[DEBUG] Preprocessing stats:")
        print(f"  - Pokémon with colors: {visual_color_count}/{len(dataset)} ({visual_color_count/len(dataset)*100:.1f}%)")
        print(f"  - Pokémon missing colors: {missing_color_count}/{len(dataset)} ({missing_color_count/len(dataset)*100:.1f}%)")
        print(f"  - Pokémon with height: {height_count}/{len(dataset)} ({height_count/len(dataset)*100:.1f}%)")
        print(f"  - Pokémon missing height: {missing_height_count}/{len(dataset)} ({missing_height_count/len(dataset)*100:.1f}%)")
        
        # Debug: Print first 3 Pokémon after preprocessing
        for i, pokemon in enumerate(dataset[:3]):
            print(f"[DEBUG] Pokemon {i+1} after preprocessing: {pokemon['nom']}")
            print(f"  - visual_primary_color: {pokemon.get('visual_primary_color', 'missing')}")
            print(f"  - height_category: {pokemon.get('height_category', 'missing')}")
    
    return dataset

def get_type_combinations(pokemon_set: List[Dict[str, Any]]) -> Dict[Tuple[str, ...], List[Dict[str, Any]]]:
    """Get all type combinations present in the dataset with their Pokemon"""
    combinations = defaultdict(list)
    for pokemon in pokemon_set:
        type_combo = tuple(sorted(pokemon['types']))
        combinations[type_combo].append(pokemon)
    return combinations

def get_type_groups(pokemon_set: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group Pokemon by their types (single or part of dual-type)"""
    groups = defaultdict(list)
    for pokemon in pokemon_set:
        for type_ in pokemon['types']:
            groups[type_].append(pokemon)
    return groups

def load_dataset() -> List[Dict[str, Any]]:
    """Load Pokémon dataset from JSON file and preprocess it."""
    try:
        data_path = DATA_DIR / "pokemon_gen1_dataset_with_colors.json"
        print(f"Loading dataset from: {data_path} (exists: {data_path.exists()})")
        
        with open(data_path, 'r', encoding='utf-8') as f:
            raw_data = f.read()
            print(f"Read {len(raw_data)} bytes from file")
            
            try:
                dataset = json.loads(raw_data)
                print(f"Successfully parsed JSON, loaded {len(dataset)} Pokémon")
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                return []
            
            # Preprocess the dataset with verbose output
            dataset = preprocess_pokemon_dataset(dataset, verbose=True)
            
            return dataset
    except Exception as e:
        print(f"Erreur lors du chargement du dataset: {e}")
        traceback.print_exc()  # Print the full traceback
        return []

class QuestionGenerator:
    """Main class for generating questions and managing game state.
    
    This class implements the core game logic, including:
    - Generating optimal questions based on remaining Pokémon
    - Tracking and updating the set of possible Pokémon
    - Handling edge cases and final guesses
    
    Attributes:
        dataset: List of dictionaries containing Pokémon data
        current_pokemon_set: List of Pokémon still possible based on answers
        type_rarity: Dictionary mapping types to their frequency in the dataset
        asked_questions: Set of questions we've already asked
    """
    
    ATTRIBUTE_TRANSLATIONS = {
        "type": "type",
        "primary_color": "primary color",
        "height_category": "height",
        "weight_category": "weight"
    }
    
    COLOR_TRANSLATIONS = {
        "red": "rouge",
        "blue": "bleu",
        "green": "vert",
        "yellow": "jaune",
        "brown": "marron",
        "purple": "violet",
        "pink": "rose",
        "gray": "gris",
        "black": "noir",
        "white": "blanc",
        "orange": "orange"
    }
    
    HEIGHT_TRANSLATIONS = {
        "small": "petit",
        "medium": "moyen",
        "large": "grand"
    }
    
    WEIGHT_TRANSLATIONS = {
        "light": "léger",
        "medium": "moyen",
        "heavy": "lourd"
    }
    
    def __init__(self, dataset: List[Dict[str, Any]]):
        """Initialize the game with a Pokémon dataset.
        
        Args:
            dataset: List of dictionaries containing Pokémon data with attributes
                    like type, height, weight, color, etc.
        """
        self.dataset = dataset
        self.current_pokemon_set = dataset.copy()
        self.asked_questions = set()  # Track questions we've already asked
        
        # Calculate type rarity for weighting type questions
        all_types = []
        for pokemon in dataset:
            all_types.extend(pokemon['types'])
        self.type_rarity = Counter(all_types)
    
    def get_type_distribution(self, pokemon_set: List[Dict[str, Any]]) -> Counter:
        """Get distribution of Pokémon types in the given set.
        
        Args:
            pokemon_set: List of Pokémon to analyze
            
        Returns:
            Counter mapping types to their frequency
        """
        types = []
        for pokemon in pokemon_set:
            types.extend(pokemon['types'])
        return Counter(types)
    
    def get_visual_attribute_distribution(self, pokemon_set: List[Dict[str, Any]], attribute: str) -> Counter:
        """Get distribution of visual attributes."""
        print(f"\n[DEBUG] Getting visual distribution for '{attribute}'")
        print(f"[DEBUG] Pokémon set size: {len(pokemon_set)}")
        
        counts = Counter()
        key = f"visual_{attribute}"
        
        # Don't show all Pokemon in debug to avoid cluttering
        for i, pokemon in enumerate(pokemon_set[:5]):
            print(f"[DEBUG] Pokemon {i+1}: {pokemon['nom']} - {key}: {pokemon.get(key, 'unknown')}")
            
            # Only count non-unknown values
            if pokemon.get(key, "unknown") != "unknown":
                counts[pokemon.get(key, "unknown")] += 1
        
        # Process the rest silently
        for pokemon in pokemon_set[5:]:
            if pokemon.get(key, "unknown") != "unknown":
                counts[pokemon.get(key, "unknown")] += 1
        
        unknown_count = len(pokemon_set) - sum(counts.values())
        print(f"[DEBUG] Visual attribute counts: {dict(counts)}")
        print(f"[DEBUG] Unknown visual attributes: {unknown_count}/{len(pokemon_set)}")
        return counts

    def get_height_distribution(self, pokemon_set: List[Dict[str, Any]]) -> Counter:
        """Get distribution of height categories."""
        print("\n[DEBUG] Getting height distribution")
        print(f"[DEBUG] Pokémon set size: {len(pokemon_set)}")
        
        counts = Counter()
        
        # Don't show all Pokemon in debug to avoid cluttering
        for i, pokemon in enumerate(pokemon_set[:5]):
            category = pokemon.get("height_category", "unknown")
            print(f"[DEBUG] Pokemon {i+1}: {pokemon['nom']} - height_category: {category}")
            
            # Only count non-unknown values
            if category != "unknown":
                counts[category] += 1
        
        # Process the rest silently
        for pokemon in pokemon_set[5:]:
            category = pokemon.get("height_category", "unknown")
            if category != "unknown":
                counts[category] += 1
        
        unknown_count = len(pokemon_set) - sum(counts.values())
        print(f"[DEBUG] Height category counts: {dict(counts)}")
        print(f"[DEBUG] Unknown height categories: {unknown_count}/{len(pokemon_set)}")
        return counts
    
    def get_weight_distribution(self, pokemon_set: List[Dict[str, Any]]) -> Counter:
        """Get distribution of weight categories."""
        print("\n[DEBUG] Getting weight distribution")
        print(f"[DEBUG] Pokémon set size: {len(pokemon_set)}")
        
        counts = Counter()
        
        # Don't show all Pokemon in debug to avoid cluttering
        for i, pokemon in enumerate(pokemon_set[:5]):
            category = pokemon.get("weight_category", "unknown")
            print(f"[DEBUG] Pokemon {i+1}: {pokemon['nom']} - weight_category: {category}")
            
            # Only count non-unknown values
            if category != "unknown":
                counts[category] += 1
        
        # Process the rest silently
        for pokemon in pokemon_set[5:]:
            category = pokemon.get("weight_category", "unknown")
            if category != "unknown":
                counts[category] += 1
        
        unknown_count = len(pokemon_set) - sum(counts.values())
        print(f"[DEBUG] Weight category counts: {dict(counts)}")
        print(f"[DEBUG] Unknown weight categories: {unknown_count}/{len(pokemon_set)}")
        return counts
    
    def get_evolution_distribution(self, pokemon_set: List[Dict[str, Any]]) -> Counter:
        """Get distribution of evolution capability in the given set.
        
        Args:
            pokemon_set: List of Pokémon to analyze
            
        Returns:
            Counter mapping evolution capability (True/False) to frequency
        """
        values = []
        for pokemon in pokemon_set:
            values.append(pokemon.get('can_evolve', True))
        return Counter(values)
    
    def get_letter_distribution(self, pokemon_set: List[Dict[str, Any]]) -> Counter:
        """Get distribution of first letters in Pokémon names.
        
        Handles French accents by normalizing letters (é -> e).
        
        Args:
            pokemon_set: List of Pokémon to analyze
            
        Returns:
            Counter mapping normalized first letters to their frequency
        """
        values = []
        for pokemon in pokemon_set:
            if pokemon['nom']:
                values.append(normalize_letter(pokemon['nom'][0]))
        return Counter(values)
    
    def evaluate_questions(self) -> List[Tuple[float, str, Tuple[str, Any]]]:
        """Evaluate all possible questions and return ranked list.
        
        Returns:
            List of tuples (score, question text, (attribute, value))
        """
        print(f"\n[DEBUG] Evaluating questions for {len(self.current_pokemon_set)} Pokémon")
        
        # Create distributions
        distributions = {
            'type': self.get_type_distribution(self.current_pokemon_set),
            'primary_color': self.get_visual_attribute_distribution(self.current_pokemon_set, 'primary_color'),
            'height_category': self.get_height_distribution(self.current_pokemon_set),
            'weight_category': self.get_weight_distribution(self.current_pokemon_set),
        }
        
        # Debug output
        print("\n[DEBUG] Distribution summaries:")
        for attr, dist in distributions.items():
            total = sum(dist.values())
            unique = len(dist)
            print(f"[DEBUG] {attr}: {unique} unique values, {total} total")
            print(f"[DEBUG] {attr} distribution: {dict(dist)}")
        
        # Filter out empty or singleton distributions
        valid_distributions = {}
        for attr, dist in distributions.items():
            if len(dist) > 1:  # Need at least 2 values to form a meaningful question
                valid_distributions[attr] = dist
        
        print(f"\n[DEBUG] After filtering - remaining distributions: {list(valid_distributions.keys())}")
        
        questions = []
        
        # Generate questions for each attribute and value
        for attr, dist in valid_distributions.items():
            for value, count in dist.items():
                # Skip already asked questions
                if (attr, value) in self.asked_questions:
                    continue
                    
                # Skip medium/average categories for height and weight
                if (attr == 'height_category' and value == 'medium') or \
                   (attr == 'weight_category' and value == 'medium'):
                    continue
                
                yes_count = count
                no_count = len(self.current_pokemon_set) - yes_count
                
                # Calculate how well this question splits the set
                # Ideal is 50/50 split (score = 0)
                # Worst is 100/0 or 0/100 split (score = 0.5)
                if len(self.current_pokemon_set) > 0:
                    # Get percentage of 'yes' answers
                    yes_percent = yes_count / len(self.current_pokemon_set)
                    # How far from 50% is this?
                    score = abs(0.5 - yes_percent)
                else:
                    score = 0.5  # Worst score
                
                # Create question text (English and French)
                if attr == 'type':
                    question = f"Est-ce que votre Pokémon est de type {value}?"
                    
                elif attr == 'primary_color':
                    # Map English color names to French
                    color_map = {
                        'red': 'rouge', 'blue': 'bleu', 'green': 'vert', 
                        'yellow': 'jaune', 'purple': 'violet', 'brown': 'marron',
                        'pink': 'rose', 'gray': 'gris', 'black': 'noir',
                        'white': 'blanc', 'orange': 'orange'
                    }
                    french_color = color_map.get(value, value)
                    question = f"Est-ce que votre Pokémon est principalement {french_color}?"
                    
                elif attr == 'height_category':
                    # Map height categories to French
                    height_map = {
                        'small': 'petit', 'medium': 'moyen', 'large': 'grand'
                    }
                    french_height = height_map.get(value, value)
                    
                    # Add examples for extremes to make questions clearer
                    if value == 'small':
                        question = f"Est-ce que votre Pokémon est {french_height} (moins de 0.70m)?"
                    elif value == 'large':
                        question = f"Est-ce que votre Pokémon est {french_height} (plus de 1.50m)?"
                    else:
                        question = f"Est-ce que votre Pokémon est {french_height} (en taille)?"
                        
                elif attr == 'weight_category':
                    # Map weight categories to French
                    weight_map = {
                        'light': 'léger', 'medium': 'moyen', 'heavy': 'lourd'
                    }
                    french_weight = weight_map.get(value, value)
                    
                    # Add examples for extremes to make questions clearer
                    if value == 'light':
                        question = f"Est-ce que votre Pokémon est {french_weight} (moins de 9.90kg)?"
                    elif value == 'heavy':
                        question = f"Est-ce que votre Pokémon est {french_weight} (plus de 56.25kg)?"
                    else:
                        question = f"Est-ce que votre Pokémon est {french_weight} (en poids)?"
                else:
                    continue  # Skip unknown attributes
                
                print(f"[DEBUG] Created {attr} question for '{value}' (fr: '{french_height if attr == 'height_category' else french_weight if attr == 'weight_category' else french_color if attr == 'primary_color' else value}') with score {score}")
                questions.append((score, question, (attr, value)))
        
        # Debug total questions
        print(f"\n[DEBUG] Total questions generated: {len(questions)}")
        
        # Sort by score (lower is better)
        return sorted(questions, key=lambda x: x[0])
    
    def generate_question(self) -> Tuple[str, Tuple[str, Any]]:
        """Generate the best question to ask based on current Pokémon set.
        
        Returns:
            Tuple of (question_text, (attribute, value))
            For final guesses: (question_text, ('final_guess', pokemon_name))
            For errors: (error_text, ('error', None))
        """
        if len(self.current_pokemon_set) == 0:
            return "Je ne trouve pas de Pokémon correspondant à vos réponses!", ('error', None)
        elif len(self.current_pokemon_set) == 1:
            return f"Est-ce que c'est {self.current_pokemon_set[0]['nom']}?", ('final_guess', self.current_pokemon_set[0]['nom'])
            
        questions = self.evaluate_questions()
        if not questions:
            # If we can't generate a good question, make a guess
            return f"Est-ce que c'est {self.current_pokemon_set[0]['nom']}?", ('final_guess', self.current_pokemon_set[0]['nom'])
            
        # Display top 5 questions with their split ratios
        print("\nAnalyzing", len(self.current_pokemon_set), "remaining Pokémon...\n")
        print("Top questions being considered:")
        for i, (score, question, (attr, value)) in enumerate(questions[:5], 1):
            count = 0
            total = len(self.current_pokemon_set)
            
            # Get the actual count for this attribute/value
            if attr == 'type':
                count = self.get_type_distribution(self.current_pokemon_set)[value]
            elif attr == 'primary_color':
                count = self.get_visual_attribute_distribution(self.current_pokemon_set, 'primary_color')[value]
            elif attr == 'height_category':
                count = self.get_height_distribution(self.current_pokemon_set)[value]
            elif attr == 'weight_category':
                count = self.get_weight_distribution(self.current_pokemon_set)[value]
                
            yes_ratio = count/total * 100
            print(f"{i}. Score: {score:.3f} ({count}/{total} = {yes_ratio:.1f}% yes, {100-yes_ratio:.1f}% no)")
            print(f"   Question: {question}")
        print()
        
        # Use the best question and mark it as asked
        _, question, attr_value = questions[0]
        self.asked_questions.add(attr_value)
        return question, attr_value
    
    def update_pokemon_set(self, attribute: str, value: Any, answer: bool):
        """Update the set of possible Pokémon based on the answer.
        
        Args:
            attribute: The attribute that was asked about (type, height, etc.)
            value: The specific value that was asked about
            answer: True if the answer was yes, False if no
        """
        if attribute == 'error' or attribute == 'final_guess':
            return
            
        new_set = []
        for pokemon in self.current_pokemon_set:
            matches = False
            
            if attribute == 'type':
                matches = value in pokemon['types']
            elif attribute == 'primary_color':
                matches = pokemon.get('visual_primary_color') == value
            elif attribute == 'height_category':
                matches = pokemon.get('height_category') == value
            elif attribute == 'weight_category':
                matches = pokemon.get('weight_category') == value
            elif attribute == 'evolution':
                matches = not pokemon.get('can_evolve', True)
            elif attribute == 'letter':
                matches = normalize_letter(pokemon['nom'][0]) == value
            
            if matches == answer:
                new_set.append(pokemon)
        
        self.current_pokemon_set = new_set
    
    def get_remaining_count(self) -> int:
        """Get the number of remaining possible Pokemon"""
        return len(self.current_pokemon_set)
    
    def get_possible_pokemon(self) -> List[str]:
        """Get the names of all possible Pokemon remaining"""
        return [p['nom'] for p in self.current_pokemon_set]
