"""
Autocode AI — full website
==========================
- Landing, About, Contact, Pricing
- Manual + Google OAuth login / signup
- User dashboard with usage graphs
- Code editor + AI assist + chat (now powered by Groq)
- Scan Code (OpenCV + Tesseract OCR)
- Online code runner (Python)
- Razorpay subscription checkout
"""

import os
import io
import re
import base64
import uuid
import json
import time
import traceback
import subprocess
import tempfile
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Flask, render_template, request, jsonify, redirect, url_for,
    flash, session, g
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user,
    login_required, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

import cv2
import numpy as np

try:
    import pytesseract
    # Windows path – change if Tesseract is installed elsewhere
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
except ImportError:
    pytesseract = None

try:
    from groq import Groq
except ImportError:
    Groq = None

try:
    from authlib.integrations.flask_client import OAuth
except ImportError:
    OAuth = None

try:
    import razorpay
except ImportError:
    razorpay = None

# --------------------------------------------------------------------------
# App configuration
# --------------------------------------------------------------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///autocode.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------- AI (Groq) ----------
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

_groq_client = None
_ai_ready = False
if Groq and GROQ_API_KEY:
    _groq_client = Groq(api_key=GROQ_API_KEY)
    _ai_ready = True

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
RAZORPAY_KEY_ID = os.environ.get("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET")

_razorpay_client = None
if razorpay and RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET:
    _razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

oauth = None
if OAuth and GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    oauth = OAuth(app)
    oauth.register(
        name="google",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )


# --------------------------------------------------------------------------
# Models
# --------------------------------------------------------------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    google_id = db.Column(db.String(64), unique=True, nullable=True)
    plan = db.Column(db.String(32), default="free")  # free | pro | team
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # usage counters
    ai_calls = db.Column(db.Integer, default=0)
    code_runs = db.Column(db.Integer, default=0)
    scans = db.Column(db.Integer, default=0)
    snippets_saved = db.Column(db.Integer, default=0)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)


class UsageEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    kind = db.Column(db.String(32), nullable=False)  # ai | run | scan
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PaymentOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    razorpay_order_id = db.Column(db.String(64), unique=True)
    amount = db.Column(db.Integer)  # paise
    plan = db.Column(db.String(32))
    status = db.Column(db.String(32), default="created")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


with app.app_context():
    db.create_all()


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def record_usage(user, kind):
    if not user or not user.is_authenticated:
        return
    if kind == "ai":
        user.ai_calls = (user.ai_calls or 0) + 1
    elif kind == "run":
        user.code_runs = (user.code_runs or 0) + 1
    elif kind == "scan":
        user.scans = (user.scans or 0) + 1
    db.session.add(UsageEvent(user_id=user.id, kind=kind))
    db.session.commit()


MODE_PROMPTS = {
    "explain": "Explain what the following {language} code does, step by step, "
               "in clear plain language. Point out anything non-obvious.",
    "fix": "Find and fix any bugs in the following {language} code. "
          "Return the corrected code in a fenced code block first, then a short "
          "bullet list of what was wrong and how you fixed it.",
    "optimize": "Review the following {language} code for performance and "
                "readability. Return an improved version in a fenced code block "
                "first, then a short bullet list of the changes you made.",
    "generate": "Write {language} code that does the following:\n\n{instruction}\n\n"
                "Return only clean, well-commented code in a fenced code block, "
                "followed by a one or two sentence explanation.",
    "complete": "Continue / complete the following {language} code in a way that "
                "is consistent with its existing style. Return the completed code "
                "in a fenced code block.",
}


def call_ai(system_prompt, user_message, history=None):
    """Call Groq AI"""
    if not _ai_ready or not _groq_client:
        return (
            "⚠️ No Groq API key is configured. "
            "Set GROQ_API_KEY in your .env file and restart the app.\n\n"
            "(Placeholder so you can still explore the UI.)"
        )

    try:
        messages = [{"role": "system", "content": system_prompt}]

        # Add previous conversation history
        if history:
            for turn in history[-10:]:
                role = turn.get("role", "user")
                if role == "model":
                    role = "assistant"
                messages.append({
                    "role": role,
                    "content": turn.get("content", "")
                })

        messages.append({"role": "user", "content": user_message})

        response = _groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=2048,
        )
        return response.choices[0].message.content or ""
    except Exception as exc:
        return f"AI error: {exc}"


def preprocess_for_ocr(image_bgr):
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    if max(h, w) < 1600:
        scale = 1600 / max(h, w)
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    gray = cv2.fastNlMeansDenoising(gray, h=15)
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 15
    )
    coords = np.column_stack(np.where(thresh < 255))
    angle = 0.0
    if coords.size:
        rect_angle = cv2.minAreaRect(coords)[-1]
        angle = -(90 + rect_angle) if rect_angle < -45 else -rect_angle
        if abs(angle) > 0.5:
            (h2, w2) = thresh.shape
            M = cv2.getRotationMatrix2D((w2 // 2, h2 // 2), angle, 1.0)
            thresh = cv2.warpAffine(
                thresh, M, (w2, h2), flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE,
            )
    return thresh


def run_python_code(code, timeout=5):
    """Execute Python code in a subprocess with a hard timeout."""
    banned = [
        r"\bos\.system\b", r"\bsubprocess\b", r"\b__import__\b",
        r"\beval\s*\(", r"\bexec\s*\(", r"\bopen\s*\(",
        r"\bshutil\b", r"\bsocket\b", r"\bctypes\b",
    ]
    for pat in banned:
        if re.search(pat, code):
            return "", f"Blocked for safety: pattern matched ({pat}). Online runner is restricted.", 1

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(code)
        path = f.name
    try:
        proc = subprocess.run(
            ["python", path],          # changed to "python" for Windows
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        return proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired:
        return "", f"Execution timed out after {timeout}s.", 124
    except Exception as exc:
        return "", str(exc), 1
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


# --------------------------------------------------------------------------
# Public pages
# --------------------------------------------------------------------------
@app.route("/")
def landing():
    return render_template("landing.html", ai_configured=_ai_ready)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    sent = False
    if request.method == "POST":
        sent = True
        flash("Thanks! Your message has been received. We'll get back to you soon.", "success")
    return render_template("contact.html", sent=sent)


@app.route("/pricing")
def pricing():
    return render_template(
        "pricing.html",
        razorpay_key=RAZORPAY_KEY_ID or "",
        razorpay_ready=bool(_razorpay_client),
    )


# --------------------------------------------------------------------------
# Auth
# --------------------------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=bool(request.form.get("remember")))
            next_url = request.args.get("next") or url_for("dashboard")
            return redirect(next_url)
        flash("Invalid email or password.", "error")
    return render_template("login.html", google_enabled=bool(oauth))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        if not name or not email or len(password) < 6:
            flash("Name, email, and password (min 6 chars) are required.", "error")
        elif User.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "error")
        else:
            user = User(email=email, name=name)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash("Welcome to Autocode AI!", "success")
            return redirect(url_for("dashboard"))
    return render_template("register.html", google_enabled=bool(oauth))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("landing"))


@app.route("/auth/google")
def google_login():
    if not oauth:
        flash("Google OAuth is not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET.", "error")
        return redirect(url_for("login"))
    redirect_uri = url_for("google_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@app.route("/auth/google/callback")
def google_callback():
    if not oauth:
        return redirect(url_for("login"))
    try:
        token = oauth.google.authorize_access_token()
        info = token.get("userinfo") or {}
        email = (info.get("email") or "").lower()
        google_id = info.get("sub")
        name = info.get("name") or email.split("@")[0]
        if not email:
            flash("Could not read email from Google.", "error")
            return redirect(url_for("login"))
        user = User.query.filter(
            (User.google_id == google_id) | (User.email == email)
        ).first()
        if not user:
            user = User(email=email, name=name, google_id=google_id)
            db.session.add(user)
            db.session.commit()
        else:
            if not user.google_id:
                user.google_id = google_id
                db.session.commit()
        login_user(user, remember=True)
        return redirect(url_for("dashboard"))
    except Exception as exc:
        flash(f"Google sign-in failed: {exc}", "error")
        return redirect(url_for("login"))


# --------------------------------------------------------------------------
# Dashboard
# --------------------------------------------------------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    since = datetime.utcnow() - timedelta(days=14)
    events = (
        UsageEvent.query.filter(
            UsageEvent.user_id == current_user.id,
            UsageEvent.created_at >= since,
        )
        .order_by(UsageEvent.created_at)
        .all()
    )
    days = []
    ai_series, run_series, scan_series = [], [], []
    for i in range(14):
        d = (datetime.utcnow() - timedelta(days=13 - i)).date()
        days.append(d.strftime("%b %d"))
        ai_series.append(sum(1 for e in events if e.kind == "ai" and e.created_at.date() == d))
        run_series.append(sum(1 for e in events if e.kind == "run" and e.created_at.date() == d))
        scan_series.append(sum(1 for e in events if e.kind == "scan" and e.created_at.date() == d))

    return render_template(
        "dashboard.html",
        days=days,
        ai_series=ai_series,
        run_series=run_series,
        scan_series=scan_series,
    )


# --------------------------------------------------------------------------
# Editor (main app)
# --------------------------------------------------------------------------
@app.route("/app")
@login_required
def editor():
    return render_template("editor.html", ai_configured=_ai_ready)


# --------------------------------------------------------------------------
# API: AI assist & chat
# --------------------------------------------------------------------------
@app.route("/api/assist", methods=["POST"])
@login_required
def api_assist():
    data = request.get_json(force=True, silent=True) or {}
    mode = data.get("mode", "explain")
    code = (data.get("code") or "").strip()
    language = data.get("language", "python")
    instruction = (data.get("instruction") or "").strip()

    if mode not in MODE_PROMPTS:
        return jsonify({"error": f"Unknown mode '{mode}'"}), 400
    if mode != "generate" and not code:
        return jsonify({"error": "No code provided"}), 400
    if mode == "generate" and not instruction:
        return jsonify({"error": "Describe what you want generated"}), 400

    system_prompt = (
        "You are Autocode AI, a concise, expert pair-programming assistant. "
        "Always format code in fenced code blocks with the correct language tag. "
        "Keep explanations tight and skimmable."
    )
    template = MODE_PROMPTS[mode].format(language=language, instruction=instruction)
    user_message = template if mode == "generate" else f"{template}\n\n```{language}\n{code}\n```"

    try:
        reply = call_ai(system_prompt, user_message)
        record_usage(current_user, "ai")
        return jsonify({"reply": reply})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/chat", methods=["POST"])
@login_required
def api_chat():
    data = request.get_json(force=True, silent=True) or {}
    message = (data.get("message") or "").strip()
    code_context = (data.get("code") or "").strip()
    language = data.get("language", "python")
    history = data.get("history", [])

    if not message:
        return jsonify({"error": "Empty message"}), 400

    system_prompt = (
        "You are Autocode AI, a friendly, precise coding assistant embedded in a "
        "code editor. The user may reference the code currently open in their editor. "
        "Answer clearly and use fenced code blocks for any code."
    )

    user_content = message
    if code_context:
        user_content += f"\n\nCurrent editor contents ({language}):\n```{language}\n{code_context}\n```"

    try:
        reply = call_ai(system_prompt, user_content, history=history)
        record_usage(current_user, "ai")
        return jsonify({"reply": reply})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


# --------------------------------------------------------------------------
# API: OCR scan
# --------------------------------------------------------------------------
@app.route("/api/scan", methods=["POST"])
@login_required
def api_scan():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No image selected"}), 400

    filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
    filepath = os.path.join(UPLOAD_DIR, filename)
    file.save(filepath)

    try:
        image = cv2.imread(filepath)
        if image is None:
            return jsonify({"error": "Could not read image file"}), 400
        processed = preprocess_for_ocr(image)
        if pytesseract is None:
            return jsonify({
                "error": "pytesseract / Tesseract OCR is not installed. "
                         "See README for setup instructions."
            }), 501
        config = "--psm 6"
        extracted_text = pytesseract.image_to_string(processed, config=config)
        ok, buf = cv2.imencode(".png", processed)
        preview_b64 = base64.b64encode(buf).decode("utf-8") if ok else None
        record_usage(current_user, "scan")
        return jsonify({
            "text": extracted_text.strip(),
            "preview": f"data:image/png;base64,{preview_b64}" if preview_b64 else None,
        })
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


# --------------------------------------------------------------------------
# API: Code runner
# --------------------------------------------------------------------------
@app.route("/api/run", methods=["POST"])
@login_required
def api_run():
    data = request.get_json(force=True, silent=True) or {}
    code = data.get("code") or ""
    language = (data.get("language") or "python").lower()

    if not code.strip():
        return jsonify({"error": "No code to run"}), 400

    if language not in ("python", "python3"):
        return jsonify({
            "stdout": "",
            "stderr": f"Online runner currently supports Python only. "
                      f"(Selected: {language})",
            "returncode": 1,
        })

    stdout, stderr, rc = run_python_code(code)
    record_usage(current_user, "run")
    return jsonify({"stdout": stdout, "stderr": stderr, "returncode": rc})


# --------------------------------------------------------------------------
# Razorpay
# --------------------------------------------------------------------------
PLAN_AMOUNTS = {
    "pro": 49900,    # ₹499 / month in paise
    "team": 149900,  # ₹1499 / month
}


@app.route("/api/create-order", methods=["POST"])
@login_required
def create_order():
    if not _razorpay_client:
        return jsonify({"error": "Razorpay is not configured on the server."}), 501
    data = request.get_json(force=True, silent=True) or {}
    plan = data.get("plan", "pro")
    if plan not in PLAN_AMOUNTS:
        return jsonify({"error": "Unknown plan"}), 400
    amount = PLAN_AMOUNTS[plan]
    order = _razorpay_client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1,
        "notes": {"user_id": str(current_user.id), "plan": plan},
    })
    po = PaymentOrder(
        user_id=current_user.id,
        razorpay_order_id=order["id"],
        amount=amount,
        plan=plan,
        status="created",
    )
    db.session.add(po)
    db.session.commit()
    return jsonify({
        "order_id": order["id"],
        "amount": amount,
        "currency": "INR",
        "key_id": RAZORPAY_KEY_ID,
        "name": current_user.name,
        "email": current_user.email,
        "plan": plan,
    })


@app.route("/api/verify-payment", methods=["POST"])
@login_required
def verify_payment():
    if not _razorpay_client:
        return jsonify({"error": "Razorpay not configured"}), 501
    data = request.get_json(force=True, silent=True) or {}
    order_id = data.get("razorpay_order_id")
    payment_id = data.get("razorpay_payment_id")
    signature = data.get("razorpay_signature")
    try:
        _razorpay_client.utility.verify_payment_signature({
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature,
        })
    except Exception:
        return jsonify({"error": "Signature verification failed"}), 400

    po = PaymentOrder.query.filter_by(razorpay_order_id=order_id).first()
    if po:
        po.status = "paid"
        current_user.plan = po.plan
        db.session.commit()
    return jsonify({"ok": True, "plan": current_user.plan})


# --------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)