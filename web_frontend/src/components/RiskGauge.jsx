import React from "react";
import { motion } from "framer-motion";

export default function RiskGauge({ score = 0, level = "Low", prediction = "Normal" }) {
  // Handle both 0.0 - 1.0 probability and 0 - 100 percentage values
  const raw = Number(score) || 0;
  const normalizedScore = (raw > 0 && raw <= 1.0) ? raw * 100 : Math.min(Math.max(raw, 0), 100);
  
  // Calculate angle for 180 degree semi-circle: 0% = -90deg, 100% = +90deg
  const angle = (normalizedScore / 100) * 180 - 90;

  // Determine triage color
  let color = "var(--triage-low)";
  let bgGlow = "rgba(16, 185, 129, 0.2)";
  if (normalizedScore >= 70 || level.toLowerCase().includes("high")) {
    color = "var(--triage-high)";
    bgGlow = "rgba(244, 63, 94, 0.25)";
  } else if (normalizedScore >= 35 || level.toLowerCase().includes("mod")) {
    color = "var(--triage-moderate)";
    bgGlow = "rgba(245, 158, 11, 0.25)";
  }

  return (
    <div style={{
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      position: "relative",
      padding: "1rem"
    }}>
      <div style={{ position: "relative", width: "220px", height: "130px" }}>
        <svg viewBox="0 0 220 130" width="100%" height="100%">
          <defs>
            <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#10B981" />
              <stop offset="50%" stopColor="#F59E0B" />
              <stop offset="100%" stopColor="#F43F5E" />
            </linearGradient>
            <filter id="gaugeShadow" x="-20%" y="-20%" width="140%" height="140%">
              <feDropShadow dx="0" dy="2" stdDeviation="4" floodColor={color} floodOpacity="0.4" />
            </filter>
          </defs>

          {/* Background Track Arc */}
          <path
            d="M 20 110 A 90 90 0 0 1 200 110"
            fill="none"
            stroke="var(--border)"
            strokeWidth="14"
            strokeLinecap="round"
          />

          {/* Active Gradient Arc */}
          <path
            d="M 20 110 A 90 90 0 0 1 200 110"
            fill="none"
            stroke="url(#gaugeGradient)"
            strokeWidth="14"
            strokeLinecap="round"
            filter="url(#gaugeShadow)"
          />

          {/* Center Hub */}
          <circle cx="110" cy="110" r="10" fill="var(--surface-elevated)" stroke={color} strokeWidth="3" />
        </svg>

        {/* Animated Needle */}
        <motion.div
          initial={{ rotate: -90 }}
          animate={{ rotate: angle }}
          transition={{ type: "spring", stiffness: 60, damping: 15 }}
          style={{
            position: "absolute",
            bottom: "20px",
            left: "109px",
            width: "2px",
            height: "82px",
            background: color,
            boxShadow: `0 0 8px ${color}`,
            transformOrigin: "bottom center",
            borderRadius: "2px"
          }}
        />
      </div>

      {/* Central Score Display */}
      <div style={{ textAlign: "center", marginTop: "-10px" }}>
        <div style={{
          fontSize: "2.4rem",
          fontWeight: 800,
          color: "var(--text-primary)",
          letterSpacing: "-0.04em",
          lineHeight: 1
        }}>
          {Math.round(normalizedScore)}<span style={{ fontSize: "1.2rem", color: "var(--text-muted)", fontWeight: 500 }}>%</span>
        </div>
        <div style={{
          display: "inline-block",
          marginTop: "6px",
          padding: "3px 12px",
          borderRadius: "99px",
          background: bgGlow,
          color: color,
          fontSize: "0.78rem",
          fontWeight: 700,
          textTransform: "uppercase",
          letterSpacing: "0.06em",
          border: `1px solid ${color}`
        }}>
          {level} Risk • {prediction}
        </div>
      </div>
    </div>
  );
}
