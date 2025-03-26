"""Test script for the Pokenator game"""
from pokenator.main import load_dataset, QuestionGenerator, get_height_category, get_weight_category, normalize_letter
from collections import Counter

def analyze_question_split(generator, question_metadata):
    """Analyze how well a question splits the current set"""
    if not question_metadata:
        return None
    
    attribute, value = question_metadata
    total = len(generator.current_pokemon_set)
    matching = sum(1 for p in generator.current_pokemon_set if (
        value in p['types'] if attribute == 'type'
        else value == p.get('visual_primary_color') if attribute == 'visual_primary_color'
        else value == p.get('height_category') if attribute == 'height_category'
        else value == p.get('weight_category') if attribute == 'weight_category'
        else False
    ))
    split_ratio = matching / total
    return split_ratio

def simulate_game(target_pokemon, verbose=False):
    """Simulate a game with a target Pokemon and analyze each question's split"""
    dataset = load_dataset()
    generator = QuestionGenerator(dataset)
    
    # Find target Pokemon in dataset
    target = next(p for p in dataset if p['nom'] == target_pokemon)
    
    if verbose:
        print(f"\n🎮 Testing with {target['nom']}:")
        print("----------------------------------------")
    
    question_count = 0
    max_questions = 20  # Safety limit
    success = False
    question_types = Counter()
    
    while True:
        # Get next question
        question, metadata = generator.generate_question()
        question_count += 1
        
        # If we have a guess, error, or too many questions, stop
        if metadata is None:
            if verbose:
                print(f"❌ Error: {question}")
            break
        elif metadata[0] == 'final_guess':
            success = metadata[1] == target['nom']
            if verbose:
                print(f"{'✅' if success else '❌'} Final guess: {metadata[1]}")
            break
        elif question_count > max_questions:
            if verbose:
                print("❌ Too many questions")
            break
        
        # Count question types
        attribute, value = metadata
        question_types[attribute] += 1
        
        # Analyze the split
        split_ratio = analyze_question_split(generator, metadata)
        remaining = len(generator.current_pokemon_set)
        
        # Get the correct answer for this Pokemon
        answer = (
            value in target['types'] if attribute == 'type'
            else value == target.get('visual_primary_color') if attribute == 'visual_primary_color'
            else value == target.get('height_category') if attribute == 'height_category'
            else value == target.get('weight_category') if attribute == 'weight_category'
            else False
        )
        
        # Update generator with the answer
        generator.update_pokemon_set(attribute, value, answer)
        
        # Print the question and split analysis if verbose
        if verbose:
            print(f"Q{question_count}: {question}")
            print(f"A: {'oui' if answer else 'non'}")
            if split_ratio is not None:
                print(f"Split: {split_ratio:.1%} yes, {(1-split_ratio):.1%} no")
            print(f"Remaining: {remaining} -> {len(generator.current_pokemon_set)}")
            print("----------------------------------------")
    
    return {
        'pokemon': target_pokemon,
        'success': success,
        'questions': question_count,
        'types': target['types'],
        'question_types': dict(question_types)
    }

def run_sample_test(sample_size=10):
    """Run tests with a sample of Pokémon and analyze results"""
    dataset = load_dataset()
    import random
    
    # Use a fixed seed for reproducible testing
    random.seed(42)
    sample = random.sample(dataset, min(sample_size, len(dataset)))
    
    print(f"🔍 Testing {len(sample)} randomly selected Pokémon...")
    
    all_questions = Counter()
    results = []
    
    for pokemon in sample:
        print(f"\nTesting {pokemon['nom']}...")
        result = simulate_game(pokemon['nom'], verbose=True)
        results.append(result)
        
        # Update question type counts
        for q_type, count in result.get('question_types', {}).items():
            all_questions[q_type] += count
    
    # Calculate statistics
    successes = sum(1 for r in results if r['success'])
    success_rate = successes / len(results)
    avg_questions = sum(r['questions'] for r in results) / len(results)
    
    print("\n📊 Results Summary:")
    print("----------------------------------------")
    print(f"Pokémon tested: {len(results)}")
    print(f"Success rate: {success_rate:.1%} ({successes}/{len(results)})")
    print(f"Average questions needed: {avg_questions:.1f}")
    
    print("\n📋 Question type distribution:")
    total_questions = sum(all_questions.values())
    for q_type, count in all_questions.most_common():
        percentage = count / total_questions * 100
        print(f"- {q_type}: {count} ({percentage:.1f}%)")

def main():
    """Run tests with selected Pokemon and analyze results"""
    import sys
    
    # Check if we're running a sample test
    if len(sys.argv) > 1 and sys.argv[1] == 'sample':
        sample_size = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        run_sample_test(sample_size)
        return
        
    # Otherwise, run a specific test with a single Pokemon
    if len(sys.argv) > 1:
        pokemon_name = sys.argv[1]
        print(f"🔍 Testing specifically with {pokemon_name}...")
        simulate_game(pokemon_name, verbose=True)
        return
    
    # Default - list some popular Pokemon to test with
    print("Usage:")
    print("  python test_game.py <pokemon_name> - Test with specific Pokemon")
    print("  python test_game.py sample [count] - Test with random sample")
    print("\nSuggested Pokemon to test:")
    popular = ["Pikachu", "Dracaufeu", "Florizarre", "Tortank", "Ronflex", "Roucool"]
    for p in popular:
        print(f"  python test_game.py {p}")

if __name__ == "__main__":
    main()
