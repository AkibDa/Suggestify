document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const mainSection = document.getElementById('main-section');
    const genreSelectionSection = document.getElementById('genre-selection-section');
    const quizSection = document.getElementById('quiz-section');
    const resultsSection = document.getElementById('results-section');
    const chatbotSection = document.getElementById('chatbot-section');
    
    // Buttons
    const genreKnowBtn = document.getElementById('genre-know-btn');
    const genreQuizBtn = document.getElementById('genre-quiz-btn');
    const chatbotBtn = document.getElementById('chatbot-btn');
    const backToMainFromGenre = document.getElementById('back-to-main-from-genre');
    const backToMainFromQuiz = document.getElementById('back-to-main-from-quiz');
    const backToMainFromResults = document.getElementById('back-to-main-from-results');
    const exitChatBtn = document.getElementById('exit-chat-btn');
    const sendChatBtn = document.getElementById('send-chat-btn');
    
    // Quiz Elements
    const quizQuestion = document.getElementById('quiz-question');
    const quizOptions = document.getElementById('quiz-options');
    const quizProgress = document.querySelector('.progress-bar');
    
    // Chat Elements
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');
    
    // Data
    const genres = [
        'Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 
        'Documentary', 'Drama', 'Family', 'Fantasy', 'History',
        'Horror', 'Music', 'Mystery', 'Romance', 'Sci-Fi',
        'Thriller', 'War', 'Western'
    ];
    
    let quizData = [];
    let currentQuizQuestion = 0;
    let genreScores = {};
    let selectedGenres = [];
    let userAnswers = [];

    // Initialize genre buttons
    function initializeGenreButtons() {
        const genreButtonsContainer = document.querySelector('.genre-buttons');
        genreButtonsContainer.innerHTML = ''; // Clear existing buttons
        
        genres.forEach(genre => {
            const btn = document.createElement('button');
            btn.className = 'btn btn-outline-primary genre-btn';
            btn.textContent = genre;
            btn.addEventListener('click', () => {
                selectedGenres = [genre];
                showRecommendations(selectedGenres);
            });
            genreButtonsContainer.appendChild(btn);
        });
    }

    // Initialize the application
    function initializeApp() {
        initializeGenreButtons();
        setupEventListeners();
        loadQuizData();
    }

    // Set up all event listeners
    function setupEventListeners() {
        // Navigation buttons
        genreKnowBtn.addEventListener('click', showGenreSelection);
        genreQuizBtn.addEventListener('click', startQuiz);
        chatbotBtn.addEventListener('click', showChatbot);
        
        backToMainFromGenre.addEventListener('click', () => showSection('main'));
        backToMainFromQuiz.addEventListener('click', () => {
            resetQuiz();
            showSection('main');
        });
        backToMainFromResults.addEventListener('click', () => {
            selectedGenres = [];
            showSection('main');
        });
        exitChatBtn.addEventListener('click', () => {
            showSection('main');
            resetChat();
        });
        
        // Chat functionality
        sendChatBtn.addEventListener('click', sendMessage);
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }

    // Load quiz data from backend
    async function loadQuizData() {
        try {
            const response = await fetch('http://localhost:5000/api/quiz/questions');
            if (!response.ok) {
                throw new Error('Failed to load quiz questions');
            }
            const data = await response.json();
            quizData = data.questions;
        } catch (error) {
            console.error('Error loading quiz questions:', error);
            // Fallback to default quiz data
            quizData = [
                // ... (your default quiz data here)
            ];
        }
    }

    // Show different sections of the app
    function showSection(sectionName) {
        // Hide all sections first
        mainSection.classList.add('d-none');
        genreSelectionSection.classList.add('d-none');
        quizSection.classList.add('d-none');
        resultsSection.classList.add('d-none');
        chatbotSection.classList.add('d-none');
        
        // Show the requested section
        switch(sectionName) {
            case 'main':
                mainSection.classList.remove('d-none');
                break;
            case 'genre':
                genreSelectionSection.classList.remove('d-none');
                break;
            case 'quiz':
                quizSection.classList.remove('d-none');
                break;
            case 'results':
                resultsSection.classList.remove('d-none');
                break;
            case 'chat':
                chatbotSection.classList.remove('d-none');
                break;
        }
    }

    // Genre selection flow
    function showGenreSelection() {
        showSection('genre');
    }

    // Quiz flow
    function startQuiz() {
        currentQuizQuestion = 0;
        genreScores = {};
        userAnswers = [];
        showSection('quiz');
        loadQuizQuestion(currentQuizQuestion);
    }

    function loadQuizQuestion(index) {
        if (index >= quizData.length) {
            finishQuiz();
            return;
        }
        
        const question = quizData[index];
        quizQuestion.textContent = question.question;
        quizOptions.innerHTML = '';
        
        // Update progress
        const progress = ((index) / quizData.length) * 100;
        quizProgress.style.width = `${progress}%`;
        
        // Create option buttons
        Object.entries(question.options).forEach(([key, option]) => {
            const optionDiv = document.createElement('div');
            optionDiv.className = 'col-md-6';
            
            const card = document.createElement('div');
            card.className = 'card quiz-option';
            card.innerHTML = `
                <div class="card-body">
                    <h5 class="card-title">${key}</h5>
                    <p class="card-text">${option.text}</p>
                </div>
            `;
            
            card.addEventListener('click', () => {
                // Record the answer
                userAnswers.push(key);
                
                // Update genre scores
                option.genres.forEach(genre => {
                    genreScores[genre] = (genreScores[genre] || 0) + 1;
                });
                
                // Load next question
                currentQuizQuestion++;
                loadQuizQuestion(currentQuizQuestion);
            });
            
            optionDiv.appendChild(card);
            quizOptions.appendChild(optionDiv);
        });
    }

    async function finishQuiz() {
        try {
            const response = await fetch('http://localhost:5000/api/quiz/result', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ answers: userAnswers })
            });

            if (!response.ok) {
                throw new Error('Failed to calculate quiz result');
            }

            const data = await response.json();
            selectedGenres = data.genres;
            showRecommendations(selectedGenres);
        } catch (error) {
            console.error('Error:', error);
            // Fall back to local calculation if API fails
            const maxScore = Math.max(...Object.values(genreScores));
            selectedGenres = Object.keys(genreScores).filter(genre => genreScores[genre] === maxScore);
            showRecommendations(selectedGenres);
        }
    }

    function resetQuiz() {
        currentQuizQuestion = 0;
        genreScores = {};
        userAnswers = [];
        quizProgress.style.width = '0%';
    }

    // Recommendations flow
    async function showRecommendations(genres) {
        showSection('results');
        const recommendedShows = document.getElementById('recommended-shows');
        recommendedShows.innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Finding the perfect shows for you...</p>
            </div>
        `;

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
            displayRecommendations(data);
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

    function displayRecommendations(data) {
        const recommendedShows = document.getElementById('recommended-shows');
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
        genreInfo.innerHTML = `<p class="text-muted">Based on your preferred genres: ${Array.isArray(data.genres) ? data.genres.join(', ') : data.genres}</p>`;
        recommendedShows.prepend(genreInfo);
    }

    // Chatbot flow
    function showChatbot() {
        showSection('chat');
    }

    function resetChat() {
        chatMessages.innerHTML = `
            <div class="message bot-message">
                Hello! I'm Suggestify, your TV show recommendation assistant. How can I help you today?
            </div>
        `;
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
                    showSection('main');
                    resetChat();
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

    // Initialize the application
    initializeApp();
});