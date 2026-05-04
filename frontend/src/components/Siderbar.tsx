interface SidebarProps {
  sessionId: string | null;
  onNewChat: () => void;
}

function Sidebar({ sessionId, onNewChat }: SidebarProps) {
  return (
    <aside className="sidebar">
      <div>
        <h1>Cal AI</h1>
        <p>Scheduling assistant</p>

        <button className="new-chat-button" onClick={onNewChat}>
          + New Chat
        </button>
      </div>

      <div className="sidebar-footer">
        <span>Session</span>
        <small>{sessionId || "Not created yet"}</small>
      </div>
    </aside>
  );
}

export default Sidebar;