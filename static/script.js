async function showRecommendations(genres) {
  // Show loading state
  resultsSection.classList.remove('d-none');
  const recommendedShows = document.getElementById('recommended-shows');
  recommendedShows.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div><p class="mt-2">Finding the perfect shows for you...</p></div>';

  try {
      const response = await fetch('http://localhost:5000/api/recommend', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify({ genres: genres })
      });

      if (!response.ok) {
          throw new Error('Network response was not ok');
      }

      const data = await response.json();

      // Display results
      recommendedShows.innerHTML = '';
      
      if (data.error) {
          recommendedShows.innerHTML = `
              <div class="col-12 text-center py-4">
                  <h4>${data.error}</h4>
                  <p>Try selecting different genres or taking the quiz again.</p>
              </div>
          `;
          return;
      }

      data.recommendations.forEach(show => {
          const col = document.createElement('div');
          col.className = 'col-md-6 col-lg-4 mb-4';
          col.innerHTML = `
              <div class="card h-100 show-card">
                  <div class="card-body">
                      <h5 class="card-title">${show.title} (${show.year})</h5>
                      <h6 class="card-subtitle mb-2 text-muted">${show.genres}</h6>
                      <p class="card-text">${show.description}</p>
                  </div>
              </div>
          `;
          recommendedShows.appendChild(col);
      });

      // Add genre info
      const genreInfo = document.createElement('div');
      genreInfo.className = 'col-12 text-center mt-3 mb-2';
      genreInfo.innerHTML = `<p class="text-muted">Based on your preferred genres: ${data.genres.join(', ')}</p>`;
      recommendedShows.prepend(genreInfo);

  } catch (error) {
      console.error('Error:', error);
      recommendedShows.innerHTML = `
          <div class="col-12 text-center py-4">
              <h4>Error loading recommendations</h4>
              <p>${error.message}</p>
          </div>
      `;
  }
}

async function sendMessage() {
  const message = chatInput.value.trim();
  if (!message) return;
  
  // Add user message to chat
  const userMessage = document.createElement('div');
  userMessage.className = 'message user-message';
  userMessage.textContent = message;
  chatMessages.appendChild(userMessage);
  
  // Clear input
  chatInput.value = '';
  
  // Scroll to bottom
  chatMessages.scrollTop = chatMessages.scrollHeight;
  
  // Show typing indicator
  const typingIndicator = document.createElement('div');
  typingIndicator.className = 'message bot-message';
  typingIndicator.innerHTML = '<div class="typing"><span></span><span></span><span></span></div>';
  chatMessages.appendChild(typingIndicator);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  
  try {
      const response = await fetch('http://localhost:5000/api/chat', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify({ message: message })
      });

      if (!response.ok) {
          throw new Error('Network response was not ok');
      }

      const data = await response.json();

      // Remove typing indicator
      chatMessages.removeChild(typingIndicator);
      
      // Add bot response
      const botMessage = document.createElement('div');
      botMessage.className = 'message bot-message';
      botMessage.textContent = data.response;
      chatMessages.appendChild(botMessage);
      
      // Scroll to bottom
      chatMessages.scrollTop = chatMessages.scrollHeight;

      if (message.toLowerCase().includes('exit') || message.toLowerCase().includes('bye')) {
          setTimeout(() => {
              chatbotSection.classList.add('d-none');
              mainSection.classList.remove('d-none');
              chatMessages.innerHTML = '<div class="message bot-message">Hello! I\'m Suggestify, your TV show recommendation assistant. How can I help you today?</div>';
          }, 1000);
      }
  } catch (error) {
      console.error('Error:', error);
      // Remove typing indicator
      chatMessages.removeChild(typingIndicator);
      
      const errorMessage = document.createElement('div');
      errorMessage.className = 'message bot-message';
      errorMessage.textContent = "Sorry, I'm having trouble connecting to the server. Please try again later.";
      chatMessages.appendChild(errorMessage);
  }
}

// Update the quiz functions
async function startQuiz() {
  try {
      const response = await fetch('http://localhost:5000/api/quiz/questions');
      if (!response.ok) {
          throw new Error('Failed to load quiz questions');
      }
      const data = await response.json();
      quizData = data.questions;
      currentQuizQuestion = 0;
      genreScores = {};
      loadQuizQuestion(currentQuizQuestion);
  } catch (error) {
      console.error('Error:', error);
      // Fall back to local quiz data if API fails
      loadQuizQuestion(currentQuizQuestion);
  }
}

async function finishQuiz() {
  try {
      const response = await fetch('http://localhost:5000/api/quiz/result', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 
              answers: userAnswers 
          })
      });

      if (!response.ok) {
          throw new Error('Failed to calculate quiz result');
      }

      const data = await response.json();
      selectedGenres = data.genres;
      
      // Show results
      showRecommendations(selectedGenres);
  } catch (error) {
      console.error('Error:', error);
      // Fall back to local calculation if API fails
      const maxScore = Math.max(...Object.values(genreScores));
      selectedGenres = Object.keys(genreScores).filter(genre => genreScores[genre] === maxScore);
      showRecommendations(selectedGenres);
  }
}