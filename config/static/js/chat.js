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
const selectBar = document.getElementById("select-bar");
const selectCancelBtn = document.getElementById("select-cancel");
const selectDeleteBtn = document.getElementById("select-delete");

let state = loadState();
let selectMode = false;
const selectedIds = new Set();

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
  const activeId = chats.some((c) => c.id === parsed.activeId)
    ? parsed.activeId
    : chats[0].id;
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

function updateSelectBar() {
  const count = selectedIds.size;
  selectDeleteBtn.disabled = count === 0;
  selectDeleteBtn.textContent = count ? `Delete (${count})` : "Delete";
}

function enterSelectMode(initialId) {
  selectMode = true;
  selectedIds.clear();
  if (initialId) selectedIds.add(initialId);
  closeAllChatMenus();
  sidebar.classList.add("selecting");
  selectBar.hidden = false;
  updateSelectBar();
  renderChatList();
}

function exitSelectMode() {
  selectMode = false;
  selectedIds.clear();
  sidebar.classList.remove("selecting");
  selectBar.hidden = true;
  updateSelectBar();
  renderChatList();
}

function toggleSelected(id) {
  if (selectedIds.has(id)) selectedIds.delete(id);
  else selectedIds.add(id);
  updateSelectBar();
  renderChatList();
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
    const isSelected = selectedIds.has(chat.id);
    item.className = `chat-item${
      !selectMode && chat.id === state.activeId ? " active" : ""
    }${isSelected ? " selected" : ""}`;

    if (selectMode) {
      const check = document.createElement("input");
      check.type = "checkbox";
      check.className = "chat-check";
      check.checked = isSelected;
      check.addEventListener("click", (event) => {
        event.stopPropagation();
        toggleSelected(chat.id);
      });

      const main = document.createElement("button");
      main.type = "button";
      main.className = "chat-item-main";
      main.textContent = chat.title;
      main.addEventListener("click", () => toggleSelected(chat.id));

      item.append(check, main);
      chatListEl.appendChild(item);
      continue;
    }

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
      <button type="button" data-action="select">Select</button>
      <button type="button" data-action="pin">Pin chat</button>
      <button type="button" class="danger" data-action="delete">Delete</button>
    `;
    menu.addEventListener("click", (event) => {
      event.stopPropagation();
      const action = event.target.closest("button")?.dataset.action;
      if (action === "delete") {
        deleteChat(chat.id);
      } else if (action === "rename") {
        closeAllChatMenus();
        beginRename(chat.id, item, main);
      } else if (action === "select") {
        enterSelectMode(chat.id);
      }
      // pin stays UI-only for now
    });

    item.append(main, more, menu);
    chatListEl.appendChild(item);
  }
}

function beginRename(id, item, titleBtn) {
  const chat = state.chats.find((c) => c.id === id);
  if (!chat) return;

  const input = document.createElement("input");
  input.type = "text";
  input.className = "chat-item-rename";
  input.value = chat.title;
  input.maxLength = 60;

  titleBtn.replaceWith(input);
  item.classList.add("renaming");
  input.focus();
  input.select();

  let finished = false;

  function finish(save) {
    if (finished) return;
    finished = true;
    const next = input.value.replace(/\s+/g, " ").trim();
    if (save && next) {
      chat.title = next;
      chat.updatedAt = Date.now();
      saveState();
    }
    renderChatList();
    renderMessages();
  }

  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      finish(true);
    } else if (event.key === "Escape") {
      event.preventDefault();
      finish(false);
    }
  });

  input.addEventListener("blur", () => finish(true));
  input.addEventListener("click", (event) => event.stopPropagation());
}

function deleteChat(id) {
  closeAllChatMenus();
  if (state.chats.length === 1) {
    state.chats[0] = createChat();
    state.activeId = state.chats[0].id;
  } else {
    state.chats = state.chats.filter((c) => c.id !== id);
    if (state.activeId === id) {
      state.activeId = state.chats[0].id;
    }
  }
  saveState();
  renderChatList();
  renderMessages();
}

function deleteSelectedChats() {
  if (!selectedIds.size) return;

  const remaining = state.chats.filter((c) => !selectedIds.has(c.id));
  if (!remaining.length) {
    const chat = createChat();
    state.chats = [chat];
    state.activeId = chat.id;
  } else {
    state.chats = remaining;
    if (!remaining.some((c) => c.id === state.activeId)) {
      state.activeId = remaining[0].id;
    }
  }

  saveState();
  exitSelectMode();
  renderMessages();
}

function startNewChat() {
  if (selectMode) exitSelectMode();
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

// 3.3 Connect App
form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = promptEl.value.trim();
  if (!text) return;

  appendMessage("user", text);
  promptEl.value = "";
  autosize();
  sendBtn.disabled = true;
  
  try {
    const res = await fetch("/chat/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    const data = await res.json();
    if (!res.ok) {
      appendMessage("assistant", data.error || "Request failed.");
      return;
    }
    appendMessage("assistant", data.message || "No reply.");
  } catch (_) {
    appendMessage("assistant", "Request failed.");
  } finally {
    sendBtn.disabled = false;
    promptEl.focus();
  }
});

newChatBtn.addEventListener("click", startNewChat);
menuBtn.addEventListener("click", openSidebar);
selectCancelBtn.addEventListener("click", exitSelectMode);
selectDeleteBtn.addEventListener("click", deleteSelectedChats);
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
