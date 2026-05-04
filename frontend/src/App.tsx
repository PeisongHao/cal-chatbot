import { useState } from "react";

import { sendChatMessage } from "./api/chatApi";
import Sidebar from "./components/Siderbar";
import ChatHeader from "./components/ChatHeader";
import MessageList from "./components/MessageList";
import ChatInput from "./components/ChatInput";
import type { ChatMessage } from "./types/chat";

import "./App.css";

function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: crypto.randomUUID(),
      role: "assistant",
      content:
        "Hi! I can help you book a meeting or list your scheduled meetings. How can I help?",
    },
  ]);

  const [sessionId, setSessionId] = useState<string | null>(() => {
    return localStorage.getItem("cal_chatbot_session_id");
  });

  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async (message: string) => {
    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: message,
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await sendChatMessage({
        message,
        session_id: sessionId,
      });

      if (response.session_id && response.session_id !== sessionId) {
        setSessionId(response.session_id);
        localStorage.setItem("cal_chatbot_session_id", response.session_id);
      }

      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: response.reply,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch {
      const errorMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content:
          "Sorry, something went wrong while connecting to the backend. Please check if the FastAPI server is running.",
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    localStorage.removeItem("cal_chatbot_session_id");
    setSessionId(null);
    setMessages([
      {
        id: crypto.randomUUID(),
        role: "assistant",
        content:
          "New chat started. I can help you book a meeting or list scheduled meetings.",
      },
    ]);
  };

  return (
    <div className="app-shell">
      <Sidebar sessionId={sessionId} onNewChat={handleNewChat} />

      <main className="chat-main">
        <ChatHeader />
        <MessageList messages={messages} isLoading={isLoading} />
        <ChatInput isLoading={isLoading} onSendMessage={handleSendMessage} />
      </main>
    </div>
  );
}

export default App;