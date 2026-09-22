// State layer: owns the chat state and its localStorage persistence.

const STORAGE_KEY = "researchai.chats.v2";
export const DEFAULT_TITLE = "ResearchAI";

function uid() {
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
}

export function createChat(title = DEFAULT_TITLE) {
  return {
    id: uid(),
    conversationId: null, // backend Conversation.id
    title,
    updatedAt: Date.now(),
    messages: [],
  };
}

function normalizeState(parsed) {
  const chats = (parsed.chats || []).map((chat) => ({
    ...chat,
    conversationId: chat.conversationId ?? null,
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

const state = loadState();

// Returns the single shared state object. Callers mutate its properties
// (state.chats, state.activeId, ...) and then call saveState().
export function getState() {
  return state;
}

export function saveState() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

export function activeChat() {
  return state.chats.find((c) => c.id === state.activeId) || state.chats[0];
}
