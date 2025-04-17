from flask import Flask, request, jsonify, render_template
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
import google.generativeai as genai
from keys import API_KEY
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

df = pd.read_csv("data/imdb_top_5000_tv_shows.csv")
df['genres_clean'] = df['genres'].str.lower()

tfidf_vectorizer = TfidfVectorizer(stop_words='english')
title_tfidf = tfidf_vectorizer.fit_transform(df['primaryTitle'])
X = title_tfidf
y = df['genres_clean']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
rf_model = RandomForestClassifier(random_state=0)
rf_model.fit(X_train, y_train)

@app.route('/api/recommend', methods=['POST'])
def recommend_shows():
    data = request.json
    genre_input = data.get('genres', '')
    
    if isinstance(genre_input, list):
        genre_input_list = [g.strip().lower() for g in genre_input]
    else:
        genre_input_list = [g.strip().lower() for g in genre_input.split(",")]
    
    filtered_df = df[df['genres_clean'].apply(lambda g: all(genre in g for genre in genre_input_list))]
    
    if filtered_df.empty:
        return jsonify({"error": f"No shows found for the genre(s): {genre_input}"}), 404
    
    recommendations = []
    for i in range(min(5, len(filtered_df))):
        show = filtered_df.iloc[i]
        recommendations.append({
            "title": show['primaryTitle'],
            "year": show['startYear'],
            "genres": show['genres'],
            "description": f"A {show['genres']} show from {show['startYear']}"
        })
    
    return jsonify({"recommendations": recommendations, "genres": genre_input})

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    prompt = data.get('message', '')
    
    if prompt.lower() == 'exit':
        return jsonify({"response": "Goodbye! Have a great day!"})
    
    chat = model.start_chat()
    response = chat.send_message(prompt)
    return jsonify({"response": response.text})

quiz_questions = [
    {
      "question": "What kind of story pace do you prefer?",
      "options": {
        "A": {
          "text": "Fast-paced with twists and action",
          "genres": ["Action"]
        },
        "B": {
          "text": "Slow and emotional with deep character arcs",
          "genres": ["Drama"]
        },
        "C": {
          "text": "Light, funny, and easy to follow",
          "genres": ["Comedy"]
        },
        "D": {
          "text": "Filled with magical or futuristic elements",
          "genres": ["Fantasy", "Sci-Fi"]
        }
      }
    },
    {
      "question": "Which of these settings excites you the most?",
      "options": {
        "A": {
          "text": "Crime-ridden city or warzone",
          "genres": ["Crime", "Action"]
        },
        "B": {
          "text": "A medieval kingdom or distant galaxy",
          "genres": ["Fantasy", "Sci-Fi"]
        },
        "C": {
          "text": "A relatable modern-day town or workplace",
          "genres": ["Comedy"]
        },
        "D": {
          "text": "A courtroom, hospital, or detective’s office",
          "genres": ["Drama", "Mystery"]
        }
      }
    },
    {
      "question": "What kind of emotional vibe are you going for?",
      "options": {
        "A": {
          "text": "Edge-of-your-seat suspense",
          "genres": ["Thriller"]
        },
        "B": {
          "text": "Laughs and good vibes",
          "genres": ["Comedy"]
        },
        "C": {
          "text": "Complex emotions and tearjerkers",
          "genres": ["Drama", "Romance"]
        },
        "D": {
          "text": "Epic, adventurous, and imaginative",
          "genres": ["Fantasy", "Sci-Fi"]
        }
      }
    },
    {
      "question": "Which activity sounds the most fun to watch?",
      "options": {
        "A": {
          "text": "Solving crimes or chasing bad guys",
          "genres": ["Crime", "Thriller"]
        },
        "B": {
          "text": "Exploring other worlds or timelines",
          "genres": ["Sci-Fi", "Fantasy"]
        },
        "C": {
          "text": "Watching characters fall in love",
          "genres": ["Romance"]
        },
        "D": {
          "text": "Friends joking around and living life",
          "genres": ["Comedy"]
        }
      }
    },
    {
      "question": "Pick your ideal TV character:",
      "options": {
        "A": {
          "text": "A witty detective or secret agent",
          "genres": ["Crime", "Mystery"]
        },
        "B": {
          "text": "A sarcastic best friend in a café",
          "genres": ["Comedy"]
        },
        "C": {
          "text": "A time-traveling scientist or wizard",
          "genres": ["Sci-Fi", "Fantasy"]
        },
        "D": {
          "text": "A passionate doctor, lawyer, or artist",
          "genres": ["Drama", "Romance"]
        }
      }
    }
]

@app.route('/api/quiz/questions', methods=['GET'])
def get_quiz_questions():
    return jsonify({"questions": quiz_questions})

@app.route('/api/quiz/result', methods=['POST'])
def calculate_quiz_result():
    data = request.json
    answers = data.get('answers', [])
    
    genre_scores = {}
    for i, choice in enumerate(answers):
        question = quiz_questions[i]
        option = question['options'].get(choice.upper())
        
        if option:
            for genre in option['genres']:
                genre_scores[genre] = genre_scores.get(genre, 0) + 1
    
    max_score = max(genre_scores.values())
    top_genres = [g for g, s in genre_scores.items() if s == max_score]
    
    return jsonify({
        "genres": top_genres,
        "message": "Here are the genres you might enjoy based on your answers"
    })

if __name__ == '__main__':
    app.run(debug=True)