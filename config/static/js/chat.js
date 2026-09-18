// 3.1 Frontend

const STORAGE_KEY = "researchai.chats.v2";
const DEFAULT_TITLE = "ResearchAI";

const form = document.getElementById("composer");
const promptEl = document.getElementById("prompt");
const sendBtn = document.getElementById("send");
const uploadBtn = document.getElementById("upload-btn");
const messagesEl = document.getElementById("messages");
const emptyState = document.getElementById("empty-state");
const chatEl = document.getElementById("chat");
const chatListEl = document.getElementById("chat-list");
const currentTitleEl = document.getElementById("current-title");
const newChatBtn = document.getElementById("new-chat");
const menuBtn = document.getElementById("menu-btn");
const sidebar = document.getElementById("sidebar");
const backdrop = document.getElementById("backdrop");

let state = loadState();

function uid() {
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
}

function createChat(title = DEFAULT_TITLE) {
  return {
    id: uid(),
    title,
    updatedAt: Date.now(),
    messages: [],
  };
}

function normalizeState(parsed) {
  const chats = (parsed.chats || []).map((chat) => ({
    ...chat,
    title:
      !chat.title || chat.title === "New chat" ? DEFAULT_TITLE : chat.title,
  }));
  if (!chats.length) {
    const chat = createChat();
    return { activeId: chat.id, chats: [chat] };
  }
  const activeId =
    chats.some((c) => c.id === parsed.activeId) ? parsed.activeId : chats[0].id;
  return { activeId, chats };
}

function loadState() {
  try {
    const raw =
      localStorage.getItem(STORAGE_KEY) ||
      localStorage.getItem("researchai.chats.v1");
    if (raw) {
      const parsed = JSON.parse(raw);
      if (parsed?.chats?.length) return normalizeState(parsed);
    }
  } catch (_) {
    /* ignore */
  }
  const chat = createChat();
  return { activeId: chat.id, chats: [chat] };
}

function saveState() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function activeChat() {
  return state.chats.find((c) => c.id === state.activeId) || state.chats[0];
}

function autosize() {
  promptEl.style.height = "auto";
  promptEl.style.height = `${Math.min(promptEl.scrollHeight, 160)}px`;
}

function closeSidebar() {
  sidebar.classList.remove("open");
  backdrop.hidden = true;
}

function openSidebar() {
  sidebar.classList.add("open");
  backdrop.hidden = false;
}

function closeAllChatMenus() {
  document.querySelectorAll(".chat-item.menu-open").forEach((el) => {
    el.classList.remove("menu-open");
  });
}

function renderMessages() {
  const chat = activeChat();
  messagesEl.innerHTML = "";
  currentTitleEl.textContent = chat.title;

  if (!chat.messages.length) {
    emptyState.hidden = false;
    messagesEl.hidden = true;
    return;
  }

  emptyState.hidden = true;
  messagesEl.hidden = false;

  for (const message of chat.messages) {
    const row = document.createElement("article");
    row.className = `msg ${message.role}`;

    const body = document.createElement("div");
    body.className = "msg-body";
    body.textContent = message.content;

    row.append(body);
    messagesEl.appendChild(row);
  }

  chatEl.scrollTop = chatEl.scrollHeight;
}

function renderChatList() {
  chatListEl.innerHTML = "";
  const chats = [...state.chats].sort((a, b) => b.updatedAt - a.updatedAt);

  for (const chat of chats) {
    const item = document.createElement("div");
    item.className = `chat-item${chat.id === state.activeId ? " active" : ""}`;

    const main = document.createElement("button");
    main.type = "button";
    main.className = "chat-item-main";
    main.textContent = chat.title;
    main.addEventListener("click", () => {
      closeAllChatMenus();
      state.activeId = chat.id;
      saveState();
      renderChatList();
      renderMessages();
      closeSidebar();
      promptEl.focus();
    });

    const more = document.createElement("button");
    more.type = "button";
    more.className = "chat-item-more";
    more.setAttribute("aria-label", "Chat options");
    more.textContent = "⋯";
    more.addEventListener("click", (event) => {
      event.stopPropagation();
      const wasOpen = item.classList.contains("menu-open");
      closeAllChatMenus();
      if (!wasOpen) item.classList.add("menu-open");
    });

    const menu = document.createElement("div");
    menu.className = "chat-menu";
    menu.innerHTML = `
      <button type="button" data-action="rename">Rename</button>
      <button type="button" data-action="pin">Pin chat</button>
      <button type="button" class="danger" data-action="delete">Delete</button>
    `;
    // Menu options are UI-only for now (no handlers).

    item.append(main, more, menu);
    chatListEl.appendChild(item);
  }
}

function startNewChat() {
  closeAllChatMenus();
  const chat = createChat();
  state.chats.unshift(chat);
  state.activeId = chat.id;
  saveState();
  renderChatList();
  renderMessages();
  closeSidebar();
  promptEl.focus();
}

function titleFromPrompt(text) {
  const clean = text.replace(/\s+/g, " ").trim();
  return clean.length > 36 ? `${clean.slice(0, 36)}…` : clean;
}

function appendMessage(role, content) {
  const chat = activeChat();
  chat.messages.push({ role, content, createdAt: Date.now() });
  chat.updatedAt = Date.now();
  if (role === "user" && chat.title === DEFAULT_TITLE) {
    chat.title = titleFromPrompt(content);
  }
  saveState();
  renderChatList();
  renderMessages();
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const text = promptEl.value.trim();
  if (!text) return;

  appendMessage("user", text);
  promptEl.value = "";
  autosize();
  sendBtn.disabled = true;

  // Static page only — placeholder reply until the mock API step.
  window.setTimeout(() => {
    appendMessage(
      "assistant",
      "This is a static UI preview. Backend chat comes next."
    );
    sendBtn.disabled = false;
    promptEl.focus();
  }, 350);
});

newChatBtn.addEventListener("click", startNewChat);
menuBtn.addEventListener("click", openSidebar);
backdrop.addEventListener("click", () => {
  closeSidebar();
  closeAllChatMenus();
});

// Upload is UI-only for now (no file handling / backend).
uploadBtn.addEventListener("click", (event) => {
  event.preventDefault();
});

document.addEventListener("click", (event) => {
  if (!event.target.closest(".chat-item")) {
    closeAllChatMenus();
  }
});

promptEl.addEventListener("input", autosize);
promptEl.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

renderChatList();
renderMessages();
autosize();
promptEl.focus();
