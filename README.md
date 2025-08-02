# Mail Generator App

This app streamlines your daily email workflow by helping you quickly and effortlessly reply to incoming threads in your unique writing style. 
It intelligently analyzes your writing habits, understands the context of each email conversation, prompts you for any additional information if needed, and generates personalized, context-aware email responses on your behalf.

# Style analysis :



## 🚀 Features

- **User Authentication**: Secure login system with bcrypt password hashing
- **Gmail Integration**: OAuth2 authentication for Gmail API access
- **Writing Style Analysis**: AI-powered analysis of user's email writing style
- **Email Search**: Search through Gmail messages with subject-based queries
- **Thread Summarization**: Automatic summarization of email threads
- **AI Email Assistant**: Interactive Q&A system for generating contextual email replies
- **Comprehensive Logging**: Structured logging with configurable levels
- **Database Integration**: SQLAlchemy with SQLite for user data persistence

## 📋 Prerequisites

- Python 3.8+
- Gmail account with API access
- Google Cloud Project with Gmail API enabled

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Flask-test
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   encryption_key=your_encryption_key_here
   LOG_LEVEL=INFO
   ```

5. **Configure Google OAuth2**
   - Create a project in Google Cloud Console
   - Enable Gmail API
   - Create OAuth2 credentials
   - Download `client_secret.json` and place it in the project root


## 🏃‍♂️ Running the Application

### Development Mode
```bash
python app.py
```

### Production Mode
```bash
export FLASK_ENV=production
export LOG_LEVEL=WARNING
python app.py
```

The application will be available at `http://localhost:5000`


## 🔧 Project Structure

```
Flask-test/
├── app.py                 # Main Flask application
├── agent.py              # AI agent for email processing
├── authenticate.py       # OAuth2 authentication
├── get_messages.py       # Gmail API message handling
├── models.py             # Database models
├── db.py                 # Database configuration
├── logging_config.py     # Logging configuration
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
├── client_secret.json    # Google OAuth2 credentials
├── app_secret_key.json  # Flask secret key
├── static/               # CSS and static assets
├── templates/            # HTML templates
└── instance/             # Database files
```

## 🎯 Usage Guide



## 🔐 Security Features

- **Password Hashing**: bcrypt for secure password storage
- **OAuth2 Authentication**: Secure Gmail API access
- **Credential Encryption**: Encrypted storage of OAuth tokens
- **Session Management**: Flask session-based authentication
- **CSRF Protection**: State validation in OAuth2 flow

## 🤖 AI Features

### Writing Style Analysis
- Analyzes email patterns, vocabulary, and tone
- Extracts features like sentence length, formality, and complexity
- Provides detailed style descriptions

### Email Summarization
- Automatic summarization of email threads
- Extracts key points, action items, and context
- Maintains conversation tone and structure

### Interactive Q&A System
- AI asks clarifying questions before generating replies
- Gathers context to create more accurate responses
- Maintains conversation flow and style consistency

## 📝 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home page |
| `/login` | GET | Login page |
| `/validateUser` | POST | User authentication |
| `/addUser` | POST | User registration |
| `/home` | GET | Main dashboard |
| `/authorize` | GET | OAuth2 authorization |
| `/oauth2callback` | GET | OAuth2 callback |
| `/search_window` | GET | Email search interface |
| `/search` | GET | Email search API |
| `/get_style` | GET | Writing style analysis |
| `/get_thread/<threadID>` | GET | Fetch email thread |
| `/generate_mail/` | GET | Email generation interface |
| `/get_model_output/<reply>` | GET | AI Q&A processing |
| `/logout` | GET | User logout |

## 🐛 Troubleshooting

### Common Issues

1. **OAuth2 Errors**
   - Ensure `client_secret.json` is properly configured
   - Check that Gmail API is enabled in Google Cloud Console
   - Verify redirect URI matches OAuth2 configuration

2. **AI Model Errors**
   - Verify `GROQ_API_KEY` is set in `.env`
   - Check internet connectivity for API calls
   - Review logs for specific error messages

### Debug Mode
Enable debug logging for detailed troubleshooting:
```bash
export LOG_LEVEL=DEBUG
python app.py
```

## 📈 Performance Considerations

- **Log Rotation**: Logs are automatically rotated to prevent disk space issues
- **Database Optimization**: SQLAlchemy with SQLite for lightweight deployment
- **Caching**: Consider implementing Redis for session storage in production
- **Rate Limiting**: Implement rate limiting for API endpoints in production

## 🔄 Development



### Testing
```bash
# Run with debug logging
export LOG_LEVEL=DEBUG && python app.py

# Run with minimal logging
export LOG_LEVEL=ERROR && python app.py
```

**Note**: This application requires proper Google OAuth2 setup and Groq API access. Ensure all credentials and API keys are securely managed and not committed to version control.
