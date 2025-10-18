const API_URL = import.meta.env.VITE_FRONTEND_API_URL ?? 'http://localhost:8000';

export interface ChatRequest {
  conversationId: string;
  message: string;
}

export async function sendMessage({ conversationId, message }: ChatRequest): Promise<string> {
  const response = await fetch(${API_URL}/api/chat/stream, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      conversation_id: conversationId,
      messages: [
        { role: 'user', content: message }
      ]
    })
  });

  if (!response.body) {
    throw new Error('Streaming not supported by response');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let text = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }
    text += decoder.decode(value, { stream: true });
  }

  return text.trim();
}

