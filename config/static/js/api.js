// Network layer: all calls to the Django backend live here.
// Each function returns { ok, data } so callers can handle errors uniformly.

export async function uploadFile(file) {
  const body = new FormData();
  body.append("file", file);

  const response = await fetch("/upload/", {
    method: "POST",
    body,
  });
  const data = await response.json();
  return { ok: response.ok, data };
}

export async function sendChatMessage(text, conversationId) {
  const response = await fetch("/chat/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: text,
      conversation_id: conversationId,
    }),
  });
  const data = await response.json();
  return { ok: response.ok, data };
}
