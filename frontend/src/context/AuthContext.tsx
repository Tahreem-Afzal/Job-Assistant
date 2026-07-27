import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { User, getMe, loginUser, registerUser, loginWithGoogle } from "../api/client";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  loginGoogle: (credential: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      setLoading(false);
      return;
    }
    getMe()
      .then((res) => setUser(res.data))
      .catch(() => localStorage.removeItem("token"))
      .finally(() => setLoading(false));
  }, []);

  async function login(email: string, password: string) {
    const res = await loginUser({ email, password });
    localStorage.setItem("token", res.data.access_token);
    const me = await getMe();
    setUser(me.data);
  }

  async function register(email: string, password: string, fullName?: string) {
    await registerUser({ email, password, full_name: fullName });
    await login(email, password);
  }

  async function loginGoogle(credential: string) {
    const res = await loginWithGoogle(credential);
    localStorage.setItem("token", res.data.access_token);
    const me = await getMe();
    setUser(me.data);
  }

  function logout() {
    localStorage.removeItem("token");
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, loginGoogle, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}