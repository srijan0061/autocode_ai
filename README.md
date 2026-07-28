# 🚀 AutoCode AI

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python">
  <img src="https://img.shields.io/badge/Flask-Web%20Framework-black?style=for-the-badge&logo=flask">
  <img src="https://img.shields.io/badge/MySQL-Database-orange?style=for-the-badge&logo=mysql">
  <img src="https://img.shields.io/badge/Google-Gemini%20AI-blue?style=for-the-badge&logo=google">
  <img src="https://img.shields.io/badge-License-MIT-green?style=for-the-badge">
</p>

<p align="center">
An AI-powered code generation platform that transforms natural language prompts into executable source code using Google Gemini AI.
</p>

---

# 📖 Overview

**AutoCode AI** is a Flask-based web application that enables users to generate source code by simply describing their requirements in natural language. The platform leverages **Google Gemini AI** to produce clean, structured, and reusable code snippets across multiple programming languages.

The application provides a simple and intuitive interface for developers, students, and programming enthusiasts to accelerate development, learn programming concepts, and automate repetitive coding tasks.

---

# ✨ Features

### 🤖 AI Code Generation

- Generate code from plain English prompts
- Multi-language code generation
- AI-powered coding assistance
- Fast and accurate responses
- Beginner-friendly interface

---

### 🔐 User Authentication

- User Registration
- Secure Login
- Session Management
- Protected Dashboard

---

### 💬 Prompt-Based Development

Users can describe requirements like:

- Build a login page
- Create a REST API
- Write Python scripts
- Generate HTML/CSS layouts
- SQL Queries
- Java Programs
- JavaScript Functions

and receive AI-generated source code instantly.

---

### 📁 Dashboard

Users can

- Generate code
- View previous prompts
- Manage generated responses
- Continue development seamlessly

---

### 🗄 Database

MySQL stores

- User Accounts
- Prompt History
- Generated Code
- Session Information

---

# 🏗 Architecture

```

User

↓

Flask Application

↓

Google Gemini AI

↓

Generated Source Code

↓

MySQL Database

```

---

# 🛠 Tech Stack

| Category | Technology |
|----------|------------|
| Backend | Flask |
| Language | Python |
| Frontend | HTML, CSS, JavaScript |
| Templates | Jinja2 |
| Database | MySQL |
| AI Model | Google Gemini AI |
| Authentication | Flask Login |
| Environment | Python-dotenv |

---

# 📂 Project Structure

```
AutoCode-AI/
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/
│
├── app.py
├── config.py
├── requirements.txt
├── .env
└── README.md
```

---

# 🚀 Installation

## Clone Repository

```bash
git clone https://github.com/srijan0061/autocode_ai.git

cd autocode_ai
```

---

## Create Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment Variables

Create a `.env` file.

```env
SECRET_KEY=your_secret_key

MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_DB=autocode_ai

GEMINI_API_KEY=your_google_gemini_api_key
```

---

## Run the Application

```bash
python app.py
```

Open

```
http://127.0.0.1:5000
```

---

# 💡 Key Functionalities

- AI Code Generation
- Prompt-Based Development
- Google Gemini Integration
- Secure Authentication
- User Dashboard
- Prompt History
- MySQL Database
- Responsive UI

---

# 🤖 AI Workflow

```
User Prompt

↓

Google Gemini API

↓

Prompt Processing

↓

Source Code Generation

↓

Display Generated Code
```

---

# 📈 Future Enhancements

- Code Explanation Feature
- Code Optimization Suggestions
- AI Debugging Assistant
- Code Download (.py, .java, .cpp)
- Dark Mode
- Voice Prompt Support
- Project Generation
- GitHub Integration
- Multiple AI Models
- Code Sharing

---

# 🤝 Contributing

Contributions are welcome!

1. Fork the repository

2. Create a new branch

```bash
git checkout -b feature-name
```

3. Commit your changes

```bash
git commit -m "Add new feature"
```

4. Push the branch

```bash
git push origin feature-name
```

5. Open a Pull Request

---

# 📜 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

**Srijan Pandit**

🎓 MCA Student  
💻 Full Stack Developer  
🤖 AI & Web Development Enthusiast

### GitHub

https://github.com/srijan0061

---

# ⭐ Support

If you found this project useful,

⭐ Star the repository

🍴 Fork the project

🐛 Report Issues

💡 Suggest Features

---

<p align="center">
Made with ❤️ using Flask, Python, MySQL and Google Gemini AI.
</p>
