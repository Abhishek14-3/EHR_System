import React from "react";

/**
 * Mathematical Graph Paper Background
 * - Clean, classic square grid (32px minor squares)
 * - Subtle major unit grid (160px = 5x5 square blocks) for authentic engineering graph paper
 * - Ultra-subtle paper texture
 * - 100% non-interactive, fixed behind all content
 */
export default function TechnicalBackground() {
  return (
    <div
      aria-hidden="true"
      style={{
        position: "fixed",
        inset: 0,
        zIndex: -1,
        pointerEvents: "none",
        overflow: "hidden",
        backgroundColor: "var(--bg)",
        transition: "background-color 0.3s ease"
      }}
    >
      {/* 1. Subtle Paper Grain Texture Layer */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          opacity: "var(--noise-opacity, 0.018)",
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
          backgroundRepeat: "repeat",
          mixBlendMode: "overlay"
        }}
      />

      {/* 2. Mathematical Graph Paper Square Grid */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage: `
            linear-gradient(to right, var(--graph-major) 1px, transparent 1px),
            linear-gradient(to bottom, var(--graph-major) 1px, transparent 1px),
            linear-gradient(to right, var(--graph-minor) 1px, transparent 1px),
            linear-gradient(to bottom, var(--graph-minor) 1px, transparent 1px)
          `,
          backgroundSize: `
            160px 160px,
            160px 160px,
            32px 32px,
            32px 32px
          `,
          backgroundPosition: "-1px -1px"
        }}
      />
    </div>
  );
}
