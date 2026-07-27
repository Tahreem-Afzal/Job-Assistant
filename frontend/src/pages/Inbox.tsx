import { useEffect, useState } from "react";
import {
  GmailMessage,
  getGmailStatus,
  getGmailConnectUrl,
  listGmailMessages,
  draftGmailReply,
  disconnectGmail,
} from "../api/client";

const CATEGORY_LABELS: Record<string, string> = {
  recruiter_response: "Recruiter response",
  interview_invite: "Interview invite",
  scholarship_decision: "Scholarship decision",
  other: "Other",
};

export default function Inbox() {
  const [connected, setConnected] = useState<boolean | null>(null);
  const [emailAddress, setEmailAddress] = useState<string | undefined>();
  const [messages, setMessages] = useState<GmailMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [drafts, setDrafts] = useState<Record<string, string>>({});
  const [draftingId, setDraftingId] = useState<string | null>(null);
  const [error, setError] = useState("");

  async function loadStatus() {
    const res = await getGmailStatus();
    setConnected(res.data.connected);
    setEmailAddress(res.data.email_address);
    if (res.data.connected) loadMessages();
  }

  async function loadMessages() {
    setLoading(true);
    setError("");
    try {
      const res = await listGmailMessages();
      setMessages(res.data);
    } catch {
      setError("Couldn't load messages - try reconnecting Gmail.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadStatus();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleConnect() {
    try {
      const res = await getGmailConnectUrl();
      window.location.href = res.data.auth_url;
    } catch {
      setError("Gmail integration isn't configured on the server yet.");
    }
  }

  async function handleDisconnect() {
    await disconnectGmail();
    setConnected(false);
    setMessages([]);
  }

  async function handleDraft(messageId: string) {
    setDraftingId(messageId);
    try {
      const res = await draftGmailReply({ message_id: messageId });
      setDrafts((prev) => ({ ...prev, [messageId]: res.data.draft_reply }));
    } finally {
      setDraftingId(null);
    }
  }

  if (connected === null) return <div className="empty-state">Loading...</div>;

  return (
    <div>
      <div className="page-header">
        <h1>Inbox</h1>
        <p>
          Read-only - this app never sends email for you. Drafts are generated for you to copy and
          send yourself.
        </p>
      </div>

      {!connected && (
        <div className="empty-state">
          <p style={{ marginBottom: 16 }}>Connect Gmail to see recruiter replies and interview invites in one place.</p>
          <button className="btn btn-primary" onClick={handleConnect}>
            Connect Gmail
          </button>
        </div>
      )}

      {connected && (
        <>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
            <span style={{ color: "var(--muted)", fontSize: 14 }}>
              Connected as {emailAddress || "your Gmail account"}
            </span>
            <button className="btn btn-ghost btn-sm" onClick={handleDisconnect}>
              Disconnect
            </button>
          </div>

          {error && <div className="error-text">{error}</div>}
          {loading && <div className="empty-state">Loading messages...</div>}

          {!loading && messages.length === 0 && !error && (
            <div className="empty-state">No recent messages found in your inbox.</div>
          )}

          <div className="job-list">
            {messages.map((m) => (
              <div className="job-card" key={m.id}>
                <div className="job-main">
                  <span className="job-source">{CATEGORY_LABELS[m.category] || m.category}</span>
                  <h3>{m.subject}</h3>
                  <div className="job-meta">
                    {m.sender}
                    {m.received_at ? ` · ${m.received_at}` : ""}
                  </div>
                  <div className="job-desc">{m.snippet}</div>
                  <div className="job-actions">
                    <button
                      className="btn btn-ghost btn-sm"
                      onClick={() => handleDraft(m.id)}
                      disabled={draftingId === m.id}
                    >
                      {draftingId === m.id ? "Drafting..." : "Draft a reply"}
                    </button>
                  </div>
                  {drafts[m.id] && <div className="letter-output">{drafts[m.id]}</div>}
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}