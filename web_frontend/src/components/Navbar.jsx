import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Activity, ShieldCheck, Sun, Moon, LogOut, User, Server } from "lucide-react";

export default function Navbar() {
  const { user, theme, toggleTheme, logoutUser } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logoutUser();
    navigate("/login");
  };

  return (
    <header style={{
      position: "sticky",
      top: 0,
      zIndex: 100,
      backdropFilter: "blur(20px)",
      WebkitBackdropFilter: "blur(20px)",
      background: "var(--surface-glass)",
      borderBottom: "1px solid var(--border)"
    }}>
      <div className="container" style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        height: "70px"
      }}>
        {/* Logo & Network Status */}
        <div style={{ display: "flex", alignItems: "center", gap: "1.75rem" }}>
          <Link to="/" style={{ display: "flex", alignItems: "center", gap: "0.6rem", textDecoration: "none" }}>
            <div style={{
              width: "36px",
              height: "36px",
              borderRadius: "10px",
              background: "linear-gradient(135deg, var(--accent) 0%, var(--tech) 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#FFFFFF",
              boxShadow: "0 4px 14px var(--accent-glow)"
            }}>
              <Activity size={20} strokeWidth={2.4} />
            </div>
            <div>
              <span style={{
                fontSize: "1.15rem",
                fontWeight: 800,
                color: "var(--text-primary)",
                letterSpacing: "-0.03em"
              }}>
                HealthChain<span style={{ color: "var(--accent)" }}>AI</span>
              </span>
            </div>
          </Link>

          {/* Hyperledger Fabric Network Ticker Badge */}
          <div style={{
            display: "none",
            alignItems: "center",
            gap: "0.5rem",
            padding: "0.3rem 0.85rem",
            borderRadius: "99px",
            background: "var(--surface-elevated)",
            border: "1px solid var(--border)",
            fontSize: "0.75rem",
            fontWeight: 600,
            color: "var(--text-secondary)"
          }} className="network-status-badge">
            <span className="pulse-dot" style={{ background: "var(--triage-low)" }}></span>
            <span>Hyperledger Fabric Org1MSP</span>
            <span style={{ color: "var(--text-muted)" }}>•</span>
            <span style={{ color: "var(--tech)", fontFamily: "var(--font-mono)" }}>Block #1,442</span>
          </div>
        </div>

        {/* Right Actions */}
        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            className="btn btn-secondary"
            style={{ padding: "0.5rem 0.8rem", borderRadius: "10px" }}
            title={theme === "dark" ? "Switch to Light Mode" : "Switch to Dark Mode"}
          >
            {theme === "dark" ? <Sun size={17} color="#FBBF24" /> : <Moon size={17} color="#6366F1" />}
          </button>

          {user ? (
            <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
              {/* Role Chip */}
              <div style={{
                display: "flex",
                alignItems: "center",
                gap: "0.5rem",
                padding: "0.4rem 0.85rem",
                borderRadius: "10px",
                background: "var(--surface-elevated)",
                border: "1px solid var(--border)",
                fontSize: "0.82rem",
                fontWeight: 600,
                color: "var(--text-primary)"
              }}>
                <ShieldCheck size={16} color="var(--accent)" />
                <span style={{ textTransform: "capitalize" }}>{user.role}</span>
                <span style={{ color: "var(--text-muted)" }}>|</span>
                <span style={{ color: "var(--text-secondary)" }}>{user.username}</span>
              </div>

              {/* Logout Button */}
              <button
                onClick={handleLogout}
                className="btn btn-ghost"
                style={{ padding: "0.5rem 0.75rem", color: "var(--triage-high)" }}
                title="Disconnect Node Session"
              >
                <LogOut size={17} />
              </button>
            </div>
          ) : (
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <Link to="/login" className="btn btn-primary" style={{ padding: "0.5rem 1.15rem" }}>
                Connect Node
              </Link>
            </div>
          )}
        </div>
      </div>
      <style>{`
        @media (min-width: 768px) {
          .network-status-badge {
            display: flex !important;
          }
        }
      `}</style>
    </header>
  );
}
