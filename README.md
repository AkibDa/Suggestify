# Suggestify: Your Personalized TV Show Recommendation App 🎬

Suggestify is a web application built with Streamlit that helps you discover your next favorite TV show. Whether you know exactly what genres you're in the mood for, want to explore based on your preferences through an interactive quiz, or need instant recommendations and information from an AI assistant, Suggestify has you covered!

## ✨ Key Features

1.  **Genre-Based Recommendations:**
    * Select your preferred genres (e.g., Comedy, Crime, Drama) from a user-friendly dropdown menu.
    * Receive a list of top-rated TV shows matching your selected genres, sourced from the `imdb_top_5000_tv_shows.csv` dataset.

2.  **Interactive Genre Quiz:**
    * Not sure what you're in the mood for? Take our fun and engaging quiz!
    * Answer questions about your preferred story pace, emotional vibe, setting, and more.
    * Suggestify intelligently analyzes your choices to guess your favorite genres.
    * Get personalized TV show recommendations based on the identified genres.

3.  **AI Chatbot Assistant (Gemini-powered 🤖):**
    * Interact with our intelligent AI chatbot powered by Google's Gemini 2.0 Flash.
    * Ask natural language questions to get TV show recommendations, facts, plot summaries, and suggestions based on your mood or specific preferences.
    * Enjoy quick and smart responses thanks to the power of Gemini.

4.  **Built with Machine Learning:**
    * Leverages machine learning techniques for intelligent genre classification.
    * Utilizes TF-IDF vectorization to understand the relevance of words in TV show titles.
    * Employs a Random Forest model trained to classify shows into different genres.

5.  **Streamlit UI:**
    * Enjoy a clean, modern, and intuitive user interface built with Streamlit.
    * Navigate seamlessly through different functionalities using distinct tabs:
        * **Genre Selection:** Directly choose your favorite genres.
        * **Quiz:** Discover new genres through an interactive quiz.
        * **Chat Assistant:** Engage with the Gemini-powered AI for personalized assistance.

## �� Getting Started

### Prerequisites

* Python 3.x
* pip (Python package installer)

### Installation

1.  Clone the repository:
    ```bash
    git clone [https://github.com/AkibDa/Suggestify.git](https://github.com/AkibDa/Suggestify.git)
    cd Suggestify
    ```

2.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  (Optional) If you plan to run the chatbot, ensure you have the necessary credentials/API key for the Gemini API and configure it in your `chatbot.py` file.

4.  Place the `imdb_top_5000_tv_shows.csv` file in the `data/` directory.

### Running the Application

```bash
streamlit run main.py
```

### 🛠️ Usage

* Genre Selection: Go to the "Genre Selection" tab, choose your favorite genres from the dropdown, and click the "Recommend Shows" button.
* Quiz: Navigate to the "Quiz" tab and answer the questions to let Suggestify guess your preferred genres and provide recommendations.
* Chat Assistant: Open the "Chat Assistant" tab and start chatting with the AI to ask for recommendations, information, or any other queries related to TV shows.

### Author

Sk Akib Ahammed [ahammedskakib@gmail.com]
