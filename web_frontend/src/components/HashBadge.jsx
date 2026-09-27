import React, { useState } from "react";
import { Copy, Check } from "lucide-react";

export default function HashBadge({ hash, prefixLen = 8, suffixLen = 4, label = "" }) {
  const [copied, setCopied] = useState(false);

  if (!hash || String(hash).trim() === "" || hash === "None" || hash === "N/A") {
    return <span style={{ color: "var(--text-muted)", fontSize: "0.8rem", fontStyle: "italic" }}>Not Anchored</span>;
  }

  const clean = String(hash).trim();
  const display = clean.length > prefixLen + suffixLen + 3
    ? `${clean.substring(0, prefixLen)}...${clean.substring(clean.length - suffixLen)}`
    : clean;

  const copyToClipboard = (e) => {
    e.stopPropagation();
    navigator.clipboard.writeText(clean);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <span
      onClick={copyToClipboard}
      className="hash-badge"
      title={`Click to copy full hash: ${clean}`}
    >
      {label && <span style={{ color: "var(--text-muted)", fontWeight: 500 }}>{label}:</span>}
      <span>{display}</span>
      {copied ? <Check size={12} color="#10B981" /> : <Copy size={12} />}
    </span>
  );
}
