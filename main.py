import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer

def show_recommendation(genre_input):
  print("Let's find a TV show for you!")

  df = pd.read_csv("data/imdb_top_5000_tv_shows.csv")

  if isinstance(genre_input, list):
    genre_input_list = [g.strip().lower() for g in genre_input]
  else:
    genre_input_list = [g.strip().lower() for g in genre_input.split(",")]

  df['genres_clean'] = df['genres'].str.lower()

  filtered_df = df[df['genres_clean'].apply(lambda g: all(genre in g for genre in genre_input_list))]

  if filtered_df.empty:
    print(f"Sorry, no shows found for the genre(s): {genre_input}")
    return

  tfidf_vectorizer = TfidfVectorizer(stop_words='english')
  title_tfidf = tfidf_vectorizer.fit_transform(df['primaryTitle'])

  X = title_tfidf
  y = df['genres_clean']

  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

  model = RandomForestClassifier(random_state=0)
  model.fit(X_train, y_train)

  print("Here are some TV shows you might like:")
  for i in range(min(5, len(filtered_df))):
    show = filtered_df.iloc[i]
    print(f"- {show['primaryTitle']} ({show['startYear']}) - Genre: {show['genres']}")

def genre_suggestion():
  print("Let's play a game to find out your preferred genre!")
  print("We will ask you a series of questions to determine your genre preference.")

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


  genre_scores = {}
  user_answers = []
  selected_answers = []
  
  for question in quiz_questions:
    print(question["question"])
    for option, option_data in question["options"].items():
      print(f"{option}: {option_data['text']}")
    answer = input("Your answer (A/B/C/D): ").strip().upper()
    while answer not in question["options"]:
      print("Invalid option. Please choose A, B, C, or D.")
      answer = input("Your answer (A/B/C/D): ").strip().upper()
    user_answers.append(answer)
  print("Thank you for your answers! Let's calculate your preferred genre.")

  for i, choice in enumerate(user_answers):
    question = quiz_questions[i]
    option = question["options"].get(choice.upper())

    if not option:
      selected_answers.append("Invalid answer")
      continue

    selected_answers.append(option["text"])

    for genre in option["genres"]:
      genre_scores[genre] = genre_scores.get(genre, 0) + 1

  max_score = max(genre_scores.values())
  top_genres = [g for g, s in genre_scores.items() if s == max_score]

  print("Based on your answers, here are the genres you might enjoy:")
  for genre in top_genres:
    print(f"- {genre}")
  print("Thank you for participating in the quiz!")
  show_recommendation(top_genres)

if __name__ == "__main__":
  print("Welcome to Suggestify!")
  print("This app will help you find TV shows according to your preferences.")
  
  ans = input("Do you have genre in mind? (yes/no): ").strip().lower()
  if ans == "yes":
    genre = input("Please enter the genre you are interested in: ").strip().capitalize()
    print(f"Great! You have selected the genre: {genre}.")
    show_recommendation(genre)
  elif ans == "no":
    print("No problem! Let's find out your genre preference.")
    genre_suggestion()
  elif ans == "exit":
    print("Thank you for using Suggestify! Goodbye!")
  else:
    print("Invalid input. Please answer with 'yes' or 'no'.")