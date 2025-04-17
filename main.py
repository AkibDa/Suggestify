import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
import google.generativeai as genai
from keys import API_KEY

st.set_page_config(
    page_title="Suggestify - TV Show Recommender",
    page_icon="🍿",
    layout="wide"
)

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

@st.cache_data
def load_data():
    return pd.read_csv("data/imdb_top_5000_tv_shows.csv")

df = load_data()
df['genres_clean'] = df['genres'].str.lower()

@st.cache_resource
def prepare_model():
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    title_tfidf = tfidf_vectorizer.fit_transform(df['primaryTitle'])
    X = title_tfidf
    y = df['genres_clean']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(random_state=0)
    model.fit(X_train, y_train)
    return tfidf_vectorizer, model

tfidf_vectorizer, rf_model = prepare_model()

def show_recommendation(genre_input):
    if isinstance(genre_input, list):
        genre_input_list = [g.strip().lower() for g in genre_input]
    else:
        genre_input_list = [g.strip().lower() for g in genre_input.split(",")]
    
    filtered_df = df[df['genres_clean'].apply(lambda g: all(genre in g for genre in genre_input_list))]
    
    if filtered_df.empty:
        st.warning(f"Sorry, no shows found for the genre(s): {genre_input}")
        return
    
    st.subheader("Here are some TV shows you might like:")
    cols = st.columns(3)
    for i in range(min(5, len(filtered_df))):
        show = filtered_df.iloc[i]
        with cols[i % 3]:
            st.write(f"**{show['primaryTitle']}** ({show['startYear']})")
            st.caption(f"Genre: {show['genres']}")
            st.write(f"A {show['genres']} show from {show['startYear']}")

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
    # ... (include all your quiz questions here)
]

def genre_suggestion():
    st.subheader("Let's find your perfect genre!")
    genre_scores = {}
    
    for i, question in enumerate(quiz_questions):
        st.write(f"**Question {i+1}:** {question['question']}")
        option_keys = list(question["options"].keys())
        cols = st.columns(len(option_keys))
        
        selected = None
        for j, key in enumerate(option_keys):
            with cols[j]:
                if st.button(question["options"][key]["text"], key=f"q{i}_opt{j}"):
                    selected = key
        
        if not selected:
            st.warning("Please select an option to continue")
            st.stop()
        
        for genre in question["options"][selected]["genres"]:
            genre_scores[genre] = genre_scores.get(genre, 0) + 1
    
    max_score = max(genre_scores.values())
    top_genres = [g for g, s in genre_scores.items() if s == max_score]
    
    st.success("Based on your answers, here are the genres you might enjoy:")
    for genre in top_genres:
        st.write(f"- {genre}")
    
    if st.button("Get Recommendations"):
        show_recommendation(top_genres)

def chatbot():
    st.subheader("TV Show Recommendation Assistant")
    st.write("Ask me anything about TV shows!")
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        st.session_state.chat = model.start_chat(history=[])
    
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    prompt = st.chat_input("Type your message here...")
    if prompt:
        with st.chat_message("user"):
            st.write(prompt)
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.spinner("Thinking..."):
            response = st.session_state.chat.send_message(prompt)
            
            with st.chat_message("assistant"):
                st.write(response.text)
            st.session_state.chat_history.append({"role": "assistant", "content": response.text})

def main():
    st.title("🍿 Suggestify - TV Show Recommender")
    st.write("Discover your next favorite TV show!")
    
    tab1, tab2, tab3 = st.tabs(["Genre Selection", "Genre Quiz", "Chat Assistant"])
    
    with tab1:
        st.header("Select Your Preferred Genre")
        selected_genres = st.multiselect(
            "Choose one or more genres:",
            options=sorted(df['genres'].str.split(',').explode().str.strip().unique()),
            default=["Comedy"]
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