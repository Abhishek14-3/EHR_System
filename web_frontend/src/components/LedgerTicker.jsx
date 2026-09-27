import React from "react";
import { Link2, Shield, Database, Cpu } from "lucide-react";

export default function LedgerTicker() {
  const tickerItems = [
    { icon: <Link2 size={13} color="var(--accent)" />, text: "Hyperledger Fabric: Channel 'ehrchannel' • Block #1,442 Committed" },
    { icon: <Database size={13} color="var(--tech)" />, text: "IPFS Swarm: 24 Distributed Medical Pinners Active" },
    { icon: <Cpu size={13} color="var(--triage-low)" />, text: "AI Diagnostic Engine: Random Forest + SHAP TreeExplainer v1.4 Loaded" },
    { icon: <Shield size={13} color="var(--triage-audit)" />, text: "RBAC Cryptographic Ledger: Zero Patient Data Leaks Detected" }
  ];

  return (
    <div style={{
      width: "100%",
      background: "var(--surface)",
      borderBottom: "1px solid var(--border)",
      overflow: "hidden",
      padding: "0.45rem 0",
      fontSize: "0.76rem",
      color: "var(--text-secondary)",
      whiteSpace: "nowrap"
    }}>
      <div style={{
        display: "inline-flex",
        gap: "3rem",
        animation: "scroll-ticker 40s linear infinite"
      }}>
        {[...tickerItems, ...tickerItems].map((item, idx) => (
          <div key={idx} style={{ display: "inline-flex", alignItems: "center", gap: "0.45rem" }}>
            {item.icon}
            <span style={{ fontFamily: "var(--font-mono)", fontWeight: 500 }}>{item.text}</span>
            <span style={{ color: "var(--text-muted)" }}>//</span>
          </div>
        ))}
      </div>
      <style>{`
        @keyframes scroll-ticker {
          0% { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }
      `}</style>
    </div>
  );
}
