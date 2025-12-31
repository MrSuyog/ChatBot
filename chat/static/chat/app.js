
const chat = document.getElementById("chat");
const input = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const typingEl = document.getElementById("typing");

let lastId = 0;
const renderedIds = new Set();

let polling = false;
let pollTimeout = null;
let nextDelay = 1000;
const MIN_DELAY = 1000;
const MAX_DELAY = 15000;
const IDLE_TIMEOUT = 60000;
let idleTimer = null;
let isIdle = false;

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return decodeURIComponent(parts.pop().split(';').shift());
  return null;
}
const csrftoken = getCookie('csrftoken');

window.addEventListener("DOMContentLoaded", async () => {
  await loadHistory();
  startPolling();
  setupActivityDetection();
  setupVisibilityHandlers();
  setupOnlineOffline();
});

sendBtn.addEventListener("click", onSend);
input.addEventListener("keydown", (e) => { if (e.key === "Enter") onSend(); });

async function onSend() {
  const text = input.value.trim();
  if (!text) return;

  const tempEl = addMessage({ id: null, sender: "user", message: text, timestamp: new Date().toISOString() }, true);

  typingEl.classList.remove("hidden");
  input.value = "";
  input.focus();

  isIdle = false;
  nextDelay = MIN_DELAY;
  if (!polling && !document.hidden && navigator.onLine) startPolling();

  try {
    const res = await fetch("/api/send", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json", "X-CSRFToken": csrftoken || "" },
      body: JSON.stringify({ message: text }),
    });

    let data = {}; try { data = await res.json(); } catch {}
    if (!res.ok) throw new Error(`Failed to send (${res.status})`);

    if (tempEl && tempEl.parentNode) tempEl.parentNode.removeChild(tempEl);

    [data.user_message, data.bot_message].filter(Boolean).forEach((m) => {
      if (!renderedIds.has(m.id)) {
        addMessage(m); renderedIds.add(m.id); lastId = Math.max(lastId, m.id);
      }
    });
  } catch (err) {
    console.error(err);
    if (tempEl) tempEl.classList.add("error");
    alert("Error sending message. Are you logged in? Check server console.");
  } finally {
    typingEl.classList.add("hidden");
    scrollToBottom();
  }
}

async function loadHistory() {
  try {
    const res = await fetch("/api/history", { credentials: "same-origin" });
    if (!res.ok) throw new Error(`Failed to load history (${res.status})`);
    const data = await res.json();

    chat.innerHTML = "";
    (data.messages || []).forEach((m) => {
      addMessage(m);
      renderedIds.add(m.id);
      lastId = Math.max(lastId, m.id);
    });
    scrollToBottom();
  } catch (e) {
    console.error("Failed to load history", e);
  }
}

function startPolling() { if (!polling) { polling = true; scheduleNextPoll(MIN_DELAY); } }
function stopPolling() { polling = false; if (pollTimeout) { clearTimeout(pollTimeout); pollTimeout = null; } }
function scheduleNextPoll(delay) { if (!polling) return; if (pollTimeout) clearTimeout(pollTimeout); pollTimeout = setTimeout(fetchNewMessages, delay); }

async function fetchNewMessages() {
  if (!polling || document.hidden || isIdle || !navigator.onLine) return;
  try {
    const res = await fetch(`/api/messages?after=${lastId}`, { credentials: "same-origin" });
    if (!res.ok) throw new Error("poll failed");
    const data = await res.json();
    const msgs = data.messages || [];

    if (msgs.length > 0) {
      msgs.forEach((m) => {
        if (!renderedIds.has(m.id)) {
          addMessage(m); renderedIds.add(m.id); lastId = Math.max(lastId, m.id);
        }
      });
      nextDelay = MIN_DELAY; typingEl.classList.add("hidden"); scrollToBottom();
    } else {
      nextDelay = Math.min(MAX_DELAY, Math.round(nextDelay * 1.7));
    }
  } catch (e) {
    console.error("Polling error:", e);
    nextDelay = Math.min(MAX_DELAY, Math.round(nextDelay * 2));
  } finally {
    scheduleNextPoll(nextDelay);
  }
}

function setupActivityDetection() {
  const markActive = () => {
    isIdle = false; nextDelay = MIN_DELAY;
    if (!polling && !document.hidden && navigator.onLine) startPolling();
    if (idleTimer) clearTimeout(idleTimer);
    idleTimer = setTimeout(() => { isIdle = true; stopPolling(); }, IDLE_TIMEOUT);
  };
  ["mousemove", "keydown", "click", "touchstart"].forEach((evt) => window.addEventListener(evt, markActive));
  markActive();
}
function setupVisibilityHandlers() { document.addEventListener("visibilitychange", () => { if (document.hidden) stopPolling(); else if (!isIdle && navigator.onLine) startPolling(); }); }
function setupOnlineOffline() { window.addEventListener("offline", () => stopPolling()); window.addEventListener("online", () => { if (!document.hidden && !isIdle) startPolling(); }); }

function addMessage(m, isTemp = false) {
  const wrapper = document.createElement("div");
  wrapper.className = `msg ${m.sender}${isTemp ? " pending" : ""}`;
  if (m.id) wrapper.dataset.id = m.id;

  const content = document.createElement("div");
  content.textContent = m.message;

  const meta = document.createElement("span");
  meta.className = "meta";
  meta.textContent = formatTime(m.timestamp || new Date().toISOString());

  wrapper.appendChild(content);
  wrapper.appendChild(meta);
  chat.appendChild(wrapper);
  return wrapper;
}

function scrollToBottom() { chat.scrollTop = chat.scrollHeight; }
function formatTime(iso) { try { return new Date(iso).toLocaleString(); } catch { return ""; } }