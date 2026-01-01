Overview
A simple Django-based chatbot with per-user chat history and a small memory (preferred name). Users register/login, chat with a rule-based bot, and see only their own history.

Repository
https://github.com/MrSuyog/ChatBot

FEATURES

Register / Login / Logout (Django auth + sessions)
Per-user chat history (Message model)
Bot memory:
• “my name is Suresh”
• “what is my name”
• “reset” / “forget my name”
Real-time style replies:
• Time & date (local + UTC)
• Safe calculator (“calculate 12*(3+4)”, “what is 2+2”)
• Jokes / Quotes
• Basic tech FAQs (Python, Django, HTML/CSS/JS, API/REST)
• Project Q&A (overview, modules, stack, features, DB, ER/DFD, how to run, limitations, future work, security)
• If unknown, bot asks a follow-up question
Clean UI (HTML/CSS/JS), CSRF-aware fetch, adaptive polling
SQLite in development (easy to switch to Postgres/MySQL)
TECH STACK

Backend: Python 3.x, Django 5.x
Frontend: HTML, CSS, vanilla JS
Database: SQLite (dev)
Auth: Django auth + sessions
PROJECT STRUCTURE (short)
chatproject/
chat/ Django app (static, templates, bot_logic, views, models, forms, urls)
chatproject/ Django project (settings, urls, wsgi/asgi)
manage.py
requirements.txt
.gitignore ignores venv/, db.sqlite3, .env, pycache/ etc.

QUICK START

Requirements

-Python 3.10+ and pip
-Git (if cloning)
-SQLite (bundled with Python)
-Create and activate virtualenv

-Windows (CMD/PowerShell)
-python -m venv venv
-venv\Scripts\activate

-macOS/Linux
-python3 -m venv venv
-source venv/bin/activate

Install dependencies
-pip install -r requirements.txt

Environment variables (create .env next to manage.py)
DJANGO_SECRET_KEY=replace-with-a-strong-random-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

Migrate and run
-python manage.py makemigrations chat
-python manage.py migrate
-python manage.py runserver
-Open http://127.0.0.1:8000

Create admin user (optional)
-python manage.py createsuperuser
-Open http://127.0.0.1:8000/admin

HOW IT WORKS

Flow

UI loads recent history via GET /api/history, then polls GET /api/messages?after=<id>.
When a user sends a message, UI calls POST /api/send with JSON {"message": "..."}.
Server saves the user message, generates a reply via bot_logic.py, saves the reply, and returns both as JSON.
Name memory is saved in Profile.preferred_name (handled in views).
Bot capabilities (examples)

Time/Date: “time”, “date”, “today”, “UTC time”, “day of week”, “month”, “year”
Calculator (safe): “calculate 12*(3+4)”, “what is 2+2”, “9/3^2”
Jokes/Quotes: “joke”, “funny”, “quote”, “motivate”, “inspire”
Tech FAQs: “what is python/django/html/css/javascript/api/rest api/sql”
Project Q&A: “tell me about your project”, “project modules”, “tech stack”, “features”, “database design”, “er diagram”, “dfd”, “how to run”, “limitations”, “future work”, “security”
If unknown: bot asks a helpful follow-up question
Name memory

“my name is Suresh” → remembers name
“what is my name” → replies with saved name
“reset” / “forget my name” → clears saved name
API endpoints

GET /api/history → returns last N messages for current user
GET /api/messages?after=<id> → returns messages where id > after (polling)
POST /api/send → saves user message, generates and saves bot reply; returns both
DATABASE DESIGN (SUMMARY)

Tables:
• auth_user (built-in Django users)
• chat_profile (user_id UNIQUE FK, preferred_name, created_at, updated_at)
• chat_message (user_id FK, sender in {'user','bot'}, message, created_at)
Relations:
• User 1—1 Profile (unique FK to user)
• User 1—N Message
Index:
• chat_message(user_id, id) for fast “after=lastId” polling and history
SECURITY NOTES

Development posture:
• Chat APIs use CSRF; index view sets CSRF cookie; JS sends X-CSRFToken.
• Auth forms are CSRF-exempt to allow pure HTML forms.
Production hardening:
• Enable CSRF on auth forms (remove @csrf_exempt; add {% csrf_token %} or JS injector)
• DEBUG=False, strong DJANGO_SECRET_KEY, proper ALLOWED_HOSTS
• HTTPS and secure cookies
• Avoid logging sensitive message content
CONFIGURATION

Current dev policy:
• Username: exactly 6 alphanumeric characters
• Password: exactly 6 alphanumeric characters (custom validator)
Recommended production policy:
• Username: 3–30 letters/digits/._-
• Password: minimum 12 characters, any characters; optionally check against breached lists
Database (SQLite in settings.py):
DATABASES = {
'default': {
'ENGINE': 'django.db.backends.sqlite3',
'NAME': BASE_DIR / 'db.sqlite3',
}
}
DEPLOYMENT (OVERVIEW)

Set environment variables: DJANGO_SECRET_KEY, DEBUG=False, ALLOWED_HOSTS=yourdomain
Run migrations: python manage.py migrate
Serve with Gunicorn (and NGINX as reverse proxy) or a platform service
Use WhiteNoise or a proper static files solution
Prefer Postgres for production
TROUBLESHOOTING

CSRF errors on /api/send:
• Ensure index view uses @ensure_csrf_cookie
• Requests include X-CSRFToken
• User is logged in
“no such table: chat_message”:
• Run migrations: python manage.py makemigrations chat && python manage.py migrate
Username/password rejected:
• Dev rule requires exactly 6 alphanumeric characters; adjust forms/validators if needed
Old JS/CSS cached:
• Hard refresh (Ctrl+F5) or bump query strings (e.g., app.js?v=11)
ROADMAP / FUTURE WORK

Strong password policy (min 12) + breached password validator
Conversations/threads, attachments, search
WebSockets for real-time updates
Analytics and admin dashboards
Optional LLM integration (RAG)
LICENSE
Add a license file (e.g., MIT) if you want others to use or contribute.

CONTACT / NOTES

Maintainer: Suyog Sonawane (GitHub: MrSuyog)
To run locally: follow Quick Start above.
To contribute: open issues or pull requests on the GitHub repository.
