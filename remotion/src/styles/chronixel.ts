export const FONTS = {
  heading: "'Poppins', sans-serif",
  headingWeight: 800,
  mono: "'JetBrains Mono', monospace",
  body: "'Poppins', sans-serif",
  bodyWeight: 400,
  semibold: 600,
} as const;

export const NICHE_FONTS = {
  ds:     { heading: "'Space Grotesk', sans-serif", body: "'Space Grotesk', sans-serif" },
  life:   { heading: "'Lora', serif",               body: "'Nunito Sans', sans-serif" },
  poetry: { heading: "'Playfair Display', serif",   body: "'DM Sans', sans-serif" },
} as const;

export const COLORS = {
  bg: "#1E1B2E",
  surface: "rgba(255,255,255,0.05)",
  surfaceBorder: "rgba(255,255,255,0.10)",
  surfaceBorderHover: "rgba(255,255,255,0.18)",
  text: "#f0f0f2",
  textMuted: "rgba(240,240,242,0.50)",
  textDim: "rgba(240,240,242,0.30)",
  ds: {
    accent: "#6B8FA8",
    accentDark: "#3D5F75",
    glow: "rgba(107,143,168,0.20)",
    glowStrong: "rgba(107,143,168,0.40)",
    grid: "rgba(107,143,168,0.06)",
  },
  life: {
    accent: "#E8705A",
    accentDark: "#B34A38",
    glow: "rgba(232,112,90,0.20)",
    glowStrong: "rgba(232,112,90,0.40)",
    grid: "rgba(232,112,90,0.06)",
  },
  poetry: {
    accent: "#B89850",
    accentDark: "#8A6E30",
    glow: "rgba(184,152,80,0.20)",
    glowStrong: "rgba(184,152,80,0.40)",
    grid: "rgba(184,152,80,0.06)",
  },
} as const;

export const SPACING = {
  xs: 8,
  sm: 16,
  md: 24,
  lg: 40,
  xl: 64,
  xxl: 96,
} as const;

export const RADIUS = {
  sm: 8,
  md: 14,
  lg: 20,
  pill: 999,
} as const;

export const SHOW_NAMES = {
  ds: "Breath of Data Science",
  life: "Breath of Life",
  poetry: "Breath of Poetry",
} as const;

export const NICHE_CTAS = {
  ds: "Subscribe for weekly Python & data science",
  life: "Subscribe for weekly reflections",
  poetry: "Subscribe for weekly poetry",
} as const;

export type Niche = "ds" | "life" | "poetry";

export const nicheAccent = (niche: Niche): string => COLORS[niche].accent;
export const nicheAccentDark = (niche: Niche): string => COLORS[niche].accentDark;
export const nicheGlow = (niche: Niche): string => COLORS[niche].glow;
export const nicheGlowStrong = (niche: Niche): string => COLORS[niche].glowStrong;
export const nicheGrid = (niche: Niche): string => COLORS[niche].grid;
export const nicheShowName = (niche: Niche): string => SHOW_NAMES[niche];
export const nicheCTA = (niche: Niche): string => NICHE_CTAS[niche];
export const nicheFonts = (niche: Niche) => NICHE_FONTS[niche];

export const glassPanel = (alpha = 0.05): React.CSSProperties => ({
  background: `rgba(255,255,255,${alpha})`,
  border: `1px solid ${COLORS.surfaceBorder}`,
  borderRadius: RADIUS.md,
  backdropFilter: "blur(12px)",
});

export const gridOverlay = (niche: Niche): React.CSSProperties => ({
  position: "absolute",
  inset: 0,
  backgroundImage: `linear-gradient(${nicheGrid(niche)} 1px, transparent 1px), linear-gradient(90deg, ${nicheGrid(niche)} 1px, transparent 1px)`,
  backgroundSize: "80px 80px",
  pointerEvents: "none",
});

// suppress React import — Remotion environments provide it globally
import type React from "react";
