# Pokenator 🎮

A Python-based Pokémon guessing game that uses binary search and attribute-based questions to identify Gen 1 Pokémon.

## Features 🌟

- Smart question generation based on multiple Pokémon attributes
- Visual web interface to explore the Pokémon dataset
- Efficient binary search algorithm with attribute weighting
- Support for French language
- Handles edge cases and similar Pokémon gracefully

## Attributes Used for Questions 📊

The game asks questions based on these Pokémon characteristics:

1. **Type** (e.g., "Est-ce que le Pokémon est de type Feu?")
2. **Height Categories**:
   - Small: ≤ 0.70m (25th percentile)
   - Medium: 0.70m - 1.50m (25th to 75th percentile)
   - Large: > 1.50m (above 75th percentile)
3. **Weight Categories**:
   - Light: ≤ 9.90kg (25th percentile)
   - Medium: 9.90kg - 56.25kg (25th to 75th percentile)
   - Heavy: > 56.25kg (above 75th percentile)
4. **Primary Color** (extracted from official artwork)
5. **Evolution Capability** (can/cannot evolve)
6. **First Letter** of the name (used for disambiguation)

## Project Structure 📁

```
pokenator/
├── data/
│   ├── pokemon_gen1_dataset_with_colors.json  # Main dataset with attributes
│   └── ...
├── pokenator/
│   ├── __init__.py
│   └── main.py                               # Core game logic
├── scripts/
│   ├── add_size_categories.py                # Height/weight categorization
│   └── extract_primary_colors.py             # Color extraction from sprites
├── web/
│   ├── app.py                                # Flask web application
│   └── templates/
│       └── index.html                        # Pokemon grid visualization
├── play_game.py                              # CLI game interface
└── test_game.py                              # Game logic tests
```

## Installation 🔧

1. Create and activate the conda environment:
```bash
conda create -n ai_default python=3.10
conda activate ai_default
```

2. Install dependencies:
```bash
pip install requests python-dotenv flask
```

## Usage 🎯

### CLI Game
```bash
python play_game.py
```

### Web Interface
```bash
python web/app.py
```
Then visit http://localhost:5002 to view the Pokémon grid.

## How It Works 🤔

1. **Question Generation**:
   - Analyzes the distribution of each attribute in the remaining Pokémon set
   - Calculates split scores to find questions that best divide the search space
   - Applies attribute-specific modifiers (e.g., bonus for rare types)
   - Uses first letter questions for final disambiguation

2. **Binary Search**:
   - Starts with all 151 Gen 1 Pokémon
   - Each answer eliminates incompatible Pokémon
   - Aims for a roughly 50/50 split with each question
   - Special handling for edge cases (2 remaining Pokémon, similar Pokémon)

3. **Attribute Weighting**:
   - Type questions get a bonus based on type rarity
   - Distinctive colors (yellow, red, blue, green) get a bonus
   - Extreme sizes (small/large, light/heavy) preferred over medium
   - Letter questions get a bonus when few Pokémon remain

## Future Enhancements 🚀

- [ ] Add voice synthesis for questions
- [ ] Expand to later generation Pokémon
- [ ] Add more visual attributes (patterns, shapes)
- [ ] Implement learning from player feedback
- [ ] Add multilingual support

---
Created with ❤️ for Pokémon trainers everywhere