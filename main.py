def genre_suggestion():
  print("Let's play a game to find out your preferred genre!")
  print("We will ask you a series of questions to determine your genre preference.")
  print("Please answer with 'yes' or 'no'.")

  quiz_questions = [
    {
      "question": "What kind of story pace do you prefer?",
      "options": {
        "A": "Action",
        "B": "Drama",
        "C": "Comedy",
        "D": ["Fantasy", "Sci-Fi"]
      }
    },
    {
      "question": "Which of these settings excites you the most?",
      "options": {
        "A": ["Crime", "Action"],
        "B": ["Fantasy", "Sci-Fi"],
        "C": "Comedy",
        "D": ["Drama", "Mystery"]
      }
    },
    {
      "question": "What kind of emotional vibe are you going for?",
      "options": {
        "A": "Thriller",
        "B": "Comedy",
        "C": ["Drama", "Romance"],
        "D": ["Fantasy", "Sci-Fi"]
      }
    },
    {
      "question": "Which activity sounds the most fun to watch?",
      "options": {
        "A": ["Crime", "Thriller"],
        "B": ["Sci-Fi", "Fantasy"],
        "C": "Romance",
        "D": "Comedy"
      }
    },
    {
      "question": "Pick your ideal TV character:",
      "options": {
        "A": ["Crime", "Mystery"],
        "B": "Comedy",
        "C": ["Sci-Fi", "Fantasy"],
        "D": ["Drama", "Romance"]
      }
    }
]

  genre_scores = {}
  user_answers = []
  
  for question in quiz_questions:
    print(question["question"])
    for option, genres in question["options"].items():
      if isinstance(genres, list):
        genres = ", ".join(genres)
      print(f"{option}: {genres}")
    answer = input("Your answer (A/B/C/D): ").strip().upper()
    while answer not in question["options"]:
      print("Invalid option. Please choose A, B, C, or D.")
      answer = input("Your answer (A/B/C/D): ").strip().upper()
    user_answers.append(answer)
  print("Thank you for your answers! Let's calculate your preferred genre.")

  for i, answer in enumerate(user_answers):
    options = quiz_questions[i]["options"]
    selected = options.get(answer.upper())

    if not selected:
      continue

    if isinstance(selected, str):
      selected = [selected]

    for genre in selected:
      genre_scores[genre] = genre_scores.get(genre, 0) + 1

  max_score = max(genre_scores.values())
  top_genres = [genre for genre, score in genre_scores.items() if score == max_score]

  return top_genres





if __name__ == "__main__":
  print("Welcome to Suggestify!")
  print("This app will help you find TV shows according to your preferences.")
  
  ans = input("Do you have genre in mind? (yes/no): ").strip().lower()
  if ans == "yes":
    genre = input("Please enter the genre you are interested in: ").strip().lower()
    print(f"Great! You have selected the genre: {genre}.")
  elif ans == "no":
    print("No problem! Let's find out your genre preference.")
    genre_suggestion()
  elif ans == "exit":
    print("Thank you for using Suggestify! Goodbye!")
  else:
    print("Invalid input. Please answer with 'yes' or 'no'.")