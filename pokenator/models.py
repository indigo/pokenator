"""Models module for the Pokenator game.

This module contains the core data models and game logic for the Pokenator game.
It handles data loading, preprocessing, and the main game state management.
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple, Union
from collections import Counter, defaultdict
import traceback

from .language import (
    normalize_letter, get_first_letter, HEIGHT_BRACKETS, WEIGHT_BRACKETS,
    generate_question, generate_final_guess_question, generate_error_message,
    COLOR_TRANSLATIONS, HEIGHT_TRANSLATIONS, WEIGHT_TRANSLATIONS
)

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
    if weight <= WEIGHT_BRACKETS['light']:
        return 'light'
    elif weight <= WEIGHT_BRACKETS['medium']:
        return 'medium'
    else:
        return 'heavy'

def can_evolve(evolution: List[Any], id: int) -> bool:
    """Check if a Pokemon can evolve based on its evolution chain"""
    if not evolution or not isinstance(evolution, list):
        return False
    
    # Find the position of this Pokémon in the evolution chain
    try:
        position = evolution.index(id)
        # If it's not the last in the chain, it can evolve
        can_evolve = position < len(evolution) - 1
        print(f"[DEBUG] ID {id} is at position {position} in chain {evolution}, can_evolve={can_evolve}")
        return can_evolve
    except ValueError:
        # ID not found in evolution chain
        print(f"[DEBUG] ID {id} not found in evolution chain {evolution}")
        return False

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
            print(f"[DEBUG] Processing evolution for {pokemon['nom']} (ID: {pokemon['id']})")
            print(f"[DEBUG] Evolution chain: {pokemon['evolution']}")
            pokemon['can_evolve'] = can_evolve(pokemon['evolution'], pokemon['id'])
            print(f"[DEBUG] {pokemon['nom']} can_evolve = {pokemon['can_evolve']}")
    
    if verbose:
        print(f"[DEBUG] Preprocessing stats:")
        print(f"  - Pokémon with colors: {visual_color_count}/{len(dataset)} ({visual_color_count/len(dataset)*100:.1f}%)")
        print(f"  - Pokémon missing colors: {missing_color_count}/{len(dataset)} ({missing_color_count/len(dataset)*100:.1f}%)")
        print(f"  - Pokémon with height: {height_count}/{len(dataset)} ({height_count/len(dataset)*100:.1f}%)")
        print(f"  - Pokémon missing height: {missing_height_count}/{len(dataset)} ({missing_height_count/len(dataset)*100:.1f}%)")
        
        # Count evolution capability
        can_evolve_count = sum(1 for p in dataset if p.get('can_evolve', False))
        print(f"  - Pokémon that can evolve: {can_evolve_count}/{len(dataset)} ({can_evolve_count/len(dataset)*100:.1f}%)")
        print(f"  - Pokémon that cannot evolve: {len(dataset) - can_evolve_count}/{len(dataset)} ({(len(dataset) - can_evolve_count)/len(dataset)*100:.1f}%)")
        
        # Debug: Print first 3 Pokémon after preprocessing
        for i, pokemon in enumerate(dataset[:3]):
            print(f"[DEBUG] Pokemon {i+1} after preprocessing: {pokemon['nom']}")
            print(f"  - visual_primary_color: {pokemon.get('visual_primary_color', 'missing')}")
            print(f"  - height_category: {pokemon.get('height_category', 'missing')}")
            print(f"  - can_evolve: {pokemon.get('can_evolve', 'missing')}")
    
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
                
    except Exception as e:
        print(f"Error loading dataset: {e}")
        traceback.print_exc()
        return []
        
    # Preprocess the dataset to add derived attributes
    return preprocess_pokemon_dataset(dataset, verbose=True)

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
        """Get distribution of evolution capability in the given set."""
        print("\n[DEBUG] Getting evolution distribution")
        print(f"[DEBUG] Pokémon set size: {len(pokemon_set)}")
        
        values = []
        # Show first few Pokémon for debugging
        for i, pokemon in enumerate(pokemon_set[:5]):
            can_evolve_val = pokemon.get('can_evolve', False)
            print(f"[DEBUG] Pokemon {i+1}: {pokemon['nom']} - can_evolve: {can_evolve_val}")
            values.append(can_evolve_val)
        
        # Process the rest silently
        values.extend([p.get('can_evolve', False) for p in pokemon_set[5:]])
        
        counter = Counter(values)
        print(f"[DEBUG] Evolution capability counts: {dict(counter)}")
        print(f"[DEBUG] True ratio: {counter[True]/len(pokemon_set)*100:.1f}% can evolve")
        return counter
    
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
    
    def calculate_question_score(self, attribute: str, value: Any, pokemon_set: List[Dict[str, Any]]) -> float:
        """Calculate question score using information gain for the attribute-value pair."""
        if attribute == 'can_evolve':
            # Handle boolean attributes using the same scoring as other attributes
            total = len(pokemon_set)
            yes_count = sum(1 for p in pokemon_set if p.get(attribute) == value)
            yes_ratio = yes_count/total * 100
            score = abs(0.5 - yes_ratio/100)  # Changed to match other attribute scoring
            print(f"[DEBUG] Scoring evolution question: yes={yes_count}/{total} ({yes_ratio:.1f}%), score={score:.3f}")
            return score
        else:
            yes_count = 0
            total = len(pokemon_set)
            
            # Get the actual count for this attribute/value
            if attribute == 'type':
                yes_count = self.get_type_distribution(pokemon_set)[value]
            elif attribute == 'primary_color':
                yes_count = self.get_visual_attribute_distribution(pokemon_set, 'primary_color')[value]
            elif attribute == 'height_category':
                yes_count = self.get_height_distribution(pokemon_set)[value]
            elif attribute == 'weight_category':
                yes_count = self.get_weight_distribution(pokemon_set)[value]
                
            yes_ratio = yes_count/total * 100
            score = abs(0.5 - yes_ratio/100)
            print(f"[DEBUG] Scoring {attribute} question for '{value}': yes={yes_count}/{total} ({yes_ratio:.1f}%), score={score:.3f}")
            return score
    
    def evaluate_questions(self) -> List[Tuple[float, str, Tuple[str, Any]]]:
        """Evaluate all possible questions and return ranked list."""
        print("\n[DEBUG] Starting question evaluation")
        
        # Get distributions for each attribute
        distributions = {
            'type': self.get_type_distribution(self.current_pokemon_set),
            'primary_color': self.get_visual_attribute_distribution(self.current_pokemon_set, 'primary_color'),
            'height_category': self.get_height_distribution(self.current_pokemon_set),
            'weight_category': self.get_weight_distribution(self.current_pokemon_set),
            'can_evolve': self.get_evolution_distribution(self.current_pokemon_set),
        }
        
        print("\n[DEBUG] Initial distributions:")
        for attr, dist in distributions.items():
            print(f"[DEBUG] {attr}: {dict(dist)}")
        
        # Filter out empty or singleton distributions
        valid_distributions = {}
        for attr, dist in distributions.items():
            if len(dist) > 1:  # Need at least 2 values to form a meaningful question
                valid_distributions[attr] = dist
            else:
                print(f"[DEBUG] Filtered out {attr} - only has {len(dist)} values: {dict(dist)}")
        
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
                
                score = self.calculate_question_score(attr, value, self.current_pokemon_set)
                
                # Create question text
                question = generate_question(attr, value)
                
                # Debug output
                if attr == 'height_category':
                    french_value = 'petit' if value == 'small' else 'grand' if value == 'large' else 'moyen'
                elif attr == 'weight_category':
                    french_value = 'léger' if value == 'light' else 'lourd' if value == 'heavy' else 'moyen'
                elif attr == 'primary_color':
                    french_value = COLOR_TRANSLATIONS.get(value, value)
                else:
                    french_value = value
                
                print(f"[DEBUG] Created {attr} question for '{value}' (fr: '{french_value}') with score {score}")
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
            return generate_error_message(), ('error', None)
        elif len(self.current_pokemon_set) == 1:
            return generate_final_guess_question(self.current_pokemon_set[0]['nom']), ('final_guess', self.current_pokemon_set[0]['nom'])
            
        questions = self.evaluate_questions()
        if not questions:
            # If we can't generate a good question, make a guess
            return generate_final_guess_question(self.current_pokemon_set[0]['nom']), ('final_guess', self.current_pokemon_set[0]['nom'])
            
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
            elif attr == 'can_evolve':
                count = self.get_evolution_distribution(self.current_pokemon_set)[value]
                
            yes_ratio = count/total * 100
            print(f"{i}. Score: {score:.3f} ({count}/{total} = {yes_ratio:.1f}% yes, {100-yes_ratio:.1f}% no)")
            print(f"   Question: {question}")
        print()
        
        # Use the best question and mark it as asked
        _, question, attr_value = questions[0]
        self.asked_questions.add(attr_value)
        return question, attr_value
    
    def update_pokemon_set(self, attribute: str, value: Any, answer: bool):
        """Update the set of possible Pokémon based on the answer."""
        if attribute == 'error' or attribute == 'final_guess':
            return
            
        print(f"\n[DEBUG] Filtering Pokémon for {attribute}={value} (answer: {answer})")
        print(f"[DEBUG] Before filtering: {len(self.current_pokemon_set)} Pokémon")
        
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
            elif attribute == 'can_evolve':
                # For "is final form" question, we want Pokémon that CANNOT evolve
                # For "can evolve" question, we want Pokémon that CAN evolve
                is_final_form = not pokemon.get('can_evolve', False)
                matches = is_final_form if value == False else not is_final_form
            elif attribute == 'letter':
                matches = normalize_letter(pokemon['nom'][0]) == value
            
            if matches == answer:
                new_set.append(pokemon)
                print(f"[DEBUG] Keeping {pokemon['id']} - {pokemon['nom']} (can_evolve={pokemon.get('can_evolve', 'unknown')})")
        
        self.current_pokemon_set = new_set
        print(f"[DEBUG] After filtering: {len(self.current_pokemon_set)} Pokémon")
    
    def get_remaining_count(self) -> int:
        """Get the number of remaining possible Pokemon"""
        return len(self.current_pokemon_set)
    
    def get_possible_pokemon(self) -> List[str]:
        """Get the names of all possible Pokemon remaining"""
        return [p['nom'] for p in self.current_pokemon_set]
