import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
import google.generativeai as genai
from keys import API_KEY

# Set page config
st.set_page_config(
    page_title="Suggestify - TV Show Recommender",
    page_icon="🍿",
    layout="wide"
)

# Initialize Gemini AI
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")  # Updated model name

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/imdb_top_5000_tv_shows.csv")
        df['genres_clean'] = df['genres'].str.lower()
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(columns=['primaryTitle', 'startYear', 'genres'])

df = load_data()

# Prepare TF-IDF and model
@st.cache_resource
def prepare_model():
    try:
        tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        title_tfidf = tfidf_vectorizer.fit_transform(df['primaryTitle'])
        X = title_tfidf
        y = df['genres_clean']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = RandomForestClassifier(random_state=0)
        model.fit(X_train, y_train)
        return tfidf_vectorizer, model
    except Exception as e:
        st.error(f"Error preparing model: {e}")
        return None, None

tfidf_vectorizer, rf_model = prepare_model()

# Recommendation function
def show_recommendation(genre_input):
    try:
        if isinstance(genre_input, list):
            genre_input_list = [g.strip().lower() for g in genre_input]
        else:
            genre_input_list = [g.strip().lower() for g in genre_input.split(",")]
        
        filtered_df = df[df['genres_clean'].apply(lambda g: all(genre in g for genre in genre_input_list))]
        
        if filtered_df.empty:
            st.warning(f"Sorry, no shows found for the genre(s): {', '.join(genre_input_list)}")
            return
        
        st.subheader("Here are some TV shows you might like:")
        cols = st.columns(3)
        
        for i in range(min(5, len(filtered_df))):
            show = filtered_df.iloc[i]
            with cols[i % 3]:
                st.image("https://via.placeholder.com/300x450?text=TV+Show", width=200)
                st.write(f"**{show['primaryTitle']}** ({show['startYear']})")
                st.caption(f"Genre: {show['genres']}")
                st.write(f"A {show['genres']} show from {show['startYear']}")
    except Exception as e:
        st.error(f"Error generating recommendations: {e}")

# Quiz data
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
                "text": "A courtroom, hospital, or detective's office",
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

# Quiz function
def genre_suggestion():
    st.subheader("Let's find your perfect genre!")
    
    if 'quiz_answers' not in st.session_state:
        st.session_state.quiz_answers = []
        st.session_state.current_question = 0
    
    # Display current question
    question = quiz_questions[st.session_state.current_question]
    st.write(f"**Question {st.session_state.current_question + 1}:** {question['question']}")
    
    # Display options as radio buttons
    option_keys = list(question["options"].keys())
    options_text = [question["options"][key]["text"] for key in option_keys]
    
    selected_option = st.radio(
        "Select your answer:",
        options=options_text,
        key=f"question_{st.session_state.current_question}"
    )
    
    # Find the key for the selected option
    selected_key = None
    for key, opt in question["options"].items():
        if opt["text"] == selected_option:
            selected_key = key
            break
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("Previous") and st.session_state.current_question > 0:
            st.session_state.current_question -= 1
            st.rerun()  # Changed from experimental_rerun()
    
    with col2:
        if st.session_state.current_question < len(quiz_questions) - 1:
            if st.button("Next"):
                # Store the answer
                if len(st.session_state.quiz_answers) <= st.session_state.current_question:
                    st.session_state.quiz_answers.append(selected_key)
                else:
                    st.session_state.quiz_answers[st.session_state.current_question] = selected_key
                st.session_state.current_question += 1
                st.rerun()  # Changed from experimental_rerun()
        else:
            if st.button("Get Results"):
                # Store the final answer
                if len(st.session_state.quiz_answers) <= st.session_state.current_question:
                    st.session_state.quiz_answers.append(selected_key)
                else:
                    st.session_state.quiz_answers[st.session_state.current_question] = selected_key
                
                # Calculate results
                genre_scores = {}
                for i, answer in enumerate(st.session_state.quiz_answers):
                    question = quiz_questions[i]
                    option = question["options"].get(answer, {})
                    
                    for genre in option.get("genres", []):
                        genre_scores[genre] = genre_scores.get(genre, 0) + 1
                
                max_score = max(genre_scores.values()) if genre_scores else 0
                top_genres = [g for g, s in genre_scores.items() if s == max_score]
                
                st.success("Based on your answers, here are the genres you might enjoy:")
                for genre in top_genres:
                    st.write(f"- {genre}")
                
                if st.button("Get Recommendations"):
                    show_recommendation(top_genres)

# Chatbot function
def chatbot():
    st.subheader("TV Show Recommendation Assistant")
    st.write("Ask me anything about TV shows!")
    
    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        st.session_state.chat = model.start_chat(history=[])
    
    # Display chat messages
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Accept user input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.chat.send_message(prompt)
                    st.write(response.text)
                    st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Error getting response: {e}")
                    st.session_state.chat_history.append({"role": "assistant", "content": "Sorry, I encountered an error. Please try again."})

# Main app
def main():
    st.title("🍿 Suggestify - TV Show Recommender")
    st.write("Discover your next favorite TV show!")
    
    tab1, tab2, tab3 = st.tabs(["Genre Selection", "Genre Quiz", "Chat Assistant"])
    
    with tab1:
        st.header("Select Your Preferred Genre")
        available_genres = sorted(df['genres'].str.split(',').explode().str.strip().unique())
        selected_genres = st.multiselect(
            "Choose one or more genres:",
            options=available_genres,
            default=["Comedy"] if "Comedy" in available_genres else []
        )
        
        if st.button("Get Recommendations", key="genre_rec"):
            if not selected_genres:
                st.warning("Please select at least one genre")
            else:
                show_recommendation(selected_genres)
    
    with tab2:
        genre_suggestion()
    
    with tab3:
        chatbot()

if __name__ == '__main__':
    main()