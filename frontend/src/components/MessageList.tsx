import { useEffect, useRef } from "react";
import type { ChatMessage } from "../types/chat";

interface MessageListProps {
  messages: ChatMessage[];
  isLoading: boolean;
}

function MessageList({ messages, isLoading }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <section className="messages-container">
      {messages.map((message) => (
        <div
          key={message.id}
          className={`message-row ${
            message.role === "user" ? "user-row" : "assistant-row"
          }`}
        >
          <div className={`avatar ${message.role}`}>
            {message.role === "user" ? "U" : "AI"}
          </div>

          <div className={`message-bubble ${message.role}`}>
            {message.content}
          </div>
        </div>
      ))}

      {isLoading && (
        <div className="message-row assistant-row">
          <div className="avatar assistant">AI</div>
          <div className="message-bubble assistant typing">Thinking...</div>
        </div>
      )}

      <div ref={bottomRef} />
    </section>
  );
}

export default MessageList;