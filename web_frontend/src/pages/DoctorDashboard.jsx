import React, { useState, useEffect, useMemo } from "react";
import { useAuth } from "../context/AuthContext";
import { api } from "../services/api";
import RiskGauge from "../components/RiskGauge";
import HashBadge from "../components/HashBadge";
import { motion, AnimatePresence } from "framer-motion";
import {
  Stethoscope, Activity, Heart, Brain, FileText, Download,
  Sparkles, ShieldCheck, ChevronRight, CheckCircle2,
  AlertCircle, RefreshCw, BarChart2, Search, ArrowRight,
  UserCheck, Shield, Clock, Zap, Check, FileUp, X, HeartPulse
} from "lucide-react";

export default function DoctorDashboard() {
  const { user } = useAuth();
  const [sharedRecords, setSharedRecords] = useState([]);
  const [loadingRecords, setLoadingRecords] = useState(true);
  const [selectedRecord, setSelectedRecord] = useState(null);
  
  // Navigation Tab
  const [activeTab, setActiveTab] = useState("queue"); // "queue" | "cockpit" | "history"
  const [searchPatient, setSearchPatient] = useState("");

  // Vitals State (17 features with clinical defaults)
  const [patientId, setPatientId] = useState("");
  const [vitals, setVitals] = useState({
    Age: 52,
    Gender: "Male",
    "Blood Pressure": 135,
    Glucose: 110,
    Cholesterol: 215,
    Triglycerides: 160,
    HbA1c: 5.8,
    "Oxygen Saturation": 97,
    BMI: 27.4,
    "Sleep Hours": 7.0,
    "Physical Activity": 3.0,
    "Stress Level": 5.0,
    Smoking: 0,
    Alcohol: 0,
    "Family History": 1,
    "Diet Score": 6.0,
    LengthOfStay: 2
  });

  // Clinical Presets
  const clinicalPresets = {
    baseline: {
      name: "Healthy Baseline",
      icon: "🟢",
      data: {
        Age: 45, Gender: "Male", "Blood Pressure": 118, Glucose: 92, Cholesterol: 175,
        Triglycerides: 120, HbA1c: 5.2, "Oxygen Saturation": 99, BMI: 23.5,
        "Sleep Hours": 7.5, "Physical Activity": 4.0, "Stress Level": 3.0,
        Smoking: 0, Alcohol: 0, "Family History": 0, "Diet Score": 8.0, LengthOfStay: 1
      }
    },
    hypertensive: {
      name: "Hypertensive Alert",
      icon: "🟡",
      data: {
        Age: 58, Gender: "Male", "Blood Pressure": 158, Glucose: 115, Cholesterol: 240,
        Triglycerides: 195, HbA1c: 6.1, "Oxygen Saturation": 96, BMI: 29.2,
        "Sleep Hours": 6.0, "Physical Activity": 2.0, "Stress Level": 7.5,
        Smoking: 1, Alcohol: 1, "Family History": 1, "Diet Score": 4.5, LengthOfStay: 3
      }
    },
    diabetic: {
      name: "Diabetic Metabolic",
      icon: "🟠",
      data: {
        Age: 62, Gender: "Female", "Blood Pressure": 145, Glucose: 195, Cholesterol: 265,
        Triglycerides: 240, HbA1c: 8.4, "Oxygen Saturation": 95, BMI: 32.1,
        "Sleep Hours": 5.5, "Physical Activity": 1.5, "Stress Level": 6.0,
        Smoking: 0, Alcohol: 0, "Family History": 1, "Diet Score": 3.5, LengthOfStay: 4
      }
    },
    cardiac: {
      name: "Cardiac Critical",
      icon: "🔴",
      data: {
        Age: 67, Gender: "Male", "Blood Pressure": 182, Glucose: 210, Cholesterol: 295,
        Triglycerides: 310, HbA1c: 7.9, "Oxygen Saturation": 91, BMI: 34.0,
        "Sleep Hours": 4.5, "Physical Activity": 0.5, "Stress Level": 9.0,
        Smoking: 1, Alcohol: 1, "Family History": 1, "Diet Score": 2.0, LengthOfStay: 6
      }
    }
  };

  // Prediction Output State
  const [predictionData, setPredictionData] = useState(null);
  const [predicting, setPredicting] = useState(false);
  const [predictError, setPredictError] = useState(null);

  // Inscribe State
  const [doctorNotes, setDoctorNotes] = useState("");
  const [inscribing, setInscribing] = useState(false);
  const [inscribeSuccess, setInscribeSuccess] = useState(null);

  // Extract State
  const [extracting, setExtracting] = useState(false);
  const [extractedInfo, setExtractedInfo] = useState(null);

  const fetchSharedRecords = async () => {
    setLoadingRecords(true);
    try {
      const data = await api.getRecordsByDoctor();
      setSharedRecords(data || []);
    } catch (err) {
      console.error("Error fetching doctor records:", err);
    } finally {
      setLoadingRecords(false);
    }
  };

  useEffect(() => {
    fetchSharedRecords();
  }, []);

  const handleVitalChange = (field, value) => {
    setVitals((prev) => ({
      ...prev,
      [field]: field === "Gender" ? value : Number(value)
    }));
  };

  const applyPreset = (presetKey) => {
    if (clinicalPresets[presetKey]) {
      setVitals(clinicalPresets[presetKey].data);
    }
  };

  const handleSelectRecord = async (rec, switchToCockpit = true) => {
    setSelectedRecord(rec);
    setPatientId(rec.patientId || "");
    setInscribeSuccess(null);
    setExtractedInfo(null);

    // Auto extract vitals from PDF if ipfsHash is available
    if (rec.ipfsHash) {
      setExtracting(true);
      try {
        const res = await api.extractVitals(rec.ipfsHash);
        if (res.vitals && Object.keys(res.vitals).length > 0) {
          setVitals((prev) => ({ ...prev, ...res.vitals }));
          setExtractedInfo(Object.keys(res.vitals));
        }
      } catch (e) {
        console.warn("Could not auto-extract vitals:", e);
      } finally {
        setExtracting(false);
      }
    }

    if (switchToCockpit) {
      setActiveTab("cockpit");
    }
  };

  const handleRunPrediction = async () => {
    setPredicting(true);
    setPredictError(null);
    try {
      const res = await api.predict(vitals);
      setPredictionData(res);
    } catch (err) {
      setPredictError(err.message);
    } finally {
      setPredicting(false);
    }
  };

  const handleCommitToBlockchain = async () => {
    if (!patientId) {
      alert("Please specify a Target Patient Identifier");
      return;
    }
    setInscribing(true);
    try {
      const res = await api.createPredictionRecord({
        patientId,
        vitals,
        doctorNotes: doctorNotes || `Evaluated and certified by Dr. ${user?.username}`,
        targetEhrId: selectedRecord?.id || ""
      });
      setInscribeSuccess({
        recordId: res.record_id,
        ipfsHash: res.ipfs_hash,
        prediction: res.prediction,
        risk: res.risk_level
      });
      await fetchSharedRecords();
    } catch (err) {
      alert("Error writing to Fabric: " + err.message);
    } finally {
      setInscribing(false);
    }
  };

  // Filtered Patient Records
  const filteredRecords = useMemo(() => {
    return sharedRecords.filter((rec) => {
      if (!searchPatient.trim()) return true;
      const q = searchPatient.toLowerCase();
      return (
        (rec.patientId || "").toLowerCase().includes(q) ||
        (rec.id || "").toLowerCase().includes(q) ||
        (rec.ipfsHash || "").toLowerCase().includes(q)
      );
    });
  }, [sharedRecords, searchPatient]);

  return (
    <div className="container" style={{ padding: "2rem 1.5rem 4rem 1.5rem", maxWidth: "1280px" }}>
      {/* =========================================================================
          1. TOP DOCTOR IDENTITY & CLINICAL COMMAND BAR
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
            background: "linear-gradient(135deg, var(--accent) 0%, #1D4ED8 100%)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#FFFFFF",
            boxShadow: "0 6px 18px var(--accent-glow)",
            flexShrink: 0
          }}>
            <Stethoscope size={28} />
          </div>

          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "0.2rem" }}>
              <span style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--text-primary)" }}>
                Dr. {user?.username}
              </span>
              <span className="triage-badge triage-badge-low" style={{ fontSize: "0.7rem", padding: "0.15rem 0.55rem" }}>
                <ShieldCheck size={12} />
                Physician Node Verified
              </span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", fontSize: "0.82rem", color: "var(--text-secondary)" }}>
              <span>Role: <strong style={{ color: "var(--accent)" }}>Attending Clinician</strong></span>
              <span>•</span>
              <span>Org1MSP Active</span>
              <span>•</span>
              <span style={{ fontFamily: "var(--font-mono)", color: "var(--accent)" }}>Smart Contract: ehr_1.0</span>
            </div>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <button
            onClick={fetchSharedRecords}
            className="btn btn-secondary"
            disabled={loadingRecords}
            style={{ padding: "0.55rem 1rem", fontSize: "0.84rem" }}
          >
            <RefreshCw size={15} className={loadingRecords ? "spin" : ""} />
            <span>Refresh Queue</span>
          </button>

          <button
            onClick={() => setActiveTab("cockpit")}
            className="btn btn-primary"
            style={{ padding: "0.55rem 1.15rem", fontSize: "0.84rem" }}
          >
            <Brain size={15} />
            <span>Launch AI Cockpit</span>
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
        {/* Metric 1: Shared Patient Cases */}
        <div className="glass-card" style={{ padding: "1.25rem 1.4rem" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.5rem" }}>
            <span style={{ fontSize: "0.78rem", fontWeight: 700, textTransform: "uppercase", color: "var(--text-muted)", letterSpacing: "0.05em" }}>
              Accessible Patient Cases
            </span>
            <div style={{ width: "32px", height: "32px", borderRadius: "8px", background: "var(--accent-light)", color: "var(--accent)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <UserCheck size={17} />
            </div>
          </div>
          <div style={{ fontSize: "2rem", fontWeight: 800, color: "var(--text-primary)", lineHeight: 1.1 }}>
            {sharedRecords.length}
          </div>
          <div style={{ fontSize: "0.78rem", color: "var(--text-muted)", marginTop: "0.4rem" }}>
            Cryptographically granted by patients
          </div>
        </div>

        {/* Metric 2: AI Inference Engine */}
        <div className="glass-card" style={{ padding: "1.25rem 1.4rem" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.5rem" }}>
            <span style={{ fontSize: "0.78rem", fontWeight: 700, textTransform: "uppercase", color: "var(--text-muted)", letterSpacing: "0.05em" }}>
              AI Diagnostic Engine
            </span>
            <div style={{ width: "32px", height: "32px", borderRadius: "8px", background: "var(--triage-low-bg)", color: "var(--triage-low)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <Brain size={17} />
            </div>
          </div>
          <div style={{ fontSize: "1.25rem", fontWeight: 800, color: "var(--triage-low)", lineHeight: 1.2 }}>
            Random Forest v1.4
          </div>
          <div style={{ fontSize: "0.78rem", color: "var(--text-muted)", marginTop: "0.4rem" }}>
            SHAP Explainability TreeExplainer Active
          </div>
        </div>

        {/* Metric 3: Active Patient Selected */}
        <div className="glass-card" style={{ padding: "1.25rem 1.4rem" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.5rem" }}>
            <span style={{ fontSize: "0.78rem", fontWeight: 700, textTransform: "uppercase", color: "var(--text-muted)", letterSpacing: "0.05em" }}>
              Active Case Target
            </span>
            <div style={{ width: "32px", height: "32px", borderRadius: "8px", background: "var(--surface-elevated)", color: "var(--text-secondary)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <HeartPulse size={17} />
            </div>
          </div>
          <div style={{ fontSize: "1.3rem", fontWeight: 800, color: selectedRecord ? "var(--accent)" : "var(--text-muted)", lineHeight: 1.2 }}>
            {selectedRecord ? selectedRecord.patientId : (patientId || "None Selected")}
          </div>
          <div style={{ fontSize: "0.78rem", color: "var(--text-muted)", marginTop: "0.4rem" }}>
            {selectedRecord ? `EHR: ${selectedRecord.id?.slice(0, 10)}...` : "Select a patient to load dossier"}
          </div>
        </div>

        {/* Metric 4: Fabric Ledger Trust */}
        <div className="glass-card" style={{ padding: "1.25rem 1.4rem" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.5rem" }}>
            <span style={{ fontSize: "0.78rem", fontWeight: 700, textTransform: "uppercase", color: "var(--text-muted)", letterSpacing: "0.05em" }}>
              Smart Contract Security
            </span>
            <div style={{ width: "32px", height: "32px", borderRadius: "8px", background: "var(--triage-low-bg)", color: "var(--triage-low)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <Shield size={17} />
            </div>
          </div>
          <div style={{ fontSize: "2rem", fontWeight: 800, color: "var(--triage-low)", lineHeight: 1.1 }}>
            100%
          </div>
          <div style={{ fontSize: "0.78rem", color: "var(--text-muted)", marginTop: "0.4rem" }}>
            ABAC Verification Enabled
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
          { id: "queue", label: "Patient Case Queue & Files", count: sharedRecords.length, icon: <FileText size={16} /> },
          { id: "cockpit", label: "AI Diagnostic Cockpit & Simulator", icon: <Brain size={16} /> },
          { id: "history", label: "Certified Blockchain Inscriptions", icon: <ShieldCheck size={16} /> }
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
          TAB 1: PATIENT CASE QUEUE & RECORDS
          ========================================================================= */}
      {activeTab === "queue" && (
        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          {/* Search Bar */}
          <div style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: "1rem"
          }}>
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
                value={searchPatient}
                onChange={(e) => setSearchPatient(e.target.value)}
                placeholder="Search by Patient Node ID, EHR ID, or IPFS..."
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
              {searchPatient && (
                <button
                  onClick={() => setSearchPatient("")}
                  style={{ border: "none", background: "transparent", cursor: "pointer", color: "var(--text-muted)" }}
                >
                  <X size={14} />
                </button>
              )}
            </div>

            <span style={{ fontSize: "0.84rem", color: "var(--text-muted)" }}>
              {filteredRecords.length} patient records accessible under your doctor key
            </span>
          </div>

          {/* Records List */}
          {loadingRecords ? (
            <div className="glass-card" style={{ padding: "3.5rem", textAlign: "center", color: "var(--text-muted)" }}>
              <RefreshCw size={26} className="spin" style={{ margin: "0 auto 1rem auto" }} />
              <p style={{ fontSize: "0.95rem" }}>Querying Hyperledger Fabric peer for patient permissions...</p>
            </div>
          ) : filteredRecords.length === 0 ? (
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
                <UserCheck size={26} />
              </div>
              <h3 style={{ fontSize: "1.25rem", fontWeight: 700, marginBottom: "0.5rem" }}>
                {searchPatient ? "No Matching Patients Found" : "No Patient Records In Your Queue"}
              </h3>
              <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", maxWidth: "420px", margin: "0 auto" }}>
                {searchPatient
                  ? "Try searching for a different patient ID or reset your query."
                  : `Patients must grant permission to your physician username (Dr. ${user?.username}) from their dashboard.`}
              </p>
            </div>
          ) : (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(380px, 1fr))", gap: "1.25rem" }}>
              {filteredRecords.map((rec) => {
                const isSelected = selectedRecord?.id === rec.id;
                return (
                  <div
                    key={rec.id}
                    className="glass-card"
                    style={{
                      padding: "1.4rem",
                      border: isSelected ? "2px solid var(--accent)" : "1px solid var(--border)",
                      background: isSelected ? "var(--surface-elevated)" : "var(--surface)",
                      transition: "all 0.2s ease"
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: "0.75rem" }}>
                      <div>
                        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.25rem" }}>
                          <span style={{ fontSize: "1.1rem", fontWeight: 800, color: "var(--text-primary)" }}>
                            Patient: {rec.patientId}
                          </span>
                        </div>
                        <div style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>
                          Consent Granted • Verified on Hyperledger Fabric
                        </div>
                      </div>

                      <span className="triage-badge triage-badge-low" style={{ fontSize: "0.7rem" }}>
                        Active Decryption
                      </span>
                    </div>

                    {/* Hashes Row */}
                    <div style={{
                      display: "flex",
                      flexDirection: "column",
                      gap: "0.4rem",
                      padding: "0.65rem 0.8rem",
                      background: "var(--surface-elevated)",
                      borderRadius: "8px",
                      marginBottom: "1.1rem",
                      fontSize: "0.76rem"
                    }}>
                      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                        <span style={{ color: "var(--text-muted)" }}>EHR ID:</span>
                        <HashBadge hash={rec.id} prefixLen={8} suffixLen={4} />
                      </div>
                      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                        <span style={{ color: "var(--text-muted)" }}>IPFS CID:</span>
                        <HashBadge hash={rec.ipfsHash} prefixLen={8} suffixLen={6} />
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
                      <button
                        onClick={() => handleSelectRecord(rec, true)}
                        className="btn btn-primary"
                        style={{ flex: 1, padding: "0.5rem 0.85rem", fontSize: "0.82rem", gap: "0.4rem" }}
                      >
                        <Brain size={14} />
                        <span>Load into AI Cockpit</span>
                      </button>

                      <button
                        onClick={() => api.downloadReport(rec.id)}
                        className="btn btn-secondary"
                        style={{ padding: "0.5rem 0.85rem", fontSize: "0.82rem" }}
                        title="Download Original Medical PDF"
                      >
                        <Download size={14} />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* =========================================================================
          TAB 2: AI DIAGNOSTIC COCKPIT & SIMULATOR
          ========================================================================= */}
      {activeTab === "cockpit" && (
        <div style={{ display: "flex", flexDirection: "column", gap: "1.75rem" }}>
          {/* Active Target Banner & NLP Extraction */}
          <div className="glass-card" style={{ padding: "1.5rem" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "1rem" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                <div style={{ width: "40px", height: "40px", borderRadius: "10px", background: "var(--accent-light)", color: "var(--accent)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <HeartPulse size={20} />
                </div>
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    <h3 style={{ fontSize: "1.2rem", fontWeight: 800 }}>
                      Active Patient Telemetry: <span style={{ color: "var(--accent)" }}>{patientId || "patient_01"}</span>
                    </h3>
                  </div>
                  <p style={{ fontSize: "0.84rem", color: "var(--text-muted)" }}>
                    {selectedRecord ? `Attached to EHR Block #${selectedRecord.id?.slice(0, 10)}...` : "Select a patient or enter a target node ID below"}
                  </p>
                </div>
              </div>

              <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
                <span style={{ fontSize: "0.82rem", color: "var(--text-muted)" }}>Patient ID:</span>
                <input
                  type="text"
                  placeholder="patient_id"
                  value={patientId}
                  onChange={(e) => setPatientId(e.target.value)}
                  className="form-input"
                  style={{ width: "160px", padding: "0.45rem 0.75rem", fontSize: "0.85rem" }}
                />
              </div>
            </div>

            {/* NLP Extraction Status */}
            {extracting && (
              <div style={{ marginTop: "1rem", padding: "0.75rem 1rem", background: "var(--accent-light)", borderRadius: "8px", fontSize: "0.84rem", color: "var(--accent)", display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <Sparkles size={16} className="spin" />
                <span>Extracting clinical vitals from IPFS medical document via Scikit-NLP parser...</span>
              </div>
            )}

            {extractedInfo && (
              <div style={{ marginTop: "1rem", padding: "0.75rem 1rem", background: "var(--triage-low-bg)", borderRadius: "8px", fontSize: "0.84rem", color: "var(--triage-low)", display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <CheckCircle2 size={16} />
                <span>Extracted {extractedInfo.length} biometric parameters from PDF document: {extractedInfo.slice(0, 6).join(", ")}...</span>
              </div>
            )}
          </div>

          {/* Quick Clinical Presets Bar */}
          <div className="glass-card" style={{ padding: "1.25rem 1.5rem" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "0.75rem" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
                <Zap size={16} color="var(--accent)" />
                <span style={{ fontSize: "0.85rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--text-secondary)" }}>
                  Quick Clinical Presets:
                </span>
              </div>

              <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                {Object.entries(clinicalPresets).map(([key, preset]) => (
                  <button
                    key={key}
                    type="button"
                    onClick={() => applyPreset(key)}
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      gap: "0.4rem",
                      padding: "0.4rem 0.85rem",
                      borderRadius: "8px",
                      border: "1px solid var(--border)",
                      background: "var(--surface)",
                      color: "var(--text-primary)",
                      fontSize: "0.8rem",
                      fontWeight: 600,
                      cursor: "pointer",
                      transition: "all 0.15s ease"
                    }}
                  >
                    <span>{preset.icon}</span>
                    <span>{preset.name}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* 4 Multi-column Telemetry Panels */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "1.25rem" }}>
            {/* Panel 1: Cardiovascular */}
            <div className="glass-card" style={{ padding: "1.4rem" }}>
              <h4 style={{ fontSize: "0.85rem", textTransform: "uppercase", color: "var(--text-muted)", letterSpacing: "0.06em", marginBottom: "1.1rem" }}>
                Cardiovascular & Hemodynamics
              </h4>
              <div className="form-group">
                <label className="form-label">
                  <span>Blood Pressure (Systolic)</span>
                  <strong style={{ color: vitals["Blood Pressure"] >= 140 ? "var(--triage-high)" : vitals["Blood Pressure"] >= 130 ? "var(--triage-moderate)" : "var(--triage-low)" }}>
                    {vitals["Blood Pressure"]} mmHg
                  </strong>
                </label>
                <input
                  type="range"
                  min="80"
                  max="220"
                  value={vitals["Blood Pressure"]}
                  onChange={(e) => handleVitalChange("Blood Pressure", e.target.value)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">
                  <span>Blood Glucose</span>
                  <strong style={{ color: vitals.Glucose >= 140 ? "var(--triage-high)" : vitals.Glucose >= 110 ? "var(--triage-moderate)" : "var(--triage-low)" }}>
                    {vitals.Glucose} mg/dL
                  </strong>
                </label>
                <input
                  type="range"
                  min="50"
                  max="300"
                  value={vitals.Glucose}
                  onChange={(e) => handleVitalChange("Glucose", e.target.value)}
                />
              </div>

              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label">
                  <span>Oxygen Saturation</span>
                  <strong style={{ color: vitals["Oxygen Saturation"] < 95 ? "var(--triage-high)" : "var(--triage-low)" }}>
                    {vitals["Oxygen Saturation"]}%
                  </strong>
                </label>
                <input
                  type="range"
                  min="80"
                  max="100"
                  value={vitals["Oxygen Saturation"]}
                  onChange={(e) => handleVitalChange("Oxygen Saturation", e.target.value)}
                />
              </div>
            </div>

            {/* Panel 2: Lipids & Metabolism */}
            <div className="glass-card" style={{ padding: "1.4rem" }}>
              <h4 style={{ fontSize: "0.85rem", textTransform: "uppercase", color: "var(--text-muted)", letterSpacing: "0.06em", marginBottom: "1.1rem" }}>
                Lipid Profile & Metabolism
              </h4>
              <div className="form-group">
                <label className="form-label">
                  <span>Total Cholesterol</span>
                  <strong style={{ color: vitals.Cholesterol >= 240 ? "var(--triage-high)" : vitals.Cholesterol >= 200 ? "var(--triage-moderate)" : "var(--triage-low)" }}>
                    {vitals.Cholesterol} mg/dL
                  </strong>
                </label>
                <input
                  type="range"
                  min="100"
                  max="400"
                  value={vitals.Cholesterol}
                  onChange={(e) => handleVitalChange("Cholesterol", e.target.value)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">
                  <span>Triglycerides</span>
                  <strong style={{ color: vitals.Triglycerides >= 200 ? "var(--triage-high)" : vitals.Triglycerides >= 150 ? "var(--triage-moderate)" : "var(--triage-low)" }}>
                    {vitals.Triglycerides} mg/dL
                  </strong>
                </label>
                <input
                  type="range"
                  min="50"
                  max="500"
                  value={vitals.Triglycerides}
                  onChange={(e) => handleVitalChange("Triglycerides", e.target.value)}
                />
              </div>

              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label">
                  <span>HbA1c Glycated Hemoglobin</span>
                  <strong style={{ color: vitals.HbA1c >= 6.5 ? "var(--triage-high)" : vitals.HbA1c >= 5.7 ? "var(--triage-moderate)" : "var(--triage-low)" }}>
                    {vitals.HbA1c}%
                  </strong>
                </label>
                <input
                  type="range"
                  min="4.0"
                  max="14.0"
                  step="0.1"
                  value={vitals.HbA1c}
                  onChange={(e) => handleVitalChange("HbA1c", e.target.value)}
                />
              </div>
            </div>

            {/* Panel 3: Biometrics & Activity */}
            <div className="glass-card" style={{ padding: "1.4rem" }}>
              <h4 style={{ fontSize: "0.85rem", textTransform: "uppercase", color: "var(--text-muted)", letterSpacing: "0.06em", marginBottom: "1.1rem" }}>
                Biometrics & Physiology
              </h4>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem", marginBottom: "0.75rem" }}>
                <div className="form-group">
                  <label className="form-label">Age</label>
                  <input
                    type="number"
                    value={vitals.Age}
                    onChange={(e) => handleVitalChange("Age", e.target.value)}
                    className="form-input"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">BMI Index</label>
                  <input
                    type="number"
                    step="0.1"
                    value={vitals.BMI}
                    onChange={(e) => handleVitalChange("BMI", e.target.value)}
                    className="form-input"
                  />
                </div>
              </div>

              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label">
                  <span>Stress Level (0 - 10)</span>
                  <strong>{vitals["Stress Level"]}</strong>
                </label>
                <input
                  type="range"
                  min="0"
                  max="10"
                  step="0.5"
                  value={vitals["Stress Level"]}
                  onChange={(e) => handleVitalChange("Stress Level", e.target.value)}
                />
              </div>
            </div>

            {/* Panel 4: Risk Factors */}
            <div className="glass-card" style={{ padding: "1.4rem" }}>
              <h4 style={{ fontSize: "0.85rem", textTransform: "uppercase", color: "var(--text-muted)", letterSpacing: "0.06em", marginBottom: "1.1rem" }}>
                History & Risk Factors
              </h4>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem", marginBottom: "0.75rem" }}>
                <div className="form-group">
                  <label className="form-label">Smoking</label>
                  <select
                    value={vitals.Smoking}
                    onChange={(e) => handleVitalChange("Smoking", e.target.value)}
                    className="form-select"
                  >
                    <option value={0}>Non-Smoker</option>
                    <option value={1}>Smoker</option>
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Family History</label>
                  <select
                    value={vitals["Family History"]}
                    onChange={(e) => handleVitalChange("Family History", e.target.value)}
                    className="form-select"
                  >
                    <option value={0}>Negative</option>
                    <option value={1}>Positive</option>
                  </select>
                </div>
              </div>

              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label">Daily Sleep Hours</label>
                <input
                  type="number"
                  step="0.5"
                  value={vitals["Sleep Hours"]}
                  onChange={(e) => handleVitalChange("Sleep Hours", e.target.value)}
                  className="form-input"
                />
              </div>
            </div>
          </div>

          {/* Execution Button */}
          <button
            onClick={handleRunPrediction}
            disabled={predicting}
            className="btn btn-primary"
            style={{ width: "100%", padding: "0.95rem", fontSize: "1rem", boxShadow: "0 4px 18px var(--accent-glow)" }}
          >
            <Brain size={18} />
            <span>{predicting ? "Running Neural Diagnosis..." : "Execute AI Diagnostic Simulation →"}</span>
          </button>

          {/* =========================================================================
              AI RESULTS & ON-CHAIN COMMITMENT
              ========================================================================= */}
          {predictionData && (
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass-card"
              style={{ padding: "2rem", border: "1.5px solid var(--border)" }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "1.5rem" }}>
                <Sparkles size={20} color="var(--accent)" />
                <h3 style={{ fontSize: "1.35rem", fontWeight: 800 }}>Model Prediction Analysis</h3>
              </div>

              <div style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
                gap: "2rem",
                alignItems: "center"
              }}>
                {/* Visual Risk Gauge */}
                <div>
                  <RiskGauge
                    score={predictionData.confidence_score}
                    level={predictionData.risk_level}
                    prediction={predictionData.prediction}
                  />
                </div>

                {/* Recommendations */}
                <div>
                  <h4 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "0.75rem", color: "var(--text-primary)" }}>
                    Clinical Protocol Recommendations:
                  </h4>
                  {predictionData.recommendations && (
                    <ul style={{ paddingLeft: "1.2rem", fontSize: "0.88rem", color: "var(--text-secondary)", lineHeight: 1.7 }}>
                      {predictionData.recommendations.map((rec, idx) => (
                        <li key={idx} style={{ marginBottom: "0.4rem" }}>{rec}</li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>

              {/* SHAP Visualization */}
              {predictionData.shap_image && (
                <div style={{ marginTop: "1.75rem", paddingTop: "1.5rem", borderTop: "1px solid var(--border)" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem" }}>
                    <BarChart2 size={16} color="var(--accent)" />
                    <h4 style={{ fontSize: "0.95rem", fontWeight: 700 }}>Explainable AI (SHAP Feature Importance Attribution)</h4>
                  </div>
                  <img
                    src={`data:image/png;base64,${predictionData.shap_image}`}
                    alt="SHAP Feature Importance"
                    style={{ width: "100%", maxHeight: "360px", objectFit: "contain", borderRadius: "10px", background: "white", padding: "10px" }}
                  />
                </div>
              )}

              {/* Commit to Hyperledger Fabric Section */}
              <div style={{ marginTop: "2rem", paddingTop: "1.5rem", borderTop: "1px solid var(--border)" }}>
                <h4 style={{ fontSize: "1.05rem", fontWeight: 700, marginBottom: "0.75rem" }}>
                  Anchor Certified Report to Hyperledger Fabric
                </h4>
                <div className="form-group">
                  <label className="form-label">Doctor Observations & Prescription</label>
                  <textarea
                    rows={3}
                    value={doctorNotes}
                    onChange={(e) => setDoctorNotes(e.target.value)}
                    placeholder="Enter clinical assessment notes and prescription to inscribe on the ledger..."
                    className="form-textarea"
                  />
                </div>

                {inscribeSuccess && (
                  <div style={{
                    padding: "1rem",
                    borderRadius: "10px",
                    background: "var(--triage-low-bg)",
                    border: "1px solid rgba(16, 185, 129, 0.3)",
                    marginBottom: "1rem",
                    fontSize: "0.85rem"
                  }}>
                    <div style={{ fontWeight: 700, color: "var(--triage-low)", marginBottom: "4px" }}>
                      ✅ Certified Medical PDF Generated & Anchored to Ledger!
                    </div>
                    <div>EHR ID: <HashBadge hash={inscribeSuccess.recordId} /></div>
                    <div style={{ marginTop: "4px" }}>IPFS CID: <HashBadge hash={inscribeSuccess.ipfsHash} /></div>
                  </div>
                )}

                <button
                  onClick={handleCommitToBlockchain}
                  disabled={inscribing}
                  className="btn btn-primary"
                  style={{ width: "100%", padding: "0.85rem" }}
                >
                  <ShieldCheck size={18} />
                  <span>{inscribing ? "Inscribing on Hyperledger Fabric..." : "Generate Certified PDF & Commit On-Chain →"}</span>
                </button>
              </div>
            </motion.div>
          )}
        </div>
      )}

      {/* =========================================================================
          TAB 3: CERTIFIED BLOCKCHAIN HISTORY
          ========================================================================= */}
      {activeTab === "history" && (
        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          <div className="glass-card" style={{ padding: "1.5rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "0.4rem" }}>
              <ShieldCheck size={20} color="var(--accent)" />
              <h3 style={{ fontSize: "1.2rem", fontWeight: 700 }}>Certified Clinical Inscriptions</h3>
            </div>
            <p style={{ fontSize: "0.88rem", color: "var(--text-secondary)" }}>
              Historical log of medical diagnoses and cardiovascular assessments certified by Dr. {user?.username} on Hyperledger Fabric.
            </p>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "0.85rem" }}>
            {sharedRecords.length === 0 ? (
              <div className="glass-card" style={{ padding: "3rem", textAlign: "center", color: "var(--text-muted)" }}>
                <p>No certified reports in your history yet.</p>
              </div>
            ) : (
              sharedRecords.map((rec) => (
                <div key={rec.id} className="glass-card" style={{ padding: "1.25rem 1.5rem" }}>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "1rem" }}>
                    <div>
                      <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "0.25rem" }}>
                        <span style={{ fontWeight: 700, fontSize: "0.95rem" }}>
                          Patient: {rec.patientId}
                        </span>
                        <HashBadge hash={rec.id} prefixLen={8} suffixLen={4} />
                      </div>
                      <div style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>
                        IPFS CID: {rec.ipfsHash?.slice(0, 18)}... • Fabric Inscribed
                      </div>
                    </div>

                    <button
                      onClick={() => api.downloadReport(rec.id)}
                      className="btn btn-secondary"
                      style={{ padding: "0.45rem 0.85rem", fontSize: "0.8rem" }}
                    >
                      <Download size={13} />
                      <span>Download Certified PDF</span>
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
