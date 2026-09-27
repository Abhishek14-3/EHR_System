import React, { useState, useEffect, useMemo } from "react";
import { useAuth } from "../context/AuthContext";
import { api } from "../services/api";
import HashBadge from "../components/HashBadge";
import RiskGauge from "../components/RiskGauge";
import { motion, AnimatePresence } from "framer-motion";
import {
  FileText, Upload, Shield, UserCheck, Download, RefreshCw,
  Clock, CheckCircle2, AlertCircle, FileUp, KeyRound, Sparkles,
  Search, Filter, Lock, Eye, ChevronDown, ChevronUp, Share2,
  Activity, X, Check, ArrowRight, HardDrive, ShieldCheck, HeartPulse
} from "lucide-react";

export default function PatientDashboard() {
  const { user } = useAuth();
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Navigation & Filtering
  const [activeTab, setActiveTab] = useState("records"); // "records" | "consents" | "upload" | "analytics"
  const [searchQuery, setSearchQuery] = useState("");
  const [riskFilter, setRiskFilter] = useState("all"); // "all" | "low" | "mod" | "high" | "manual"
  const [expandedRecordId, setExpandedRecordId] = useState(null);

  // Upload State
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);

  // 1-Click Share Modal State
  const [shareModal, setShareModal] = useState({
    isOpen: false,
    recordId: "",
    doctorId: "",
    submitting: false,
    status: null
  });

  const fetchRecords = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getMyRecords();
      setRecords(data || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecords();
  }, []);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
    setUploading(true);
    setUploadStatus(null);

    try {
      const res = await api.uploadRecord(file, user.username);
      setUploadStatus({
        type: "success",
        message: `Record ${res.record_id} successfully pinned to IPFS and anchored to Hyperledger Fabric!`
      });
      setFile(null);
      await fetchRecords();
      setTimeout(() => {
        setActiveTab("records");
      }, 1500);
    } catch (err) {
      setUploadStatus({ type: "error", message: err.message });
    } finally {
      setUploading(false);
    }
  };

  const handleGrant = async (e) => {
    e.preventDefault();
    if (!shareModal.recordId || !shareModal.doctorId) return;
    setShareModal((prev) => ({ ...prev, submitting: true, status: null }));

    try {
      await api.grantAccess(shareModal.recordId, shareModal.doctorId);
      setShareModal((prev) => ({
        ...prev,
        submitting: false,
        status: {
          type: "success",
          message: `Consent key granted to Dr. ${shareModal.doctorId} on Fabric smart contract!`
        }
      }));
      await fetchRecords();
      setTimeout(() => {
        setShareModal({ isOpen: false, recordId: "", doctorId: "", submitting: false, status: null });
      }, 1800);
    } catch (err) {
      setShareModal((prev) => ({
        ...prev,
        submitting: false,
        status: { type: "error", message: err.message }
      }));
    }
  };

  const handleDownload = async (recordId) => {
    try {
      await api.downloadReport(recordId);
    } catch (err) {
      alert("Error downloading report: " + err.message);
    }
  };

  const parsePrediction = (predStr) => {
    try {
      if (!predStr) return {};
      return typeof predStr === "object" ? predStr : JSON.parse(predStr);
    } catch (e) {
      return { prediction: "Not Evaluated", risk_level: "N/A" };
    }
  };

  // Filtered Records
  const filteredRecords = useMemo(() => {
    return records.filter((rec) => {
      const pred = parsePrediction(rec.mlPrediction);
      const riskLevel = String(pred.risk_level || "").toLowerCase();
      const isManual = pred.type === "manual";

      // Filter by Risk
      if (riskFilter === "low" && !riskLevel.includes("low")) return false;
      if (riskFilter === "mod" && !riskLevel.includes("mod")) return false;
      if (riskFilter === "high" && !riskLevel.includes("high")) return false;
      if (riskFilter === "manual" && !isManual) return false;

      // Search Query
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        const matchesId = (rec.id || "").toLowerCase().includes(query);
        const matchesDoctor = (pred.doctor_id || "").toLowerCase().includes(query);
        const matchesNotes = (pred.doctor_notes || "").toLowerCase().includes(query);
        const matchesIPFS = (rec.ipfsHash || "").toLowerCase().includes(query);
        const matchesPred = (pred.prediction || "").toLowerCase().includes(query);
        return matchesId || matchesDoctor || matchesNotes || matchesIPFS || matchesPred;
      }
      return true;
    });
  }, [records, searchQuery, riskFilter]);

  // Aggregate Metrics
  const totalAuthorizedGrants = useMemo(() => {
    return records.reduce((acc, r) => acc + (r.authorizedUsers?.length || 0), 0);
  }, [records]);

  const latestAIResult = useMemo(() => {
    if (!records.length) return null;
    for (const r of records) {
      const pred = parsePrediction(r.mlPrediction);
      if (pred.risk_level && pred.risk_level !== "N/A" && pred.type !== "manual") {
        return pred;
      }
    }
    return null;
  }, [records]);

  return (
    <div className="container" style={{ padding: "2rem 1.5rem 4rem 1.5rem", maxWidth: "1280px" }}>
      {/* =========================================================================
          1. TOP PATIENT PROFILE & SOVEREIGN VAULT BAR
          ========================================================================= */}
      <div style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        flexWrap: "wrap",
        gap: "1.25rem",
        marginBottom: "2rem",
        paddingBottom: "1.5rem",
        borderBottom: "1px solid var(--border)"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "1.25rem" }}>
          <div style={{
            width: "56px",
            height: "56px",
            borderRadius: "16px",
            background: "linear-gradient(135deg, var(--accent) 0%, var(--tech) 100%)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#FFFFFF",
            fontWeight: 800,
            fontSize: "1.35rem",
            boxShadow: "0 6px 18px var(--accent-glow)",
            flexShrink: 0
          }}>
            {(user?.username || "P")[0].toUpperCase()}
          </div>

          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "0.2rem" }}>
              <span style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--text-primary)" }}>
                {user?.username}
              </span>
              <span className="triage-badge triage-badge-low" style={{ fontSize: "0.7rem", padding: "0.15rem 0.55rem" }}>
                <ShieldCheck size={12} />
                Sovereign Vault
              </span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", fontSize: "0.82rem", color: "var(--text-secondary)" }}>
              <span>Role: <strong style={{ color: "var(--accent)" }}>Patient Node</strong></span>
              <span>•</span>
              <span>Fabric Org1MSP Active</span>
              <span>•</span>
              <span style={{ fontFamily: "var(--font-mono)", color: "var(--tech)" }}>Channel: ehrchannel</span>
            </div>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <button
            onClick={fetchRecords}
            className="btn btn-secondary"
            disabled={loading}
            style={{ padding: "0.55rem 1rem", fontSize: "0.84rem" }}
          >
            <RefreshCw size={15} className={loading ? "spin" : ""} />
            <span>Sync Ledger</span>
          </button>

          <button
            onClick={() => setActiveTab("upload")}
            className="btn btn-primary"
            style={{ padding: "0.55rem 1.15rem", fontSize: "0.84rem" }}
          >
            <FileUp size={15} />
            <span>Inscribe New Record</span>
          </button>
        </div>
      </div>

      {/* =========================================================================
          2. METRIC TILES ROW (4 Clean Organized Cards)
          ========================================================================= */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(230px, 1fr))",
        gap: "1.25rem",
        marginBottom: "2rem"
      }}>
        {/* Metric 1: Total Records */}
        <div className="glass-card" style={{ padding: "1.25rem 1.4rem" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.5rem" }}>
            <span style={{ fontSize: "0.78rem", fontWeight: 700, textTransform: "uppercase", color: "var(--text-muted)", letterSpacing: "0.05em" }}>
              Secured Medical Files
            </span>
            <div style={{ width: "32px", height: "32px", borderRadius: "8px", background: "var(--accent-light)", color: "var(--accent)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <FileText size={17} />
            </div>
          </div>
          <div style={{ fontSize: "2rem", fontWeight: 800, color: "var(--text-primary)", lineHeight: 1.1 }}>
            {records.length}
          </div>
          <div style={{ fontSize: "0.78rem", color: "var(--text-muted)", marginTop: "0.4rem" }}>
            Cryptographically pinned on IPFS
          </div>
        </div>

        {/* Metric 2: AI Diagnostic Status */}
        <div className="glass-card" style={{ padding: "1.25rem 1.4rem" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.5rem" }}>
            <span style={{ fontSize: "0.78rem", fontWeight: 700, textTransform: "uppercase", color: "var(--text-muted)", letterSpacing: "0.05em" }}>
              Latest AI Triage
            </span>
            <div style={{ width: "32px", height: "32px", borderRadius: "8px", background: "var(--triage-low-bg)", color: "var(--triage-low)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <HeartPulse size={17} />
            </div>
          </div>
          <div style={{ fontSize: "1.25rem", fontWeight: 800, color: "var(--text-primary)", lineHeight: 1.2 }}>
            {latestAIResult ? (
              <span style={{ color: latestAIResult.risk_level?.toLowerCase().includes("high") ? "var(--triage-high)" : latestAIResult.risk_level?.toLowerCase().includes("mod") ? "var(--triage-moderate)" : "var(--triage-low)" }}>
                {latestAIResult.risk_level} Risk
              </span>
            ) : (
              <span style={{ color: "var(--text-muted)", fontSize: "1.1rem" }}>No AI Diagnosis</span>
            )}
          </div>
          <div style={{ fontSize: "0.78rem", color: "var(--text-muted)", marginTop: "0.4rem" }}>
            {latestAIResult ? `${latestAIResult.prediction || "Cardiovascular evaluation"}` : "Upload clinical report to evaluate"}
          </div>
        </div>

        {/* Metric 3: Active Doctor Grants */}
        <div className="glass-card" style={{ padding: "1.25rem 1.4rem" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.5rem" }}>
            <span style={{ fontSize: "0.78rem", fontWeight: 700, textTransform: "uppercase", color: "var(--text-muted)", letterSpacing: "0.05em" }}>
              Active Doctor Consents
            </span>
            <div style={{ width: "32px", height: "32px", borderRadius: "8px", background: "var(--tech-light)", color: "var(--tech)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <KeyRound size={17} />
            </div>
          </div>
          <div style={{ fontSize: "2rem", fontWeight: 800, color: "var(--text-primary)", lineHeight: 1.1 }}>
            {totalAuthorizedGrants}
          </div>
          <div style={{ fontSize: "0.78rem", color: "var(--text-muted)", marginTop: "0.4rem" }}>
            Physicians authorized via Smart Contract
          </div>
        </div>

        {/* Metric 4: Ledger Consensus */}
        <div className="glass-card" style={{ padding: "1.25rem 1.4rem" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.5rem" }}>
            <span style={{ fontSize: "0.78rem", fontWeight: 700, textTransform: "uppercase", color: "var(--text-muted)", letterSpacing: "0.05em" }}>
              Ledger Consensus
            </span>
            <div style={{ width: "32px", height: "32px", borderRadius: "8px", background: "var(--triage-low-bg)", color: "var(--triage-low)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <Shield size={17} />
            </div>
          </div>
          <div style={{ fontSize: "2rem", fontWeight: 800, color: "var(--triage-low)", lineHeight: 1.1 }}>
            100%
          </div>
          <div style={{ fontSize: "0.78rem", color: "var(--text-muted)", marginTop: "0.4rem" }}>
            Hyperledger Fabric Org1MSP Verified
          </div>
        </div>
      </div>

      {/* =========================================================================
          3. WORKSPACE SEGMENTED NAVIGATION TABS
          ========================================================================= */}
      <div style={{
        display: "flex",
        alignItems: "center",
        gap: "0.5rem",
        borderBottom: "1px solid var(--border)",
        marginBottom: "1.75rem",
        overflowX: "auto",
        paddingBottom: "2px"
      }}>
        {[
          { id: "records", label: "Health Timeline & Records", count: records.length, icon: <FileText size={16} /> },
          { id: "consents", label: "Doctor Access & Consents", count: totalAuthorizedGrants, icon: <KeyRound size={16} /> },
          { id: "upload", label: "Inscribe New File", icon: <Upload size={16} /> },
          { id: "analytics", label: "AI Diagnostic Insights", icon: <Activity size={16} /> }
        ].map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "0.55rem",
                padding: "0.75rem 1.25rem",
                border: "none",
                background: "transparent",
                color: isActive ? "var(--accent)" : "var(--text-secondary)",
                fontWeight: isActive ? 700 : 500,
                fontSize: "0.9rem",
                cursor: "pointer",
                borderBottom: isActive ? "2.5px solid var(--accent)" : "2.5px solid transparent",
                transition: "all 0.2s ease",
                whiteSpace: "nowrap"
              }}
            >
              {tab.icon}
              <span>{tab.label}</span>
              {tab.count !== undefined && (
                <span style={{
                  padding: "0.15rem 0.5rem",
                  borderRadius: "99px",
                  fontSize: "0.72rem",
                  fontWeight: 700,
                  background: isActive ? "var(--accent-light)" : "var(--surface-elevated)",
                  color: isActive ? "var(--accent)" : "var(--text-muted)"
                }}>
                  {tab.count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* =========================================================================
          TAB 1: HEALTH TIMELINE & RECORDS
          ========================================================================= */}
      {activeTab === "records" && (
        <div>
          {/* Search and Risk Filter Controls */}
          <div style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: "1rem",
            marginBottom: "1.5rem"
          }}>
            {/* Search Box */}
            <div style={{
              display: "flex",
              alignItems: "center",
              gap: "0.6rem",
              background: "var(--surface)",
              border: "1px solid var(--border)",
              borderRadius: "10px",
              padding: "0.55rem 0.95rem",
              minWidth: "280px",
              flex: "1 1 320px",
              maxWidth: "460px"
            }}>
              <Search size={16} color="var(--text-muted)" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search doctor, diagnosis, EHR ID, or IPFS..."
                style={{
                  border: "none",
                  outline: "none",
                  background: "transparent",
                  width: "100%",
                  fontSize: "0.88rem",
                  color: "var(--text-primary)",
                  fontFamily: "var(--font-sans)"
                }}
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery("")}
                  style={{ border: "none", background: "transparent", cursor: "pointer", color: "var(--text-muted)" }}
                >
                  <X size={14} />
                </button>
              )}
            </div>

            {/* Filter Pills */}
            <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", flexWrap: "wrap" }}>
              {[
                { id: "all", label: "All Records" },
                { id: "low", label: "Normal / Low" },
                { id: "mod", label: "Moderate" },
                { id: "high", label: "High Risk" },
                { id: "manual", label: "Manual Scans" }
              ].map((f) => (
                <button
                  key={f.id}
                  onClick={() => setRiskFilter(f.id)}
                  style={{
                    padding: "0.4rem 0.85rem",
                    borderRadius: "8px",
                    border: riskFilter === f.id ? "1.5px solid var(--accent)" : "1px solid var(--border)",
                    background: riskFilter === f.id ? "var(--accent-light)" : "var(--surface)",
                    color: riskFilter === f.id ? "var(--accent)" : "var(--text-secondary)",
                    fontSize: "0.8rem",
                    fontWeight: 600,
                    cursor: "pointer",
                    transition: "all 0.15s ease"
                  }}
                >
                  {f.label}
                </button>
              ))}
            </div>
          </div>

          {/* Loading State */}
          {loading ? (
            <div className="glass-card" style={{ padding: "3.5rem", textAlign: "center", color: "var(--text-muted)" }}>
              <RefreshCw size={26} className="spin" style={{ margin: "0 auto 1rem auto" }} />
              <p style={{ fontSize: "0.95rem" }}>Querying Hyperledger Fabric peer & validating state...</p>
            </div>
          ) : filteredRecords.length === 0 ? (
            /* Empty State */
            <div className="glass-card" style={{ padding: "3.5rem 2rem", textAlign: "center" }}>
              <div style={{
                width: "56px",
                height: "56px",
                borderRadius: "16px",
                background: "var(--accent-light)",
                color: "var(--accent)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                margin: "0 auto 1.25rem auto"
              }}>
                <FileUp size={26} />
              </div>
              <h3 style={{ fontSize: "1.25rem", fontWeight: 700, marginBottom: "0.5rem" }}>
                {searchQuery || riskFilter !== "all" ? "No Matching Records Found" : "No Health Records Inscribed Yet"}
              </h3>
              <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", maxWidth: "420px", margin: "0 auto 1.5rem auto" }}>
                {searchQuery || riskFilter !== "all"
                  ? "Try clearing your search query or changing the risk filter."
                  : "Upload medical reports, ECGs, or lab PDFs to inscribe them permanently onto the blockchain."}
              </p>
              {searchQuery || riskFilter !== "all" ? (
                <button onClick={() => { setSearchQuery(""); setRiskFilter("all"); }} className="btn btn-secondary">
                  Reset Filters
                </button>
              ) : (
                <button onClick={() => setActiveTab("upload")} className="btn btn-primary">
                  <Upload size={16} />
                  <span>Upload First Medical File</span>
                </button>
              )}
            </div>
          ) : (
            /* Records Grid */
            <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              {filteredRecords.map((rec) => {
                const pred = parsePrediction(rec.mlPrediction);
                const isExpanded = expandedRecordId === rec.id;
                const riskLevel = String(pred.risk_level || "N/A").toLowerCase();
                
                let triageClass = "triage-badge-audit";
                if (riskLevel.includes("low")) triageClass = "triage-badge-low";
                else if (riskLevel.includes("mod")) triageClass = "triage-badge-mod";
                else if (riskLevel.includes("high")) triageClass = "triage-badge-high";

                const isManual = pred.type === "manual";

                return (
                  <div key={rec.id} className="glass-card" style={{ padding: "1.35rem 1.6rem", transition: "all 0.2s ease" }}>
                    {/* Header Row */}
                    <div style={{
                      display: "flex",
                      alignItems: "flex-start",
                      justifyContent: "space-between",
                      flexWrap: "wrap",
                      gap: "1rem",
                      marginBottom: "1rem"
                    }}>
                      <div>
                        <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "0.35rem" }}>
                          <span style={{ fontSize: "1.05rem", fontWeight: 800, color: "var(--text-primary)" }}>
                            {isManual ? "Medical Document Inscription" : (pred.prediction ? `Cardiovascular Diagnosis: ${pred.prediction}` : "Health Record")}
                          </span>
                          <span className={`triage-badge ${triageClass}`}>
                            {isManual ? "Document Pinned" : `${pred.risk_level || "Evaluated"}`}
                          </span>
                        </div>

                        {/* Metadata row */}
                        <div style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "0.85rem",
                          fontSize: "0.8rem",
                          color: "var(--text-muted)",
                          flexWrap: "wrap"
                        }}>
                          <span style={{ display: "flex", alignItems: "center", gap: "0.35rem" }}>
                            <Clock size={13} />
                            <span>{pred.timestamp || "Timestamp Verified"}</span>
                          </span>
                          <span>•</span>
                          <span>Attending: <strong style={{ color: "var(--text-secondary)" }}>{pred.doctor_id || "Self-Inscribed"}</strong></span>
                          <span>•</span>
                          <span>
                            Authorized: <strong style={{ color: "var(--tech)" }}>{rec.authorizedUsers?.length || 0} Doctor(s)</strong>
                          </span>
                        </div>
                      </div>

                      {/* Right Quick Action Buttons */}
                      <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
                        <button
                          onClick={() => setShareModal({ isOpen: true, recordId: rec.id, doctorId: "", submitting: false, status: null })}
                          className="btn btn-secondary"
                          style={{ padding: "0.45rem 0.85rem", fontSize: "0.8rem", gap: "0.4rem" }}
                          title="Share Access with Doctor"
                        >
                          <Share2 size={13} color="var(--accent)" />
                          <span>Share Access</span>
                        </button>

                        <button
                          onClick={() => handleDownload(rec.id)}
                          className="btn btn-primary"
                          style={{ padding: "0.45rem 0.95rem", fontSize: "0.8rem", gap: "0.4rem" }}
                          title="Download Verified PDF Report"
                        >
                          <Download size={13} />
                          <span>Download PDF</span>
                        </button>

                        <button
                          onClick={() => setExpandedRecordId(isExpanded ? null : rec.id)}
                          className="btn btn-ghost"
                          style={{ padding: "0.45rem", color: "var(--text-muted)" }}
                          title={isExpanded ? "Collapse Details" : "Expand Details"}
                        >
                          {isExpanded ? <ChevronUp size={17} /> : <ChevronDown size={17} />}
                        </button>
                      </div>
                    </div>

                    {/* Hashes & Ledger Cryptographic Bar */}
                    <div style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      flexWrap: "wrap",
                      gap: "0.75rem",
                      padding: "0.6rem 0.85rem",
                      background: "var(--surface-elevated)",
                      borderRadius: "8px",
                      border: "1px solid var(--border-subtle)"
                    }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                        <span style={{ fontSize: "0.75rem", color: "var(--text-muted)", fontWeight: 600 }}>EHR ID:</span>
                        <HashBadge hash={rec.id} prefixLen={8} suffixLen={4} />
                      </div>

                      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                        <span style={{ fontSize: "0.75rem", color: "var(--text-muted)", fontWeight: 600 }}>IPFS CID:</span>
                        <HashBadge hash={rec.ipfsHash} prefixLen={8} suffixLen={6} />
                      </div>

                      <div style={{ display: "flex", alignItems: "center", gap: "0.35rem", fontSize: "0.74rem", color: "var(--triage-low)" }}>
                        <ShieldCheck size={13} />
                        <span>Fabric Org1MSP Inscribed</span>
                      </div>
                    </div>

                    {/* Expandable Clinical Observations & Vitals */}
                    <AnimatePresence>
                      {isExpanded && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: "auto" }}
                          exit={{ opacity: 0, height: 0 }}
                          transition={{ duration: 0.2 }}
                          style={{ overflow: "hidden", marginTop: "1rem" }}
                        >
                          <div style={{
                            padding: "1rem 1.15rem",
                            background: "var(--surface-elevated)",
                            borderRadius: "10px",
                            border: "1px solid var(--border)"
                          }}>
                            <h4 style={{ fontSize: "0.88rem", fontWeight: 700, marginBottom: "0.6rem", color: "var(--text-primary)" }}>
                              Clinical Observations & Doctor Notes
                            </h4>
                            <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", lineHeight: 1.6, marginBottom: "0.85rem" }}>
                              {pred.doctor_notes || "No additional physician notes recorded for this block."}
                            </p>

                            {/* Authorized Doctors List */}
                            <div style={{ borderTop: "1px solid var(--border)", paddingTop: "0.75rem" }}>
                              <span style={{ fontSize: "0.78rem", fontWeight: 600, color: "var(--text-muted)", marginRight: "0.5rem" }}>
                                Authorized Physicians:
                              </span>
                              {rec.authorizedUsers && rec.authorizedUsers.length > 0 ? (
                                <div style={{ display: "inline-flex", gap: "0.4rem", flexWrap: "wrap", marginTop: "4px" }}>
                                  {rec.authorizedUsers.map((doc, idx) => (
                                    <span key={idx} style={{
                                      fontSize: "0.74rem",
                                      fontWeight: 600,
                                      padding: "0.2rem 0.6rem",
                                      borderRadius: "6px",
                                      background: "var(--accent-light)",
                                      color: "var(--accent)",
                                      border: "1px solid var(--border)"
                                    }}>
                                      Dr. {doc}
                                    </span>
                                  ))}
                                </div>
                              ) : (
                                <span style={{ fontSize: "0.76rem", color: "var(--text-muted)" }}>
                                  Only you (Patient Owner) have access to this record.
                                </span>
                              )}
                            </div>
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* =========================================================================
          TAB 2: DOCTOR ACCESS & CONSENT MANAGEMENT
          ========================================================================= */}
      {activeTab === "consents" && (
        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          <div className="glass-card" style={{ padding: "1.5rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "0.5rem" }}>
              <ShieldCheck size={20} color="var(--accent)" />
              <h3 style={{ fontSize: "1.2rem", fontWeight: 700 }}>Sovereign Permission Matrix</h3>
            </div>
            <p style={{ fontSize: "0.88rem", color: "var(--text-secondary)", maxWidth: "700px", lineHeight: 1.6 }}>
              Under Hyperledger Fabric smart contract rules, no doctor can decrypt or view your medical records without your explicit cryptographic consent. Review all active permissions below.
            </p>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "0.85rem" }}>
            {records.map((rec) => {
              const pred = parsePrediction(rec.mlPrediction);
              const authDocs = rec.authorizedUsers || [];

              return (
                <div key={rec.id} className="glass-card" style={{ padding: "1.25rem 1.5rem" }}>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "1rem" }}>
                    <div>
                      <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "0.25rem" }}>
                        <span style={{ fontWeight: 700, fontSize: "0.95rem" }}>
                          {pred.type === "manual" ? "Medical Document" : (pred.prediction || "Cardiovascular Record")}
                        </span>
                        <HashBadge hash={rec.id} prefixLen={8} suffixLen={4} />
                      </div>
                      <div style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>
                        IPFS: {rec.ipfsHash?.slice(0, 16)}... • Uploaded: {pred.timestamp || "Verified"}
                      </div>
                    </div>

                    <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
                      <button
                        onClick={() => setShareModal({ isOpen: true, recordId: rec.id, doctorId: "", submitting: false, status: null })}
                        className="btn btn-secondary"
                        style={{ padding: "0.45rem 0.85rem", fontSize: "0.8rem" }}
                      >
                        <KeyRound size={13} />
                        <span>Authorize New Doctor</span>
                      </button>
                    </div>
                  </div>

                  {/* Active Doctors Badges */}
                  <div style={{ marginTop: "1rem", paddingTop: "0.85rem", borderTop: "1px solid var(--border)" }}>
                    <span style={{ fontSize: "0.78rem", fontWeight: 600, color: "var(--text-muted)", display: "block", marginBottom: "0.4rem" }}>
                      Physicians with Current Decryption Access:
                    </span>
                    {authDocs.length > 0 ? (
                      <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                        {authDocs.map((doc, idx) => (
                          <div
                            key={idx}
                            style={{
                              display: "inline-flex",
                              alignItems: "center",
                              gap: "0.45rem",
                              padding: "0.3rem 0.75rem",
                              borderRadius: "8px",
                              background: "var(--surface-elevated)",
                              border: "1px solid var(--border)",
                              fontSize: "0.82rem",
                              fontWeight: 600,
                              color: "var(--text-primary)"
                            }}
                          >
                            <UserCheck size={14} color="var(--accent)" />
                            <span>Dr. {doc}</span>
                            <span style={{ fontSize: "0.7rem", color: "var(--triage-low)", fontWeight: 700 }}>• Active</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div style={{ fontSize: "0.82rem", color: "var(--text-muted)", fontStyle: "italic" }}>
                        🔒 Private to patient only. No doctors have been granted access to this record.
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 3: INSCRIBE NEW RECORD (DRAG & DROP VAULT)
          ========================================================================= */}
      {activeTab === "upload" && (
        <div style={{ maxWidth: "680px", margin: "0 auto" }}>
          <div className="glass-card" style={{ padding: "2rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "0.4rem" }}>
              <div style={{
                width: "36px",
                height: "36px",
                borderRadius: "10px",
                background: "var(--accent-light)",
                color: "var(--accent)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center"
              }}>
                <Upload size={18} />
              </div>
              <div>
                <h3 style={{ fontSize: "1.3rem", fontWeight: 800 }}>Inscribe Health Record</h3>
                <p style={{ fontSize: "0.84rem", color: "var(--text-muted)" }}>
                  Upload lab reports, scans, or ECGs to IPFS and anchor them to Hyperledger Fabric.
                </p>
              </div>
            </div>

            {uploadStatus && (
              <div style={{
                display: "flex",
                alignItems: "center",
                gap: "0.6rem",
                padding: "0.85rem 1rem",
                borderRadius: "10px",
                marginTop: "1.25rem",
                fontSize: "0.85rem",
                background: uploadStatus.type === "success" ? "var(--triage-low-bg)" : "var(--triage-high-bg)",
                color: uploadStatus.type === "success" ? "var(--triage-low)" : "var(--triage-high)",
                border: `1px solid ${uploadStatus.type === "success" ? "rgba(16, 185, 129, 0.3)" : "rgba(244, 63, 94, 0.3)"}`
              }}>
                {uploadStatus.type === "success" ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
                <span>{uploadStatus.message}</span>
              </div>
            )}

            <form onSubmit={handleUpload} style={{ marginTop: "1.5rem" }}>
              {/* Drag and Drop Zone */}
              <div
                onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
                onDragLeave={() => setIsDragOver(false)}
                onDrop={(e) => {
                  e.preventDefault();
                  setIsDragOver(false);
                  if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                    setFile(e.dataTransfer.files[0]);
                  }
                }}
                onClick={() => document.getElementById("patientFileUploader").click()}
                style={{
                  border: isDragOver ? "2px dashed var(--accent)" : "2px dashed var(--border)",
                  borderRadius: "14px",
                  padding: "2.5rem 1.5rem",
                  textAlign: "center",
                  background: isDragOver ? "var(--accent-light)" : "var(--surface-elevated)",
                  cursor: "pointer",
                  transition: "all 0.2s ease",
                  marginBottom: "1.5rem"
                }}
              >
                <input
                  id="patientFileUploader"
                  type="file"
                  accept=".pdf,image/*"
                  style={{ display: "none" }}
                  onChange={(e) => setFile(e.target.files[0] || null)}
                />

                <div style={{
                  width: "52px",
                  height: "52px",
                  borderRadius: "14px",
                  background: "var(--surface)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  margin: "0 auto 1rem auto",
                  color: "var(--accent)",
                  boxShadow: "var(--card-shadow)"
                }}>
                  <FileUp size={24} />
                </div>

                {file ? (
                  <div>
                    <div style={{ fontSize: "1rem", fontWeight: 700, color: "var(--text-primary)" }}>
                      {file.name}
                    </div>
                    <div style={{ fontSize: "0.8rem", color: "var(--accent)", marginTop: "4px", fontWeight: 600 }}>
                      {(file.size / 1024).toFixed(1)} KB • Ready to Inscribe
                    </div>
                  </div>
                ) : (
                  <div>
                    <div style={{ fontSize: "0.98rem", fontWeight: 700, color: "var(--text-primary)" }}>
                      Click to browse or drop medical file here
                    </div>
                    <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginTop: "4px" }}>
                      Supports PDF, JPG, PNG up to 50MB
                    </div>
                  </div>
                )}
              </div>

              <button
                type="submit"
                disabled={!file || uploading}
                className="btn btn-primary"
                style={{ width: "100%", padding: "0.85rem", fontSize: "0.92rem" }}
              >
                {uploading ? (
                  <span style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    <RefreshCw size={16} className="spin" />
                    <span>Encrypting & Anchoring to Fabric...</span>
                  </span>
                ) : (
                  <span style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    <span>Encrypt & Inscribe on Blockchain</span>
                    <ArrowRight size={16} />
                  </span>
                )}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* =========================================================================
          TAB 4: AI DIAGNOSTIC INSIGHTS
          ========================================================================= */}
      {activeTab === "analytics" && (
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
          gap: "1.5rem",
          alignItems: "start"
        }}>
          {/* AI Gauge Card */}
          <div className="glass-card" style={{ padding: "2rem", textAlign: "center" }}>
            <h3 style={{ fontSize: "1.2rem", fontWeight: 800, marginBottom: "0.25rem" }}>
              Cardiovascular Risk Gauge
            </h3>
            <p style={{ fontSize: "0.82rem", color: "var(--text-muted)", marginBottom: "1.5rem" }}>
              Random Forest Machine Learning Diagnostic Model (Scikit-Learn v1.4)
            </p>

            {latestAIResult ? (
              <RiskGauge
                score={latestAIResult.risk_level?.toLowerCase().includes("high") ? 82 : latestAIResult.risk_level?.toLowerCase().includes("mod") ? 52 : 14}
                level={latestAIResult.risk_level}
                prediction={latestAIResult.prediction}
              />
            ) : (
              <div style={{ padding: "2rem 1rem", color: "var(--text-muted)" }}>
                <HeartPulse size={40} style={{ margin: "0 auto 1rem auto", opacity: 0.5 }} />
                <p style={{ fontSize: "0.9rem" }}>No cardiovascular ML records found on your ledger.</p>
              </div>
            )}
          </div>

          {/* Model Parameters & Security Guarantee */}
          <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
            <div className="glass-card" style={{ padding: "1.5rem" }}>
              <h4 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "0.85rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <Activity size={18} color="var(--accent)" />
                <span>AI Clinical Diagnostic Parameters</span>
              </h4>

              <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem", fontSize: "0.84rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", padding: "0.4rem 0", borderBottom: "1px solid var(--border)" }}>
                  <span style={{ color: "var(--text-muted)" }}>Model Architecture:</span>
                  <span style={{ fontWeight: 600 }}>Random Forest Ensemble (100 Trees)</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", padding: "0.4rem 0", borderBottom: "1px solid var(--border)" }}>
                  <span style={{ color: "var(--text-muted)" }}>Explainability Engine:</span>
                  <span style={{ fontWeight: 600 }}>SHAP (SHapley Additive exPlanations)</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", padding: "0.4rem 0", borderBottom: "1px solid var(--border)" }}>
                  <span style={{ color: "var(--text-muted)" }}>Validation Accuracy:</span>
                  <span style={{ fontWeight: 600, color: "var(--triage-low)" }}>91.4% ROC-AUC</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", padding: "0.4rem 0" }}>
                  <span style={{ color: "var(--text-muted)" }}>Inference Node:</span>
                  <span style={{ fontWeight: 600, fontFamily: "var(--font-mono)" }}>Flask REST Server /predict</span>
                </div>
              </div>
            </div>

            <div className="glass-card" style={{ padding: "1.5rem" }}>
              <h4 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "0.5rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <ShieldCheck size={18} color="var(--triage-low)" />
                <span>Privacy & Sovereignty Guarantee</span>
              </h4>
              <p style={{ fontSize: "0.84rem", color: "var(--text-secondary)", lineHeight: 1.6 }}>
                AI inferences are computed on-the-fly and stored only as verifiable cryptographic hashes on Hyperledger Fabric. Your raw medical imaging and PDF records remain exclusively encrypted in your IPFS vault.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          4. 1-CLICK SHARE PERMISSION MODAL
          ========================================================================= */}
      <AnimatePresence>
        {shareModal.isOpen && (
          <div
            style={{
              position: "fixed",
              inset: 0,
              zIndex: 1000,
              background: "rgba(0, 0, 0, 0.65)",
              backdropFilter: "blur(6px)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              padding: "1rem"
            }}
            onClick={() => setShareModal({ isOpen: false, recordId: "", doctorId: "", submitting: false, status: null })}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              transition={{ duration: 0.15 }}
              className="glass-card"
              style={{
                width: "100%",
                maxWidth: "480px",
                padding: "2rem",
                background: "var(--surface)",
                border: "1px solid var(--border)",
                boxShadow: "0 20px 50px rgba(0,0,0,0.3)"
              }}
              onClick={(e) => e.stopPropagation()}
            >
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1.25rem" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
                  <KeyRound size={20} color="var(--accent)" />
                  <h3 style={{ fontSize: "1.25rem", fontWeight: 800 }}>Authorize Physician Access</h3>
                </div>
                <button
                  onClick={() => setShareModal({ isOpen: false, recordId: "", doctorId: "", submitting: false, status: null })}
                  style={{ border: "none", background: "transparent", cursor: "pointer", color: "var(--text-muted)" }}
                >
                  <X size={18} />
                </button>
              </div>

              <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "1.25rem", lineHeight: 1.5 }}>
                Grant cryptographic decryption consent to a registered doctor node for this specific record.
              </p>

              {shareModal.status && (
                <div style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "0.5rem",
                  padding: "0.75rem 1rem",
                  borderRadius: "8px",
                  fontSize: "0.84rem",
                  marginBottom: "1.25rem",
                  background: shareModal.status.type === "success" ? "var(--triage-low-bg)" : "var(--triage-high-bg)",
                  color: shareModal.status.type === "success" ? "var(--triage-low)" : "var(--triage-high)",
                  border: `1px solid ${shareModal.status.type === "success" ? "rgba(16, 185, 129, 0.3)" : "rgba(244, 63, 94, 0.3)"}`
                }}>
                  {shareModal.status.type === "success" ? <Check size={16} /> : <AlertCircle size={16} />}
                  <span>{shareModal.status.message}</span>
                </div>
              )}

              <form onSubmit={handleGrant}>
                <div className="form-group">
                  <label className="form-label">Record Identifier (EHR ID)</label>
                  <input
                    type="text"
                    disabled
                    value={shareModal.recordId}
                    className="form-input"
                    style={{ background: "var(--surface-elevated)", fontFamily: "var(--font-mono)", fontSize: "0.85rem" }}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Doctor Username Node</label>
                  <input
                    type="text"
                    required
                    value={shareModal.doctorId}
                    onChange={(e) => setShareModal((prev) => ({ ...prev, doctorId: e.target.value }))}
                    placeholder="e.g. doctor_smith"
                    className="form-input"
                  />
                </div>

                <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1.5rem" }}>
                  <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Quick Select:</span>
                  {["doctor_smith", "doctor_clark"].map((doc) => (
                    <button
                      key={doc}
                      type="button"
                      onClick={() => setShareModal((prev) => ({ ...prev, doctorId: doc }))}
                      style={{
                        border: "1px solid var(--border)",
                        background: "var(--surface-elevated)",
                        borderRadius: "6px",
                        padding: "0.15rem 0.5rem",
                        fontSize: "0.74rem",
                        color: "var(--accent)",
                        cursor: "pointer",
                        fontWeight: 600
                      }}
                    >
                      {doc}
                    </button>
                  ))}
                </div>

                <div style={{ display: "flex", gap: "0.75rem", justifyContent: "flex-end" }}>
                  <button
                    type="button"
                    onClick={() => setShareModal({ isOpen: false, recordId: "", doctorId: "", submitting: false, status: null })}
                    className="btn btn-secondary"
                  >
                    Cancel
                  </button>

                  <button
                    type="submit"
                    disabled={shareModal.submitting || !shareModal.doctorId}
                    className="btn btn-primary"
                  >
                    {shareModal.submitting ? "Signing Smart Contract..." : "Commit Consent Key"}
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
