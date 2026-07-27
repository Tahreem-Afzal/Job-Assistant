import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  if (!user) return null;

  return (
    <div className="navbar">
      <div className="brand">
        <span className="mark" />
        Pathfinder
      </div>
      <div className="nav-links">
        <NavLink to="/search" className={({ isActive }) => (isActive ? "active" : "")}>
          Search
        </NavLink>
        <NavLink to="/scholarships" className={({ isActive }) => (isActive ? "active" : "")}>
          Scholarships
        </NavLink>
        <NavLink to="/inbox" className={({ isActive }) => (isActive ? "active" : "")}>
          Inbox
        </NavLink>
        <NavLink to="/saved" className={({ isActive }) => (isActive ? "active" : "")}>
          Saved
        </NavLink>
        <NavLink to="/resume" className={({ isActive }) => (isActive ? "active" : "")}>
          Cover Letters
        </NavLink>
        <NavLink to="/profile" className={({ isActive }) => (isActive ? "active" : "")}>
          Profile
        </NavLink>
        <button
          className="btn btn-ghost btn-sm"
          onClick={() => {
            logout();
            navigate("/login");
          }}
        >
          Log out
        </button>
      </div>
    </div>
  );
}