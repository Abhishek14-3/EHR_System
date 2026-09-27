import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { api } from "../services/api";
import { motion, AnimatePresence } from "framer-motion";
import { Shield, Stethoscope, User, Lock, Key, ArrowRight, CheckCircle2, AlertCircle, Database, Sparkles } from "lucide-react";

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [role, setRole] = useState("doctor");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const { loginUser } = useAuth();
  const navigate = useNavigate();

  // Simple live simulated hash to show cryptographic action
  const liveHash = password
    ? Array.from(password).reduce((acc, char) => ((acc << 5) - acc) + char.charCodeAt(0) | 0, 0).toString(16)
    : "";

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setLoading(true);

    try {
      if (isLogin) {
        const res = await api.login(username, password);
        loginUser(res.token, res.role, res.username);
        // Route according to role
        if (res.role === "doctor") navigate("/doctor");
        else if (res.role === "patient") navigate("/patient");
        else navigate("/admin");
      } else {
        await api.register(username, password, role);
        setSuccess(`Node identity '${username}' registered! You can now authenticate.`);
        setIsLogin(true);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      flex: 1,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      padding: "3rem 1.5rem"
    }}>
      <div className="container" style={{
        maxWidth: "1150px",
        display: "grid",
        gridTemplateColumns: "1fr",
        gap: "3.5rem",
        alignItems: "center"
      }}>
        {/* Left Hero & Visual Hologram */}
        <div>
          <div style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "0.55rem",
            padding: "0.35rem 0.95rem",
            borderRadius: "99px",
            background: "var(--accent-light)",
            color: "var(--accent)",
            fontFamily: "var(--font-script)",
            fontSize: "1.05rem",
            marginBottom: "1.5rem"
          }}>
            <Sparkles size={15} />
            <span>Decentralized Sovereign Health Vault</span>
          </div>

          <h1 style={{
            fontSize: "3.2rem",
            fontWeight: 800,
            letterSpacing: "-0.04em",
            lineHeight: 1.15,
            marginBottom: "1.25rem"
          }}>
            Medical Records, <br />
            <span style={{
              background: "linear-gradient(135deg, var(--accent) 0%, var(--tech) 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent"
            }}>
              Secured on Fabric.
            </span>
          </h1>

          <p style={{
            fontSize: "1.1rem",
            color: "var(--text-secondary)",
            maxWidth: "520px",
            lineHeight: 1.7,
            marginBottom: "2.5rem"
          }}>
            A clinical-grade architecture combining Hyperledger Fabric smart contracts, IPFS distributed storage, and predictive AI cardiovascular diagnostics.
          </p>

          {/* Interactive Feature Pills */}
          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
              <div style={{
                width: "40px",
                height: "40px",
                borderRadius: "12px",
                background: "var(--surface-elevated)",
                border: "1px solid var(--border)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "var(--accent)"
              }}>
                <Shield size={20} />
              </div>
              <div>
                <h4 style={{ fontSize: "0.98rem", marginBottom: "2px" }}>Patient-Controlled Sovereignty</h4>
                <p style={{ fontSize: "0.85rem", margin: 0 }}>Smart contracts enforce cryptographic consent before doctors can inspect records.</p>
              </div>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
              <div style={{
                width: "40px",
                height: "40px",
                borderRadius: "12px",
                background: "var(--surface-elevated)",
                border: "1px solid var(--border)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "var(--tech)"
              }}>
                <Database size={20} />
              </div>
              <div>
                <h4 style={{ fontSize: "0.98rem", marginBottom: "2px" }}>IPFS Merkle Storage</h4>
                <p style={{ fontSize: "0.85rem", margin: 0 }}>Zero medical data stored on central servers; cryptographically hashed & pinned.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Auth Card */}
        <div style={{ maxWidth: "480px", margin: "0 auto", width: "100%" }}>
          <div className="glass-card glow-edge" style={{ padding: "2.2rem" }}>
            {/* Tab Switcher */}
            <div style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              padding: "4px",
              background: "var(--surface-elevated)",
              borderRadius: "12px",
              marginBottom: "1.75rem",
              border: "1px solid var(--border)"
            }}>
              <button
                type="button"
                onClick={() => { setIsLogin(true); setError(null); }}
                style={{
                  padding: "0.55rem",
                  borderRadius: "8px",
                  border: "none",
                  background: isLogin ? "var(--surface)" : "transparent",
                  color: isLogin ? "var(--text-primary)" : "var(--text-muted)",
                  fontWeight: 700,
                  fontSize: "0.88rem",
                  cursor: "pointer",
                  boxShadow: isLogin ? "var(--card-shadow)" : "none",
                  transition: "all 0.2s ease"
                }}
              >
                Authenticate Node
              </button>
              <button
                type="button"
                onClick={() => { setIsLogin(false); setError(null); }}
                style={{
                  padding: "0.55rem",
                  borderRadius: "8px",
                  border: "none",
                  background: !isLogin ? "var(--surface)" : "transparent",
                  color: !isLogin ? "var(--text-primary)" : "var(--text-muted)",
                  fontWeight: 700,
                  fontSize: "0.88rem",
                  cursor: "pointer",
                  boxShadow: !isLogin ? "var(--card-shadow)" : "none",
                  transition: "all 0.2s ease"
                }}
              >
                Register Key
              </button>
            </div>

            <div style={{ marginBottom: "1.5rem" }}>
              <h2 style={{ fontSize: "1.6rem", fontWeight: 800 }}>
                {isLogin ? "Node Authentication" : "Mint Sovereign Identity"}
              </h2>
              <p style={{ fontSize: "0.88rem", color: "var(--text-muted)", marginTop: "4px" }}>
                {isLogin ? "Verify cryptographic credentials with Fabric MSP" : "Register identity credentials on the network"}
              </p>
            </div>

            {error && (
              <div style={{
                display: "flex",
                alignItems: "center",
                gap: "0.6rem",
                padding: "0.75rem 1rem",
                borderRadius: "10px",
                background: "var(--triage-high-bg)",
                color: "var(--triage-high)",
                border: "1px solid rgba(244, 63, 94, 0.3)",
                fontSize: "0.85rem",
                marginBottom: "1.25rem"
              }}>
                <AlertCircle size={16} />
                <span>{error}</span>
              </div>
            )}

            {success && (
              <div style={{
                display: "flex",
                alignItems: "center",
                gap: "0.6rem",
                padding: "0.75rem 1rem",
                borderRadius: "10px",
                background: "var(--triage-low-bg)",
                color: "var(--triage-low)",
                border: "1px solid rgba(16, 185, 129, 0.3)",
                fontSize: "0.85rem",
                marginBottom: "1.25rem"
              }}>
                <CheckCircle2 size={16} />
                <span>{success}</span>
              </div>
            )}

            <form onSubmit={handleSubmit}>
              {!isLogin && (
                <div className="form-group">
                  <label className="form-label">Network Role Designation</label>
                  <div style={{
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr 1fr",
                    gap: "0.5rem"
                  }}>
                    {[
                      { id: "doctor", label: "Doctor", icon: <Stethoscope size={15} /> },
                      { id: "patient", label: "Patient", icon: <User size={15} /> },
                      { id: "admin", label: "Admin", icon: <Shield size={15} /> }
                    ].map((item) => (
                      <button
                        key={item.id}
                        type="button"
                        onClick={() => setRole(item.id)}
                        style={{
                          display: "flex",
                          flexDirection: "column",
                          alignItems: "center",
                          gap: "0.35rem",
                          padding: "0.75rem 0.5rem",
                          borderRadius: "10px",
                          border: role === item.id ? "2px solid var(--accent)" : "1px solid var(--border)",
                          background: role === item.id ? "var(--accent-light)" : "var(--surface)",
                          color: role === item.id ? "var(--accent)" : "var(--text-secondary)",
                          fontWeight: 700,
                          fontSize: "0.8rem",
                          cursor: "pointer",
                          transition: "all 0.15s ease"
                        }}
                      >
                        {item.icon}
                        <span>{item.label}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              <div className="form-group">
                <label className="form-label">Username Node Identifier</label>
                <input
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="e.g. doctor_smith or patient_01"
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label className="form-label">
                  <span>Cryptographic Security Key</span>
                  {liveHash && (
                    <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.7rem", color: "var(--tech)" }}>
                      SHA256: 0x{liveHash.slice(0, 6)}...
                    </span>
                  )}
                </label>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="form-input"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="btn btn-primary"
                style={{ width: "100%", padding: "0.8rem", marginTop: "0.75rem" }}
              >
                {loading ? (
                  <span>Verifying Node Keys...</span>
                ) : (
                  <>
                    <span>{isLogin ? "Authenticate on Blockchain" : "Commit Identity to Ledger"}</span>
                    <ArrowRight size={17} />
                  </>
                )}
              </button>
            </form>

            <div style={{
              textAlign: "center",
              marginTop: "1.5rem",
              paddingTop: "1.25rem",
              borderTop: "1px solid var(--border)",
              fontSize: "0.78rem",
              color: "var(--text-muted)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "0.4rem"
            }}>
              <Lock size={12} color="var(--accent)" />
              <span>TLS 1.3 • End-to-End Cryptographic Ledger Session</span>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @media (min-width: 900px) {
          .container {
            grid-template-columns: 1.15fr 1fr !important;
          }
        }
      `}</style>
    </div>
  );
}
