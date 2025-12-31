
import re
import ast
import random
from datetime import datetime, timezone
from typing import Optional, Set, Tuple, List, Dict, Iterable

# ------------------------------------------------------------
# Stopwords and a Knowledge Base (general tech FAQs)
# ------------------------------------------------------------
STOPWORDS: Set[str] = {
    "the","is","a","an","and","or","to","for","of","in","on","at",
    "how","what","why","who","when","where","which",
    "i","you","me","your","my","are","please","tell","show","give",
    "can","could","would","do","does","about","explain"
}

KB: List[Tuple[str, str]] = [
    ("help", "I can show time/date, do small calculations, tell jokes/quotes, "
             "answer basic tech questions, remember your name, and keep chat history."),
    ("what is your name", "I'm your Chatbot 🤖."),
    ("who are you", "I'm a simple rule‑based assistant running on Django."),
    ("what can you do", "Time/date, small math, jokes/quotes, basic tech answers, name memory, and chat history."),

    # Tech FAQs (expandable)
    ("what is python", "Python is a high‑level language known for readability and a huge ecosystem."),
    ("what is django", "Django is a high‑level Python web framework for secure, scalable apps."),
    ("what is html", "HTML defines the structure of web pages."),
    ("what is css", "CSS styles the look and layout of web pages."),
    ("what is javascript", "JavaScript adds interactivity and logic in the browser."),
    ("what is database", "A database stores and organizes data for efficient retrieval."),
    ("what is sql", "SQL is a language for querying and managing relational databases."),
    ("what is api", "An API lets software talk to other software via defined requests/responses."),
    ("what is rest api", "A REST API uses HTTP verbs (GET/POST/PUT/DELETE) and JSON over resources."),
    ("what is json", "JSON is a lightweight data format for structured data (key/value, arrays, objects)."),
    ("what is http", "HTTP is the protocol used to transfer data on the Web; HTTPS is HTTP over TLS."),
    ("what is git", "Git is a distributed version control system for tracking changes in code."),
    ("what is github", "GitHub hosts Git repositories and enables collaboration, issues, and CI/CD."),
]

JOKES = [
    "Why did the developer go broke? Because they used up all their cache. 😄",
    "I told my computer I needed a break; it said 'No problem—going to sleep.'",
    "Why do programmers prefer dark mode? Because light attracts bugs!",
]

QUOTES = [
    "Stay curious and keep shipping.",
    "Small steps every day lead to big results.",
    "Code is like humor. When you have to explain it, it’s bad. — Cory House",
]

# ------------------------------------------------------------
# Project knowledge (long, slide‑ready answers)
# ------------------------------------------------------------
PROJECT_OVERVIEW = (
    "Project: ChatBoT – A Django‑based personal chatbot with per‑user chat history and memory.\n"
    "- Overview: Users register/login, chat with a rule‑based bot, and see only their own history.\n"
    "- Personalization: Bot remembers your preferred name (“my name is …”).\n"
    "- Tech: Python (Django 5.x), HTML/CSS/JS, SQLite (dev), index/polling APIs.\n"
    "- Features: time/date, safe calculator, jokes/quotes, basic tech Q&A, name memory."
)

PROJECT_MODULES = (
    "Project Modules:\n"
    "1) User Authentication – register/login/logout, sessions.\n"
    "2) Profile & Personalization – preferred_name memory per user.\n"
    "3) Message Management – per‑user chat history (Message model).\n"
    "4) Chat API – /api/history, /api/messages?after=ID, /api/send.\n"
    "5) Bot Engine – rule‑based replies (time/date, calc, KB, jokes/quotes).\n"
    "6) Frontend UI – HTML/CSS/JS (glass theme, polling, CSRF header).\n"
    "7) Validation & Policy – username/password rules.\n"
    "8) Security & Access – login_required on chat, CSRF on APIs.\n"
    "9) Admin & Ops – view/search Messages & Profiles.\n"
    "10) Database & Migrations – SQLite dev, easy to swap DB."
)

PROJECT_STACK = (
    "Tech Stack:\n"
    "- Backend: Python 3.x, Django 5.x\n"
    "- Frontend: HTML, CSS, vanilla JS\n"
    "- DB: SQLite (dev), swappable to Postgres/MySQL\n"
    "- Auth: Django auth + sessions; CSRF on APIs\n"
    "- Deployment path: WhiteNoise + Gunicorn/NGINX"
)

PROJECT_FEATURES = (
    "Key Features:\n"
    "- Register/login/logout; per‑user chat history\n"
    "- Bot memory: “my name is …”, “what is my name”, “reset/forget my name”\n"
    "- Real‑time: time/date (local & UTC), safe calculator, jokes/quotes\n"
    "- KB + fuzzy: basic tech FAQs\n"
    "- Clean UI: typing indicator, adaptive polling, CSRF‑aware fetch"
)

PROJECT_DATABASE = (
    "Database Design:\n"
    "- Tables: auth_user (built‑in), chat_profile (preferred_name), chat_message (sender/message/created_at)\n"
    "- Relations: User 1—1 Profile; User 1—N Message\n"
    "- Constraints: UNIQUE(chat_profile.user_id); FK ON DELETE CASCADE\n"
    "- Index: chat_message(user_id, id) for fast polling/history"
)

PROJECT_ER = (
    "ER Diagram (summary):\n"
    "- USER 1—1 PROFILE (unique FK)\n"
    "- USER 1—N MESSAGE (FK)\n"
    "- No BOT/CONVERSATION tables in current schema (sender marks user/bot)"
)

PROJECT_DFD = (
    "DFD Summary:\n"
    "- Level‑0: User ↔ ChatBoT System (login/signup, send message, request history, logout)\n"
    "- Level‑1: Auth & Sessions, Chat API, Bot Engine + Stores (User/Profile/Message/Session)\n"
    "- Level‑2: Auth (register/login/logout), Chat (history/send/poll), Bot (intents + KB + compose)"
)

PROJECT_HOW_TO_RUN = (
    "How to Run:\n"
    "1) pip install django\n"
    "2) python manage.py makemigrations chat\n"
    "3) python manage.py migrate\n"
    "4) python manage.py runserver → open http://127.0.0.1:8000\n"
    "5) Register → Login → Chat"
)

PROJECT_LIMITATIONS = (
    "Limitations:\n"
    "- Rule‑based (not an LLM), no external APIs (e.g., live weather)\n"
    "- Polling (not WebSockets) in this build\n"
    "- Simple KB; no semantic search"
)

PROJECT_FUTURE = (
    "Future Work:\n"
    "- Strong password policy & breached‑password check\n"
    "- Conversations/threads, attachments, search\n"
    "- WebSockets (real‑time), analytics, admin dashboards\n"
    "- Optionally plug in an LLM or retrieval‑augmented search"
)

PROJECT_SECURITY = (
    "Security Notes:\n"
    "- CSRF on chat APIs; sessions isolate per‑user data\n"
    "- For production: enable CSRF on auth forms, HTTPS, secure cookies, DEBUG=False\n"
    "- Avoid logging sensitive content in production"
)

# Map trigger buckets → answer
PROJECT_QA: Dict[str, Iterable[str]] = {
    "about_project": [
        "about your project", "about this project", "tell me about your project",
        "project overview", "project description", "describe your project"
    ],
    "modules": [
        "project modules", "module description", "modules of your project", "components of your project"
    ],
    "stack": [
        "tech stack", "technology stack", "tools used", "frameworks used"
    ],
    "features": [
        "features", "key features", "project features"
    ],
    "database": [
        "database design", "db design", "tables", "schema"
    ],
    "er": [
        "er diagram", "entity relationship", "er summary"
    ],
    "dfd": [
        "dfd", "data flow diagram"
    ],
    "how_to_run": [
        "how to run", "setup", "installation steps", "run project"
    ],
    "limitations": [
        "limitations", "constraints of project", "disadvantages"
    ],
    "future": [
        "future work", "next steps", "improvements"
    ],
    "security": [
        "security", "security notes", "prod security", "harden"
    ],
}

PROJECT_ANSWERS: Dict[str, str] = {
    "about_project": PROJECT_OVERVIEW,
    "modules": PROJECT_MODULES,
    "stack": PROJECT_STACK,
    "features": PROJECT_FEATURES,
    "database": PROJECT_DATABASE,
    "er": PROJECT_ER,
    "dfd": PROJECT_DFD,
    "how_to_run": PROJECT_HOW_TO_RUN,
    "limitations": PROJECT_LIMITATIONS,
    "future": PROJECT_FUTURE,
    "security": PROJECT_SECURITY,
}

def _match_project_q(text: str) -> Optional[str]:
    t = text.lower().strip()
    for key, patterns in PROJECT_QA.items():
        for p in patterns:
            if p in t:
                return PROJECT_ANSWERS[key]
    # Extra flexible catch: “project ...” + common words
    if "project" in t and any(w in t for w in ["about", "overview", "describe", "details", "explain"]):
        return PROJECT_OVERVIEW
    return None

# ------------------------------------------------------------
# Tokenizer & Jaccard (used in KB fuzzy)
# ------------------------------------------------------------
def tokenize(text: str) -> Set[str]:
    text = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    return {t for t in text.split() if t and t not in STOPWORDS}

def jaccard(a: Set[str], b: Set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0

# ------------------------------------------------------------
# Dynamic intents: time/date, jokes/quotes, calculator
# ------------------------------------------------------------
def time_date_intents(t: str) -> Optional[str]:
    t_low = t.lower()
    if "utc" in t_low and "time" in t_low:
        return "UTC time is " + datetime.now(timezone.utc).strftime("%H:%M:%S") + "."
    if "time" in t_low or "clock" in t_low:
        return "The current time is " + datetime.now().strftime("%I:%M %p") + "."
    if "date" in t_low or "today" in t_low:
        return "Today is " + datetime.now().strftime("%A, %d %B %Y") + "."
    if "day" in t_low and "week" in t_low:
        return "It’s " + datetime.now().strftime("%A") + "."
    if "month" in t_low:
        return "We are in " + datetime.now().strftime("%B") + "."
    if "year" in t_low:
        return "It’s " + datetime.now().strftime("%Y") + "."
    return None

def joke_quote_intents(t: str) -> Optional[str]:
    t_low = t.lower()
    if any(k in t_low for k in ["joke", "funny", "laugh"]):
        return random.choice(JOKES)
    if any(k in t_low for k in ["quote", "motivate", "inspire"]):
        return random.choice(QUOTES)
    return None

# Safe calculator
_ALLOWED_BINOPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow)
_ALLOWED_UNARY = (ast.UAdd, ast.USub)

def _eval_ast(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _eval_ast(node.body)
    if isinstance(node, ast.BinOp) and isinstance(node.op, _ALLOWED_BINOPS):
        left = _eval_ast(node.left)
        right = _eval_ast(node.right)
        if isinstance(node.op, ast.Div) and right == 0:
            raise ZeroDivisionError
        return {
            ast.Add: lambda a,b: a+b,
            ast.Sub: lambda a,b: a-b,
            ast.Mult: lambda a,b: a*b,
            ast.Div: lambda a,b: a/b,
            ast.Mod: lambda a,b: a%b,
            ast.Pow: lambda a,b: a**b,
        }[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, _ALLOWED_UNARY):
        val = _eval_ast(node.operand)
        return +val if isinstance(node.op, ast.UAdd) else -val
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if hasattr(ast, "Num") and isinstance(node, ast.Num):  # py<3.8
        return float(node.n)
    raise ValueError("Unsafe expression")

_CALC_TRIGGER = re.compile(r"\b(calculate|calc|compute|evaluate|what\s+is|whats)\b", re.I)
_EXPR_CAPTURE = re.compile(r"([-+/*%\d\.\(\)\s\^]+)")

def calculator_intent(t: str) -> Optional[str]:
    if not _CALC_TRIGGER.search(t) and not any(ch.isdigit() for ch in t):
        return None
    m = _EXPR_CAPTURE.search(t)
    if not m:
        return None
    expr = m.group(1).strip().replace("^", "**")
    if not re.fullmatch(r"[0-9\.\s\+\-\*\/\%\(\)\*]*", expr):
        return None
    try:
        node = ast.parse(expr, mode="eval")
        val = _eval_ast(node)
        return f"{expr} = {val:g}"
    except ZeroDivisionError:
        return "Division by zero is not allowed."
    except Exception:
        return None

# ------------------------------------------------------------
# Follow‑ups when unknown
# ------------------------------------------------------------
FOLLOWUPS = [
    "Would you like the current time/date, a small calculation, a joke, or a quick tech definition?",
    "I can do time/date, calculator, jokes/quotes, or basics like 'what is Django'. What would you like?",
    "Try: 'time', 'date', 'calculate 12*(3+4)', 'joke', or 'what is Python'. What shall we try?",
]
def followup_question() -> str:
    return random.choice(FOLLOWUPS)

# ------------------------------------------------------------
# Main function
# ------------------------------------------------------------
def generate_bot_reply(user_text: str, name: Optional[str] = None) -> str:
    # 0) Project Q&A (long answers)
    proj = _match_project_q(user_text)
    if proj:
        return proj

    # 1) Real‑time intents
    out = time_date_intents(user_text)
    if out:
        return out

    out = calculator_intent(user_text)
    if out:
        return out

    out = joke_quote_intents(user_text)
    if out:
        return out

    # 2) Greeting (with time‑of‑day; personalized if name known)
    utoks = tokenize(user_text)
    if utoks & {"hello", "hi", "hey", "yo", "greetings", "good", "morning", "afternoon", "evening"}:
        hour = datetime.now().hour
        period = "morning" if 5 <= hour < 12 else "afternoon" if 12 <= hour < 17 else "evening"
        if name:
            return f"Good {period}, {name}! How can I help you today?"
        return f"Good {period}! How can I help you today?"

    # 3) Fuzzy KB match (general tech)
    best_score, best_answer = 0.0, None
    for q, a in KB:
        score = jaccard(utoks, tokenize(q))
        if score > best_score:
            best_score, best_answer = score, a
    if best_score >= 0.22:
        return best_answer

    # 4) Unknown → ask a question back
    return followup_question()