# Mail Generator App

This app streamlines your daily email workflow by helping you quickly and effortlessly reply to incoming threads in your unique writing style. 
It intelligently analyzes your writing habits, understands the context of each email conversation, prompts you for any additional information if needed, and generates personalized, context-aware email responses on your behalf.

## 🧠 AI Model Architecture

The application uses a sophisticated AI pipeline with three main components:

### 1. Writing Style Analysis (20+ Features)

The system analyzes your email writing style using **20+ linguistic features**:

#### **Cohesion Features**
- **Connective Density**: Frequency of linking words (however, because, therefore)
- **Pronoun Density**: Usage of personal pronouns
- **Lexical Overlap**: Vocabulary diversity and repetition patterns

#### **Syntax Features**
- **Average Sentence Length**: Number of words per sentence
- **Clause Density**: Complex sentence structures (subordinate, adverbial, relative clauses)
- **Passive Voice Ratio**: Frequency of passive voice constructions

#### **Lexical Features**
- **Average Word Length**: Character count per word
- **Syllables per Word**: Word complexity measurement
- **Type-Token Ratio**: Vocabulary richness and diversity

#### **Readability Features**
- **Flesch-Kincaid Grade**: Reading difficulty level
- **SMOG Index**: Simplified Measure of Gobbledygook
- **Gunning Fog Index**: Text complexity assessment

#### **Part-of-Speech Features**
- **Noun Ratio**: Percentage of nouns in text
- **Verb Ratio**: Percentage of verbs in text
- **Adjective Ratio**: Percentage of adjectives in text
- **Adverb Ratio**: Percentage of adverbs in text

#### **Style Markers**
- **Informal Word Density**: Usage of casual language (gonna, wanna, dude)
- **Contraction Density**: Frequency of contractions (don't, can't)
- **Exclamation Density**: Use of exclamation marks
- **Question Density**: Use of question marks
- **Emoji/Symbol Density**: Special character usage

### 2. Email Thread Summarization

The AI processes email threads through a **three-step summarization process**:

1. **Thread Collection**: Gathers all emails in a conversation thread
2. **Content Extraction**: Extracts key information from each email:
   - Sender information and context
   - Subject lines and main topics
   - Full message content (plain text and HTML)
3. **AI Summarization**: Uses Groq LLM to create structured summaries:
   - **Main discussion points**
   - **Relevant information to keep in mind**
   - **Open questions or pending actions**
   - **Conversation tone analysis** (formal/informal)

### 3. Contextual Email Generation

The system generates replies using a **multi-stage approach**:

#### **Stage 1: Information Gathering**
- AI analyzes the email thread summary
- Identifies missing information needed for a complete reply
- Generates clarifying questions to gather context

#### **Stage 2: Interactive Q&A**
- Presents questions to the user one by one
- Accumulates user responses in a structured format
- Continues until all necessary information is collected

#### **Stage 3: Style-Aware Generation**
- Combines thread summary, user responses, and writing style analysis
- Generates email reply that matches the user's writing style
- Ensures consistency with conversation tone and context

### AI Model Integration

#### **Natural Language Processing**
- **SpaCy**: Advanced NLP for text analysis and feature extraction
- **TextStat**: Readability metrics and text statistics
- **Custom Style Analyzer**: Proprietary algorithm for writing style detection

#### **Large Language Model**
- **Groq API**: High-performance LLM for summarization and generation
- **Model**: `meta-llama/llama-4-scout-17b-16e-instruct` - 17B parameter instruction-tuned model
- **Context-Aware Prompts**: Structured prompts that maintain conversation flow
- **Style Consistency**: Ensures generated emails match user's writing patterns

#### **Quality Assurance**
- **Multi-turn Conversations**: Iterative refinement through Q&A
- **Context Preservation**: Maintains conversation history and tone
- **Style Matching**: Ensures generated content matches user's writing style

### Example Workflow

```
1. User selects email thread
   ↓
2. System analyzes user's writing style (20+ features)
   ↓
3. AI summarizes the email thread
   ↓
4. System identifies missing information
   ↓
5. AI asks clarifying questions
   ↓
6. User provides answers
   ↓
7. AI generates contextual, style-matched reply
```

### Technical Implementation

- **Feature Extraction**: Real-time analysis of 20+ linguistic features
- **Style Similarity**: Euclidean distance calculation with weighted features
- **Context Management**: Session-based storage of conversation state
- **Error Handling**: Graceful fallbacks for API failures and edge cases
- **LLM Integration**: Groq API with Llama 4 Scout 17B model for high-performance inference
- **Model Capabilities**: 17B parameter instruction-tuned model optimized for email processing

## 🛠️ Tech Stack

### **Backend Framework**
- **Flask 3.1.0**: Lightweight web framework for Python

### **Database & ORM**
- **Flask-SQLAlchemy 3.1.1**: Flask integration for SQLAlchemy

### **Authentication & Security**
- **bcrypt 4.1.2**: Password hashing and verification
- **cryptography 42.0.5**: Cryptographic primitives for token encryption
- **OAuth2**: Google authentication for Gmail API access

### **AI & Machine Learning**
- **Groq API**: High-performance LLM inference
- **Llama 4 Scout 17B**: 17B parameter instruction-tuned model
- **SpaCy 3.8.2**: Advanced natural language processing
- **TextStat 0.7.3**: Text statistics and readability metrics
- **NumPy 2.2.4**: Numerical computing for feature analysis

### **External APIs**
- **Gmail API**: Email access and thread management
- **Google Auth**: OAuth2 authentication and token management
- **Google API Client**: Python client for Google APIs

### **Development & Deployment**
- **Python 3.8+**: Core programming language

### **Frontend & UI**
- **HTML5**: Semantic markup
- **CSS3**: Styling and responsive design
- **JavaScript**: Client-side interactivity

### **Infrastructure**
- **Git**: Version control


## 🎯 Usage Guide

### **Step 1: Initial Setup**
1. **Register Account**
   - Navigate to `/login`
   - Click "Register" to create a new account
   - Provide your name, email, and password
   - The system will hash your password securely

2. **Gmail Authorization**
   - After registration, you'll be redirected to Google OAuth2
   - Grant permissions for Gmail API access (read/write)
   - The application stores encrypted credentials securely

### **Step 2: Writing Style Analysis**
1. **Access Style Analysis**
   - You will then be redirected to `/style` in your browser
   - The system will automatically fetch your sent emails

2. **Style Processing**
   - AI analyzes your email patterns using 20+ linguistic features
   - Extracts writing style characteristics:
     - Sentence length and complexity
     - Vocabulary diversity
     - Formality level
     - Punctuation patterns
   - Stores your writing style profile for future email generation

### **Step 3: Email Search & Selection**
1. **Search Interface**
   - You will then be redirected to `/search_window`
   - Use the search interface to find specific emails
   - Search by subject
     
2. **Thread Selection**
   - Browse through search results
   - Click on email threads to view full conversations
   - Select the thread you want to reply to

### **Step 4: AI-Powered Email Generation**
1. **Thread Analysis**
   - System fetches the complete email thread
   - AI summarizes the conversation using Llama 4 Scout 17B
   - Extracts key points, action items, and context

2. **Information Gathering**
   - AI identifies missing information needed for a complete reply
   - Generates clarifying questions to gather context
   - Presents questions one by one for user input

3. **Interactive Q&A**
   - Answer each question as it appears
   - Provide additional context or preferences
   - System accumulates responses for comprehensive understanding

4. **Style-Aware Generation**
   - AI combines thread summary, your responses, and writing style analysis
   - Generates email reply that matches your unique writing style
   - Ensures consistency with conversation tone and context

### **Step 5: Review & Send**
1. **Generated Reply**
   - Review the AI-generated email reply
   - Verify it matches your intended message and style
   - Make any necessary edits or adjustments

2. **Email Sending**
   - Copy the generated reply
   - Paste into your email client
   - Send the email through your preferred email service

### **Advanced Features**

#### **Writing Style Customization**
- Your writing style is automatically learned from your sent emails
- The system adapts to your communication patterns
- No manual configuration required

#### **Context Preservation**
- System maintains conversation history
- Understands email thread context
- Preserves tone and formality levels

### **Best Practices**

1. **For Best Results**
   - Provide detailed answers to AI questions
   - Be specific about your preferences and context
   - Review generated emails before sending

2. **Security**
   - Never share your API keys
   - Use strong passwords
   - Log out when using shared computers

3. **Performance**
   - The system works best with recent email threads
   - Larger email threads may take longer to process
   - Ensure stable internet connection for API calls

### Example Workflow

```
1. User selects email thread
   ↓
2. System analyzes user's writing style (20+ features)
   ↓
3. AI summarizes the email thread
   ↓
4. System identifies missing information
   ↓
5. AI asks clarifying questions
   ↓
6. User provides answers
   ↓
7. AI generates contextual, style-matched reply
```

### Technical Implementation

- **Feature Extraction**: Real-time analysis of 20+ linguistic features
- **Style Similarity**: Euclidean distance calculation with weighted features
- **Context Management**: Session-based storage of conversation state
- **Error Handling**: Graceful fallbacks for API failures and edge cases
- **LLM Integration**: Groq API with Llama 4 Scout 17B model for high-performance inference
- **Model Capabilities**: 17B parameter instruction-tuned model optimized for email processing


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
- Automatic summarization of email threads using Llama 4 Scout 17B model
- Extracts key points, action items, and context
- Maintains conversation tone and structure

### Interactive Q&A System
- AI asks clarifying questions before generating replies
- Gathers context to create more accurate responses
- Maintains conversation flow and style consistency

### AI Model Details
- **Model**: `meta-llama/llama-4-scout-17b-16e-instruct` (17B parameters)
- **Provider**: Groq API for high-performance inference
- **Capabilities**: Email summarization, contextual Q&A, and style-aware generation

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
