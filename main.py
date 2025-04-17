from flask import Flask, request, jsonify, render_template
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
import google.generativeai as genai
from keys import API_KEY, quiz_questions
from flask_cors import CORS

app = Flask(__name__)

# Configure CORS properly
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://127.0.0.1:5000", "http://localhost:5000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Initialize Gemini AI
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# Load data once at startup
try:
    df = pd.read_csv("data/imdb_top_5000_tv_shows.csv")
    df['genres_clean'] = df['genres'].str.lower()
except Exception as e:
    print(f"Error loading data: {e}")
    df = pd.DataFrame(columns=['primaryTitle', 'startYear', 'genres'])
    df['genres_clean'] = ''

# Prepare TF-IDF and model
try:
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    title_tfidf = tfidf_vectorizer.fit_transform(df['primaryTitle'])
    X = title_tfidf
    y = df['genres_clean']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    rf_model = RandomForestClassifier(random_state=0)
    rf_model.fit(X_train, y_train)
except Exception as e:
    print(f"Error initializing model: {e}") 
    
@app.route('/')
def index():
  return render_template('index.html')

@app.route('/api/recommend', methods=['POST', 'OPTIONS'])
def recommend_shows():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    try:
        data = request.get_json()
        genre_input = data.get('genres', '')
        
        if isinstance(genre_input, list):
            genre_input_list = [g.strip().lower() for g in genre_input]
        else:
            genre_input_list = [g.strip().lower() for g in genre_input.split(",")]
        
        filtered_df = df[df['genres_clean'].apply(lambda g: all(genre in g for genre in genre_input_list))]
        
        if filtered_df.empty:
            return _corsify_response(jsonify({"error": f"No shows found for the genre(s): {genre_input}"}), 404)
        
        recommendations = []
        for i in range(min(5, len(filtered_df))):
            show = filtered_df.iloc[i]
            recommendations.append({
                "title": show['primaryTitle'],
                "year": show['startYear'],
                "genres": show['genres'],
                "description": f"A {show['genres']} show from {show['startYear']}"
            })
        
        return _corsify_response(jsonify({
            "recommendations": recommendations, 
            "genres": genre_input
        }))
    except Exception as e:
        return _corsify_response(jsonify({"error": str(e)}), 500)

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    try:
        data = request.get_json()
        prompt = data.get('message', '')
        
        if prompt.lower() == 'exit':
            return _corsify_response(jsonify({"response": "Goodbye! Have a great day!"}))
        
        chat = model.start_chat()
        response = chat.send_message(prompt)
        return _corsify_response(jsonify({"response": response.text}))
    except Exception as e:
        return _corsify_response(jsonify({"error": str(e)}), 500)

quiz_questions = [
    # Your existing quiz questions array
    # ...
]

@app.route('/api/quiz/questions', methods=['GET', 'OPTIONS'])
def get_quiz_questions():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    return _corsify_response(jsonify({"questions": quiz_questions}))

@app.route('/api/quiz/result', methods=['POST', 'OPTIONS'])
def calculate_quiz_result():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    try:
        data = request.get_json()
        answers = data.get('answers', [])
        
        genre_scores = {}
        for i, choice in enumerate(answers):
            question = quiz_questions[i]
            option = question['options'].get(choice.upper(), {})
            
            if option:
                for genre in option.get('genres', []):
                    genre_scores[genre] = genre_scores.get(genre, 0) + 1
        
        max_score = max(genre_scores.values()) if genre_scores else 0
        top_genres = [g for g, s in genre_scores.items() if s == max_score]
        
        return _corsify_response(jsonify({
            "genres": top_genres,
            "message": "Here are the genres you might enjoy based on your answers"
        }))
    except Exception as e:
        return _corsify_response(jsonify({"error": str(e)}), 500)

def _build_cors_preflight_response():
    response = jsonify({"message": "Preflight request accepted"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response

def _corsify_response(response, status_code=200):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response, status_code

if __name__ == '__main__':
    app.run(debug=True, port=5000)