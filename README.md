# 🚀 AutoCode AI

<p align="center">
  <h3 align="center">AI-Powered Code Generation Platform</h3>
  <p align="center">
    Generate clean, efficient, and production-ready code from natural language prompts using Google Gemini AI.
  </p>
</p>

---

## 📖 Overview

**AutoCode AI** is an AI-powered web application built with **Python** and **Flask** that transforms natural language prompts into executable source code. It leverages **Google Gemini AI** to help developers, students, and programming enthusiasts generate code quickly, reduce development time, and improve productivity.

The platform features a clean and responsive interface where users can describe the functionality they need in plain English. AutoCode AI processes these prompts and generates structured code across multiple programming languages, making software development more accessible and efficient.

---

## ✨ Features

### 🤖 AI Code Generation
- Generate code from natural language prompts
- AI-powered coding assistance
- Multi-language code generation
- Fast and accurate responses
- Beginner-friendly interface

### 🔐 User Authentication
- Secure user registration
- Login and session management
- Protected user dashboard

### 💻 Interactive Dashboard
- Generate code instantly
- Manage prompt history
- View previously generated code
- Continue working on saved prompts

### 🗄 Database Management
- Secure MySQL database
- User account management
- Prompt and response history
- Session tracking

### 🎨 Responsive User Interface
- Clean modern design
- Mobile-friendly layout
- Interactive navigation
- Optimized user experience

---

## 🛠 Tech Stack

| Category | Technology |
|-----------|------------|
| Programming Language | Python |
| Backend Framework | Flask |
| Frontend | HTML, CSS, JavaScript |
| Template Engine | Jinja2 |
| Database | MySQL |
| Artificial Intelligence | Google Gemini AI |
| Authentication | Flask Login |
| Configuration | Python Dotenv |

---

## 📂 Project Structure

```
autocode_ai/
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

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/srijan0061/autocode_ai.git

cd autocode_ai
```

### 2. Create a Virtual Environment

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root.

```env
SECRET_KEY=your_secret_key

MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=autocode_ai

GEMINI_API_KEY=your_google_gemini_api_key
```

### 5. Run the Application

```bash
python app.py
```

Visit:

```
http://127.0.0.1:5000
```

---

## 💡 Core Functionalities

- AI-powered source code generation
- Prompt-based programming assistance
- Google Gemini AI integration
- User authentication
- Prompt history management
- Responsive web interface
- MySQL database integration
- Secure session handling

---

## 🤖 AI Workflow

```
User Prompt
      │
      ▼
AutoCode AI
      │
      ▼
Google Gemini AI
      │
      ▼
Generated Source Code
      │
      ▼
Display Result to User
```

---

## 📈 Future Enhancements

- AI code explanation
- Code optimization suggestions
- AI debugging assistant
- Download generated code
- Dark mode
- Voice prompt support
- GitHub integration
- Multiple AI model support
- Real-time collaboration
- Project template generation

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch

```bash
git checkout -b feature-name
```

3. Commit your changes

```bash
git commit -m "Add new feature"
```

4. Push to GitHub

```bash
git push origin feature-name
```

5. Open a Pull Request

---

## 📜 License

This project is licensed under the **MIT License**.

---

## 👨‍💻 Author

**Srijan Pandit**

🎓 MCA Student  
💻 Full Stack Developer  
🤖 AI & Web Development Enthusiast

**GitHub:** https://github.com/srijan0061

---

## ⭐ Support

If you found this project helpful:

- ⭐ Star the repository
- 🍴 Fork the project
- 🐞 Report issues
- 💡 Suggest improvements

---

<p align="center">
Made with ❤️ using Flask, Python, MySQL, and Google Gemini AI.
</p>
