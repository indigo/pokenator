"""Flask web application to display Pokemon in a grid"""
from flask import Flask, render_template
from pathlib import Path
import json

app = Flask(__name__)

def load_pokemon_data():
    """Load Pokemon dataset with attributes"""
    data_path = Path(__file__).parent.parent / 'data' / 'pokemon_gen1_dataset_with_colors.json'
    with open(data_path, 'r', encoding='utf-8') as f:
        return sorted(json.load(f), key=lambda x: x['id'])

@app.route('/')
def index():
    """Display Pokemon grid"""
    pokemon_data = load_pokemon_data()
    return render_template('index.html', pokemon_data=pokemon_data)

if __name__ == '__main__':
    app.run(debug=True, port=5002)
