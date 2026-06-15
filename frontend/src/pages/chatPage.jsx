import { useState, useRef, useEffect } from "react";
import { sendMessage, getMemory } from "../services/api";
import MemoryPanel from "../components/MemoryPanel";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function formatTime(iso) {
  return new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function TypingIndicator() {
  return (
    <div style={styles.botBubble}>
      <span style={styles.typingDots}>
        <span>●</span><span>●</span><span>●</span>
      </span>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main ChatPage component
// ---------------------------------------------------------------------------
export default function ChatPage() {
  const [userId]          = useState(1); // In production, pull from auth context
  const [messages, setMessages] = useState([
    {
      id: 0,
      role: "bot",
      text: "👋 Hi! I'm your MemoryCart AI assistant. Ask me about your orders, refunds, or store policies.",
      time: new Date().toISOString(),
    },
  ]);
  const [input, setInput]     = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);
  const [memories, setMemories] = useState([]);
  const bottomRef             = useRef(null);

  // Auto-scroll on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Load memories on mount
  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        const payload = await getMemory(userId);
        if (!mounted) return;
        // payload is unified {response,data,status}
        const mems = payload && payload.data ? payload.data : [];
        setMemories(mems);
      } catch (e) {
        // ignore — memory panel is optional
      }
    }
    load();
    return () => { mounted = false; };
  }, [userId]);

  // ---------------------------------------------------------------------------
  // Send message
  // ---------------------------------------------------------------------------
  async function handleSend(e) {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || loading) return;

    const userMsg = { id: Date.now(), role: "user", text: trimmed, time: new Date().toISOString() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    setError(null);

    try {
      const data = await sendMessage(userId, trimmed);
      const botText = data && data.response ? data.response : "Sorry, I couldn't generate a response.";
      const botMsg = {
        id: Date.now() + 1,
        role: "bot",
        text: botText,
        time: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, botMsg]);

      // Refresh memories after successful response
      try {
        const memPayload = await getMemory(userId);
        const mems = memPayload && memPayload.data ? memPayload.data : [];
        setMemories(mems);
      } catch (e) {
        // ignore memory fetch errors
      }
    } catch (err) {
      setError(err.message || "Failed to reach the server.");
      const errMsg = {
        id: Date.now() + 1,
        role: "bot",
        text: "⚠️ Sorry, I encountered an error. Please try again.",
        time: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setLoading(false);
    }
  }

  // Enter key sends, Shift+Enter adds newline
  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      handleSend(e);
    }
  }

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------
  return (
    <div style={styles.page}>
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.headerLeft}>
          <span style={styles.logo}>🛒</span>
          <div>
            <h1 style={styles.headerTitle}>MemoryCart AI</h1>
            <p style={styles.headerSub}>Powered by Groq · Hindsight · ChromaDB</p>
          </div>
        </div>
        <span style={styles.statusDot} title="Online" />
      </header>

      <div style={styles.contentArea}>
        {/* Message list */}
        <main style={styles.messageArea}>
        {messages.map((msg) => (
          <div key={msg.id} style={msg.role === "user" ? styles.userRow : styles.botRow}>
            {msg.role === "bot" && <span style={styles.avatar}>🤖</span>}
            <div style={{ maxWidth: "75%" }}>
              <div style={msg.role === "user" ? styles.userBubble : styles.botBubble}>
                {msg.text}
              </div>
              <div style={styles.timestamp}>{formatTime(msg.time)}</div>
            </div>
            {msg.role === "user" && <span style={styles.avatar}>👤</span>}
          </div>
        ))}

        {loading && (
          <div style={styles.botRow}>
            <span style={styles.avatar}>🤖</span>
            <TypingIndicator />
          </div>
        )}

        {error && <div style={styles.errorBanner}>⚠️ {error}</div>}

          <div ref={bottomRef} />
        </main>

        {/* Right-hand Memory Panel */}
        <MemoryPanel memories={memories} />
      </div>

      {/* Input bar */}
      <form onSubmit={handleSend} style={styles.inputBar}>
        <textarea
          id="chat-input"
          style={styles.textarea}
          rows={1}
          placeholder="Ask about orders, refunds, or shipping policy…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
        />
        <button
          id="chat-send-btn"
          type="submit"
          style={loading ? { ...styles.sendBtn, opacity: 0.6 } : styles.sendBtn}
          disabled={loading}
        >
          {loading ? "…" : "Send"}
        </button>
      </form>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Inline styles (no build-tool dependency — works in any React setup)
// ---------------------------------------------------------------------------
const styles = {
  page: {
    display: "flex",
    flexDirection: "column",
    height: "100vh",
    background: "linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%)",
    fontFamily: "'Segoe UI', system-ui, -apple-system, sans-serif",
    color: "#e2e8f0",
  },
  header: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "14px 24px",
    background: "rgba(255,255,255,0.04)",
    backdropFilter: "blur(12px)",
    borderBottom: "1px solid rgba(255,255,255,0.08)",
    flexShrink: 0,
  },
  headerLeft: { display: "flex", alignItems: "center", gap: 12 },
  logo: { fontSize: 32 },
  headerTitle: { margin: 0, fontSize: 20, fontWeight: 700, color: "#a78bfa" },
  headerSub: { margin: 0, fontSize: 12, color: "#94a3b8" },
  statusDot: {
    width: 10, height: 10, borderRadius: "50%",
    background: "#4ade80", boxShadow: "0 0 8px #4ade80",
  },
  messageArea: {
    flex: 1,
    overflowY: "auto",
    padding: "20px 16px",
    display: "flex",
    flexDirection: "column",
    gap: 12,
  },
  contentArea: {
    flex: 1,
    display: 'flex',
    alignItems: 'stretch',
    gap: 8,
    minHeight: 0,
  },
  userRow: { display: "flex", alignItems: "flex-end", justifyContent: "flex-end", gap: 8 },
  botRow:  { display: "flex", alignItems: "flex-end", justifyContent: "flex-start", gap: 8 },
  avatar: { fontSize: 22, flexShrink: 0 },
  userBubble: {
    background: "linear-gradient(135deg, #7c3aed, #4f46e5)",
    color: "#fff",
    padding: "10px 14px",
    borderRadius: "18px 18px 4px 18px",
    fontSize: 14,
    lineHeight: 1.5,
    whiteSpace: "pre-wrap",
    wordBreak: "break-word",
  },
  botBubble: {
    background: "rgba(255,255,255,0.06)",
    border: "1px solid rgba(255,255,255,0.1)",
    color: "#e2e8f0",
    padding: "10px 14px",
    borderRadius: "18px 18px 18px 4px",
    fontSize: 14,
    lineHeight: 1.5,
    whiteSpace: "pre-wrap",
    wordBreak: "break-word",
  },
  timestamp: { fontSize: 10, color: "#64748b", marginTop: 4, paddingLeft: 4 },
  typingDots: {
    display: "flex", gap: 4,
    "& span": { animation: "blink 1.2s infinite", animationDelay: "var(--d)" },
  },
  errorBanner: {
    background: "rgba(239,68,68,0.15)",
    border: "1px solid rgba(239,68,68,0.3)",
    borderRadius: 8,
    padding: "8px 14px",
    fontSize: 13,
    color: "#fca5a5",
    textAlign: "center",
  },
  inputBar: {
    display: "flex",
    gap: 8,
    padding: "12px 16px",
    background: "rgba(255,255,255,0.04)",
    borderTop: "1px solid rgba(255,255,255,0.08)",
    flexShrink: 0,
  },
  textarea: {
    flex: 1,
    resize: "none",
    background: "rgba(255,255,255,0.07)",
    border: "1px solid rgba(255,255,255,0.12)",
    borderRadius: 12,
    color: "#e2e8f0",
    fontSize: 14,
    padding: "10px 14px",
    outline: "none",
    fontFamily: "inherit",
    lineHeight: 1.5,
  },
  sendBtn: {
    background: "linear-gradient(135deg, #7c3aed, #4f46e5)",
    color: "#fff",
    border: "none",
    borderRadius: 12,
    padding: "10px 22px",
    fontWeight: 600,
    fontSize: 14,
    cursor: "pointer",
    transition: "opacity 0.2s",
  },
};
