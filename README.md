# Autocode AI

Full-stack AI coding assistant with:

- **Landing / About / Contact / Pricing** pages (same dark cyan theme)
- **Manual signup & login** + **Google OAuth**
- **User dashboard** with usage charts (AI calls, runs, scans)
- **Code editor** (CodeMirror) with Explain / Fix / Optimize / Complete
- **Grok AI** chat (context-aware)
- **Scan Code** — OpenCV preprocess + Tesseract OCR
- **Online Python runner** with live stdout/stderr panel
- **Razorpay** subscription checkout (Pro / Team)
- Squeeze hover effects on buttons and cards

```
┌─────────────────────────────────────────────────────────────┐
│  Navbar · Home · About · Pricing · Contact · Login/Dashboard│
├─────────────────────────────┬───────────────────────────────┤
│  Code editor (CodeMirror)   │  AI Chat  |  Scan code        │
│  Explain Fix Optimize       │  -------- |  ----------       │
│  Complete  ▶ Run            │  chat log |  drop image       │
│  ─────────────────────      │           |  → OCR text       │
│  Output panel               │           |                   │
└─────────────────────────────┴───────────────────────────────┘
```

## Setup

1. **Python deps**
   ```bash
   cd autocode-ai
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Tesseract OCR** (for Scan Code)
   - macOS: `brew install tesseract`
   - Ubuntu: `sudo apt-get install tesseract-ocr`
   - Windows: https://github.com/UB-Mannheim/tesseract/wiki

3. **Environment**
   ```bash
   cp .env.example .env
   # Edit .env:
   #   GEMINI_API_KEY=...          (required for AI)
   #   SECRET_KEY=...              (any long random string)
   #   GOOGLE_CLIENT_ID / SECRET   (optional OAuth)
   #   RAZORPAY_KEY_ID / SECRET    (optional payments)
   ```

4. **Run**
   ```bash
   python app.py
   ```
   Open http://127.0.0.1:5000

## Google OAuth setup (optional)

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create OAuth 2.0 Client ID (Web application)
3. Authorized redirect URI: `http://127.0.0.1:5000/auth/google/callback`
4. Put Client ID and Secret in `.env`

## Razorpay (optional)

1. Create account at https://razorpay.com
2. Copy Key ID and Key Secret into `.env`
3. Pricing page → Subscribe opens Razorpay Checkout

## Notes

- Without `GEMINI_API_KEY`, AI endpoints return a friendly placeholder.
- Uploaded scan images are deleted immediately after OCR.
- Online runner supports **Python only** (safe subset; dangerous builtins blocked).
- SQLite database `autocode.db` is created automatically on first run.

## Project structure

```
autocode-ai/
├── app.py
├── requirements.txt
├── .env.example
├── templates/
│   ├── base.html
│   ├── landing.html
│   ├── about.html
│   ├── contact.html
│   ├── pricing.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   └── editor.html
├── static/
│   ├── css/style.css
│   └── js/main.js
└── uploads/
```
