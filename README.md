# 🤖 Intelligent Chatbot with Document Context & Persistent Memory

An AI-powered conversational assistant built with Flask and LangChain that maintains conversation history and provides context-aware responses by integrating user documents into the chat experience.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![LangChain](https://img.shields.io/badge/LangChain-Latest-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)


## ✨ Features

- **🧠 Persistent Memory**: Maintains conversation context across multiple sessions using session-based chat history
- **📄 Document Intelligence**: Integrates user-uploaded documents for context-aware responses
- **🔄 Session Management**: User-specific conversation tracking with unique session IDs
- **🌐 RESTful API**: Flask-based API with structured JSON responses
- **💾 Database Integration**: Stores and retrieves user documents efficiently
- **🛡️ Error Handling**: Comprehensive validation and error management
- **📊 Scalable Architecture**: Designed for production deployment with Redis/Database support

## 🎬 Demo
```bash
# Example conversation
User: "Hello, who are you?"
Bot: "I'm an AI assistant. How can I help you today?"

User: "Summarize my sales report"
Bot: [Accesses user's uploaded sales document]
     "Based on your Q3 sales report, revenue increased by 23%..."
```

## 🏗️ Architecture

<img width="811" height="661" alt="Agent_Archetecture drawio" src="https://github.com/user-attachments/assets/03267656-ae26-4c20-8cde-5e94c639160c" />

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Step 1: Clone the Repository
```bash
git clone https://github.com/talaat259/Intelligent-Chatbot-with-Document-Context-Persistent-Memory.git
cd Intelligent-Chatbot-with-Document-Context-Persistent-Memory
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables

Create a `.env` file in the root directory:
```env
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
# or
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Database Configuration
DATABASE_URL=sqlite:///chatbot.db

# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_secret_key_here

# Optional: Redis for production
REDIS_URL=redis://localhost:6379
```

### Step 5: Initialize Database
```bash
python init_db.py
```

## 💻 Usage

### Running the Application

#### Development Mode
```bash
python app.py
# or
flask run
```

The application will be available at `http://localhost:5000`

#### Production Mode
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using the Chatbot

#### Command Line Interface
```bash
python user_chatbot.py
```

#### Via API
```bash
# Regular chat
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Hello, how are you?",
    "user_id": "user123"
  }'

# Chat with document context
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Summarize my documents",
    "user_id": "user123",
    "include_docs": true
  }'
```

## 📡 API Documentation

### Endpoints

#### 1. Chat Endpoint

**POST** `/chat`

Send a message to the chatbot.

**Request Body:**
```json
{
  "query": "Your message here",
  "user_id": "unique_user_id",
  "include_docs": false
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Chatbot response here",
  "type": "chat_response",
  "session_id": "user_unique_user_id",
  "context": null
}
```

#### 2. User-Specific Chat

**POST** `/chat/<user_id>`

User-specific chat endpoint.

**Request Body:**
```json
{
  "query": "Your message",
  "include_docs": true
}
```

#### 3. Document Upload

**POST** `/upload`

Upload documents for the chatbot to reference.

**Request Body:** `multipart/form-data`
- `file`: Document file
- `user_id`: User identifier

### Response Codes

| Code | Description |
|------|-------------|
| 200  | Success |
| 400  | Bad Request (invalid input) |
| 500  | Internal Server Error |

## 📁 Project Structure
```
Intelligent-Chatbot/
│
├── app.py                      # Flask application entry point
├── user_chatbot.py             # Chatbot logic and LangChain integration
├── bot_chat.py                 # Chat handler functions
├── database.py                 # Database operations
├── init_db.py                  # Database initialization
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (not in repo)
├── .gitignore                  # Git ignore file
│
├── static/                     # Static files (CSS, JS, images)
│   ├── css/
│   └── js/
│
├── templates/                  # HTML templates
│   └── index.html
│
├── uploads/                    # User document uploads
│
└── README.md                   # This file
```

## ⚙️ Configuration

### Memory Store Options

#### In-Memory (Development)
```python
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]
```

#### Redis (Production)
```python
from langchain_community.chat_message_histories import RedisChatMessageHistory

def get_session_history(session_id: str):
    return RedisChatMessageHistory(
        session_id, 
        url="redis://localhost:6379"
    )
```

#### SQL Database
```python
from langchain_community.chat_message_histories import SQLChatMessageHistory

def get_session_history(session_id: str):
    return SQLChatMessageHistory(
        session_id=session_id,
        connection_string="sqlite:///chat_history.db"
    )
```

## 🔧 Requirements
```txt
flask==3.0.0
langchain==0.1.0
langchain-community==0.0.10
langchain-openai==0.0.5
python-dotenv==1.0.0
sqlalchemy==2.0.23
redis==5.0.1
requests==2.31.0
gunicorn==21.2.0
```




## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Coding Standards

- Follow PEP 8 style guide
- Write descriptive commit messages
- Add comments for complex logic
- Update documentation for new features
- Write tests for new functionality

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```
MIT License

Copyright (c) 2024 Talaat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 👤 Author

**Talaat**

- GitHub: [@talaat259](https://github.com/talaat259)
- LinkedIn: [Talaat Sallam](www.linkedin.com/in/talaat-sallam-6461451b8)
- Email: talaat.sallam@uahoo.com

## 🙏 Acknowledgments

- [LangChain](https://langchain.com/) for the conversational AI framework
- [Flask](https://flask.palletsprojects.com/) for the web framework



## 📊 Project Status

![GitHub last commit](https://img.shields.io/github/last-commit/talaat259/Intelligent-Chatbot-with-Document-Context-Persistent-Memory)
![GitHub issues](https://img.shields.io/github/issues/talaat259/Intelligent-Chatbot-with-Document-Context-Persistent-Memory)
![GitHub stars](https://img.shields.io/github/stars/talaat259/Intelligent-Chatbot-with-Document-Context-Persistent-Memory)
![GitHub forks](https://img.shields.io/github/forks/talaat259/Intelligent-Chatbot-with-Document-Context-Persistent-Memory)

---

<div align="center">

⭐ **If you find this project helpful, please give it a star!** ⭐

Made by [Talaat](https://github.com/talaat259)

</div>
