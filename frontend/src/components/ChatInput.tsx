import { useState } from "react";

interface ChatInputProps {
  isLoading: boolean;
  onSendMessage: (message: string) => void;
}

function ChatInput({ isLoading, onSendMessage }: ChatInputProps) {
  const [input, setInput] = useState("");

  const handleSend = () => {
    const trimmedInput = input.trim();

    if (!trimmedInput || isLoading) {
      return;
    }

    onSendMessage(trimmedInput);
    setInput("");
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  return (
    <footer className="input-area">
      <textarea
        value={input}
        onChange={(event) => setInput(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Message Cal AI..."
        rows={1}
      />

      <button onClick={handleSend} disabled={!input.trim() || isLoading}>
        Send
      </button>
    </footer>
  );
}

export default ChatInput;