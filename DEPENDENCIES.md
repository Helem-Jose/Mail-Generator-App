# Dependencies Documentation

This document explains all the dependencies used in the Flask Email Assistant project and their purposes.

## Core Flask Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 3.1.0 | Main web framework |
| Flask-SQLAlchemy | 3.1.1 | Database ORM for Flask |
| Werkzeug | 3.1.3 | WSGI utility library (Flask dependency) |
| Jinja2 | 3.1.6 | Template engine (Flask dependency) |
| itsdangerous | 2.2.0 | Data signing (Flask dependency) |
| click | 8.1.8 | Command line interface (Flask dependency) |
| MarkupSafe | 3.0.2 | Safe string handling (Jinja2 dependency) |

## Database

| Package | Version | Purpose |
|---------|---------|---------|
| SQLAlchemy | 2.0.41 | Database ORM |
| greenlet | 3.2.3 | Lightweight coroutines (SQLAlchemy dependency) |

## Authentication and Security

| Package | Version | Purpose |
|---------|---------|---------|
| bcrypt | 4.1.2 | Password hashing |
| cryptography | 42.0.5 | Cryptographic primitives |
| cffi | 1.17.0 | C Foreign Function Interface (cryptography dependency) |
| pycparser | 2.22 | C parser (cffi dependency) |

## Google API Integration

| Package | Version | Purpose |
|---------|---------|---------|
| google-auth | 2.28.1 | Google authentication library |
| google-auth-oauthlib | 1.2.0 | OAuth2 library for Google APIs |
| google-auth-httplib2 | 0.2.0 | HTTP library for Google Auth |
| google-api-python-client | 2.118.0 | Google API client library |
| cachetools | 6.1.0 | Caching utilities (Google API dependency) |
| rsa | 4.9 | RSA encryption (Google Auth dependency) |
| pyasn1 | 0.6.0 | ASN.1 library (RSA dependency) |
| pyasn1-modules | 0.4.0 | ASN.1 modules (RSA dependency) |

## AI and NLP

| Package | Version | Purpose |
|---------|---------|---------|
| groq | 0.4.2 | Groq API client for LLM access |
| spacy | 3.8.2 | Natural language processing |
| textstat | 0.7.3 | Text statistics and readability |
| numpy | 2.2.4 | Numerical computing |

## Environment and Configuration

| Package | Version | Purpose |
|---------|---------|---------|
| python-dotenv | 1.0.1 | Environment variable management |

## HTTP Requests

| Package | Version | Purpose |
|---------|---------|---------|
| requests | 2.32.3 | HTTP library |
| urllib3 | 2.2.2 | HTTP client (requests dependency) |
| certifi | 2024.7.4 | SSL certificates (requests dependency) |
| charset-normalizer | 3.3.2 | Character encoding detection (requests dependency) |
| idna | 3.8 | Internationalized domain names (requests dependency) |

## Installation Notes

### Spacy Language Model
After installing spacy, you need to download the English language model:
```bash
python -m spacy download en_core_web_sm
```

### Environment Variables
Create a `.env` file with:
```env
GROQ_API_KEY=your_groq_api_key_here
encryption_key=your_encryption_key_here
LOG_LEVEL=INFO
```

### Google OAuth2 Setup
1. Create a Google Cloud Project
2. Enable Gmail API
3. Create OAuth2 credentials
4. Download `client_secret.json` to project root

## Dependency Categories

### Required for Core Functionality
- Flask ecosystem (Flask, SQLAlchemy, etc.)
- Database (SQLAlchemy, greenlet)
- Authentication (bcrypt, cryptography)

### Required for Gmail Integration
- Google API packages
- OAuth2 libraries

### Required for AI Features
- Groq API client
- NLP libraries (spacy, textstat)
- Numerical computing (numpy)

## Version Compatibility

All versions are tested and compatible with:
- Python 3.8+
- Flask 3.x
- SQLAlchemy 2.x

## Security Considerations

- `cryptography` and `bcrypt` for secure credential handling
- `google-auth` for secure OAuth2 implementation
- All packages are from trusted sources (PyPI)

## Performance Considerations

- `spacy` with language model adds ~500MB
- Consider using virtual environments for isolation 