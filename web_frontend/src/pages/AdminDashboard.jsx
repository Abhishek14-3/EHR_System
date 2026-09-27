import React, { useState, useEffect } from "react";
import { api } from "../services/api";
import { Server, Users, FileText, Activity, ShieldAlert, CheckCircle2, RefreshCw } from "lucide-react";

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [containers, setContainers] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchAdminData = async () => {
    setLoading(true);
    try {
      const [sData, uData, cData] = await Promise.all([
        api.getAdminStats().catch(() => null),
        api.getAdminUsers().catch(() => []),
        api.getDockerStatus().catch(() => ({ containers: [] }))
      ]);
      setStats(sData);
      setUsers(uData || []);
      setContainers(cData?.containers || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAdminData();
  }, []);

  return (
    <div className="container" style={{ padding: "2.5rem 1.5rem" }}>
      <div style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        flexWrap: "wrap",
        gap: "1.5rem",
        marginBottom: "2.5rem"
      }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.4rem" }}>
            <span className="pulse-dot" style={{ background: "var(--triage-audit)" }}></span>
            <span style={{ fontSize: "0.82rem", fontWeight: 700, color: "var(--triage-audit)", textTransform: "uppercase", letterSpacing: "0.08em" }}>
              Network Governance Console
            </span>
          </div>
          <h1 style={{ fontSize: "2.2rem", fontWeight: 800, letterSpacing: "-0.03em" }}>
            Hyperledger Fabric Network Status
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.95rem" }}>
            Decentralized node telemetry, cryptographic user identities, and peer container health.
          </p>
        </div>

        <button onClick={fetchAdminData} className="btn btn-secondary">
          <RefreshCw size={16} />
          <span>Refresh Telemetry</span>
        </button>
      </div>

      {/* Stats Cards */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
        gap: "1.25rem",
        marginBottom: "2.5rem"
      }}>
        <div className="glass-card" style={{ padding: "1.4rem" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.75rem" }}>
            <span style={{ fontSize: "0.78rem", fontWeight: 700, textTransform: "uppercase", color: "var(--text-muted)" }}>Total Patients</span>
            <Users size={18} color="var(--accent)" />
          </div>
          <div style={{ fontSize: "2rem", fontWeight: 800 }}>{stats?.patients ?? "-"}</div>
        </div>

        <div className="glass-card" style={{ padding: "1.4rem" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.75rem" }}>
            <span style={{ fontSize: "0.78rem", fontWeight: 700, textTransform: "uppercase", color: "var(--text-muted)" }}>Certified Physicians</span>
            <Activity size={18} color="var(--tech)" />
          </div>
          <div style={{ fontSize: "2rem", fontWeight: 800 }}>{stats?.doctors ?? "-"}</div>
        </div>

        <div className="glass-card" style={{ padding: "1.4rem" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.75rem" }}>
            <span style={{ fontSize: "0.78rem", fontWeight: 700, textTransform: "uppercase", color: "var(--text-muted)" }}>Ledger Blocks</span>
            <FileText size={18} color="var(--triage-low)" />
          </div>
          <div style={{ fontSize: "2rem", fontWeight: 800 }}>{stats?.records ?? "-"}</div>
        </div>
      </div>

      {/* Grid: Containers & Registered Identities */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2rem" }} className="admin-grid">
        {/* Docker Peer Health */}
        <div className="glass-card" style={{ padding: "1.75rem" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "1.25rem" }}>
            <Server size={18} color="var(--accent)" />
            <h3 style={{ fontSize: "1.15rem", fontWeight: 700 }}>Fabric & IPFS Containers</h3>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem", maxHeight: "400px", overflowY: "auto" }}>
            {containers.length === 0 ? (
              <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>No active local docker containers detected.</p>
            ) : (
              containers.map((c, idx) => (
                <div key={idx} style={{
                  padding: "0.85rem 1rem",
                  background: "var(--surface-elevated)",
                  borderRadius: "10px",
                  border: "1px solid var(--border)",
                  fontSize: "0.85rem"
                }}>
                  <div style={{ fontWeight: 700, color: "var(--text-primary)" }}>{c.name}</div>
                  <div style={{ fontSize: "0.78rem", color: "var(--triage-low)", marginTop: "2px" }}>{c.status}</div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Registered User MSP Identities */}
        <div className="glass-card" style={{ padding: "1.75rem" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "1.25rem" }}>
            <Users size={18} color="var(--tech)" />
            <h3 style={{ fontSize: "1.15rem", fontWeight: 700 }}>Network User Identities</h3>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem", maxHeight: "400px", overflowY: "auto" }}>
            {users.map((u) => (
              <div key={u.id} style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "0.85rem 1rem",
                background: "var(--surface-elevated)",
                borderRadius: "10px",
                border: "1px solid var(--border)",
                fontSize: "0.85rem"
              }}>
                <div>
                  <span style={{ fontWeight: 700, color: "var(--text-primary)" }}>{u.username}</span>
                  <span style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginLeft: "8px" }}>ID #{u.id}</span>
                </div>
                <span className={`triage-badge ${u.role === "doctor" ? "triage-badge-mod" : u.role === "admin" ? "triage-badge-audit" : "triage-badge-low"}`}>
                  {u.role}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <style>{`
        @media (max-width: 900px) {
          .admin-grid {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
}
