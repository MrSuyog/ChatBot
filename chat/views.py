
# chat/views.py
import re
import json, time, logging
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from .forms import RegisterForm, LoginForm
from .models import Message, Profile
from .bot_logic import generate_bot_reply

log = logging.getLogger(__name__)

# -------- Auth pages (CSRF disabled for these plain-HTML forms) --------
@csrf_exempt
def register_view(request):
    if request.user.is_authenticated:
        return redirect("index")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(user=user)
            # Redirect to login with a flag; do NOT log in here.
            return redirect("/login/?registered=1")
    else:
        form = RegisterForm()
    return render(request, "chat/register.html", {"form": form})

@csrf_exempt
def login_view(request):
    if request.user.is_authenticated:
        return redirect("index")
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            # If the flag is present, carry it to the chat page to show a toast
            registered_flag = request.POST.get("registered") or request.GET.get("registered")
            if registered_flag == "1":
                return redirect("/?registered=1")
            return redirect("index")
    else:
        form = LoginForm(request)
    return render(request, "chat/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("login")

# -------- Chat pages & APIs (CSRF enabled here) --------
@ensure_csrf_cookie
@login_required
def index(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    preferred = profile.preferred_name or request.user.first_name or ""
    return render(request, "chat/index.html", {"preferred_name": preferred})

@login_required
@require_GET
def api_history(request):
    msgs = Message.objects.filter(user=request.user).order_by("id")[:200]
    return JsonResponse({"messages": [m.as_dict() for m in msgs]})

@login_required
@require_GET
def api_messages(request):
    after = request.GET.get("after", "0")
    try:
        after_id = int(after)
    except (ValueError, TypeError):
        after_id = 0
    msgs = Message.objects.filter(user=request.user, id__gt=after_id).order_by("id")
    return JsonResponse({"messages": [m.as_dict() for m in msgs]})

def _get_profile(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile

def _try_extract_name(text: str):
    m = re.search(r"\b(?:my name is|i am|i'm|call me)\s+([A-Za-z][A-Za-z\s'-]{0,40})\b", text, re.I)
    if not m:
        return None
    name = m.group(1).strip()
    name = re.sub(r"[^\w\s'-]", "", name).strip()
    return " ".join(w.capitalize() for w in re.split(r"\s+", name))

def _is_asking_name(text: str) -> bool:
    t = text.lower()
    return bool(re.search(r"\b(what('?s| is)\s+my\s+name|who\s+am\s+i|do\s+you\s+remember\s+my\s+name)\b", t))

def _is_reset(text: str) -> bool:
    t = text.lower()
    return any(p in t for p in ["reset", "clear chat", "clear history", "forget my name"])

@login_required
@require_POST
def api_send(request):
    profile = _get_profile(request.user)
    try:
        data = json.loads((request.body or b"{}").decode("utf-8"))
    except Exception as e:
        return HttpResponseBadRequest(f"Invalid JSON: {e}")

    text = (data.get("message") or "").strip()
    if not text:
        return JsonResponse({"error": "Message cannot be empty"}, status=400)

    user_msg = Message.objects.create(user=request.user, sender=Message.USER, message=text)

    if _is_reset(text):
        profile.preferred_name = None
        profile.save(update_fields=["preferred_name", "updated_at"])
        reply = "Okay, I’ve cleared your name."
        bot_msg = Message.objects.create(user=request.user, sender=Message.BOT, message=reply)
        return JsonResponse({"user_message": user_msg.as_dict(), "bot_message": bot_msg.as_dict()})

    maybe_name = _try_extract_name(text)
    if maybe_name:
        profile.preferred_name = maybe_name
        profile.save(update_fields=["preferred_name", "updated_at"])
        reply = f"Nice to meet you, {maybe_name}! I’ll remember your name."
        bot_msg = Message.objects.create(user=request.user, sender=Message.BOT, message=reply)
        return JsonResponse({"user_message": user_msg.as_dict(), "bot_message": bot_msg.as_dict()})

    if _is_asking_name(text):
        if profile.preferred_name or request.user.first_name:
            known = profile.preferred_name or request.user.first_name
            reply = f"Your name is {known}."
        else:
            reply = "I don't know your name yet. Tell me by saying “My name is <YourName>”."
        bot_msg = Message.objects.create(user=request.user, sender=Message.BOT, message=reply)
        return JsonResponse({"user_message": user_msg.as_dict(), "bot_message": bot_msg.as_dict()})

    try:
        name = profile.preferred_name or request.user.first_name or None
        reply = generate_bot_reply(text, name=name)
    except Exception as e:
        log.exception("generate_bot_reply failed")
        reply = f"Sorry, I hit an error: {e}"

    time.sleep(0.2)
    bot_msg = Message.objects.create(user=request.user, sender=Message.BOT, message=reply)
    return JsonResponse({"user_message": user_msg.as_dict(), "bot_message": bot_msg.as_dict()})