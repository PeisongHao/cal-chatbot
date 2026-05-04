import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export interface ChatRequest {
  message: string;
  session_id?: string | null;
}

export interface ChatResponse {
  reply: string;
  session_id: string;
}

export async function sendChatMessage(
  payload: ChatRequest
): Promise<ChatResponse> {
  const response = await axios.post<ChatResponse>(
    `${API_BASE_URL}/chat`,
    payload
  );

  return response.data;
}