import { useEffect, useRef } from "react";

declare global {
  interface Window {
    google?: any;
  }
}

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || "";

export default function GoogleButton({ onCredential }: { onCredential: (credential: string) => void }) {
  const buttonRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!GOOGLE_CLIENT_ID || !window.google || !buttonRef.current) return;

    window.google.accounts.id.initialize({
      client_id: GOOGLE_CLIENT_ID,
      callback: (response: { credential: string }) => onCredential(response.credential),
    });

    window.google.accounts.id.renderButton(buttonRef.current, {
      theme: "outline",
      size: "large",
      width: 336,
      text: "continue_with",
    });
  }, [onCredential]);

  if (!GOOGLE_CLIENT_ID) {
    return (
      <div style={{ fontSize: 12, color: "var(--muted)", textAlign: "center", padding: "8px 0" }}>
        Google Sign-In not configured (set VITE_GOOGLE_CLIENT_ID)
      </div>
    );
  }

  return <div ref={buttonRef} />;
}