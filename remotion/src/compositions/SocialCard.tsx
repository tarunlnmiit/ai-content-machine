import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import {
  COLORS,
  FONTS,
  RADIUS,
  type Niche,
  nicheAccent,
  nicheGrid,
  nicheGlow,
} from "../styles/chronixel";

export interface SocialCard1x1Props extends Record<string, unknown> {
  headline: string;
  subtext?: string;
  niche: Niche;
  animationStyle?: "slide-in" | "reveal" | "build";
}

export interface SocialCard9x16Props extends SocialCard1x1Props {}

type AnimStyle = "slide-in" | "reveal" | "build";

function useSocialCardAnim(frame: number, fps: number, style: AnimStyle) {
  if (style === "slide-in") {
    const s = spring({ frame, fps, config: { damping: 70, stiffness: 180 } });
    return {
      panelOpacity: interpolate(frame, [0, 12], [0, 1], { extrapolateRight: "clamp" }),
      panelY: interpolate(s, [0, 1], [60, 0]),
      headlineOpacity: interpolate(frame, [10, 26], [0, 1], { extrapolateRight: "clamp" }),
      headlineY: interpolate(spring({ frame: frame - 10, fps, config: { damping: 80, stiffness: 200 } }), [0, 1], [24, 0]),
      subtextOpacity: interpolate(frame, [22, 38], [0, 1], { extrapolateRight: "clamp" }),
    };
  }
  if (style === "reveal") {
    return {
      panelOpacity: interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" }),
      panelY: 0,
      headlineOpacity: interpolate(frame, [14, 30], [0, 1], { extrapolateRight: "clamp" }),
      headlineY: 0,
      subtextOpacity: interpolate(frame, [24, 40], [0, 1], { extrapolateRight: "clamp" }),
    };
  }
  // build
  const s = spring({ frame, fps, config: { damping: 60, stiffness: 220 } });
  return {
    panelOpacity: 1,
    panelY: 0,
    headlineOpacity: interpolate(s, [0, 1], [0, 1]),
    headlineY: interpolate(s, [0, 1], [30, 0]),
    subtextOpacity: interpolate(frame, [20, 36], [0, 1], { extrapolateRight: "clamp" }),
  };
}

function SocialCardBase({
  headline,
  subtext,
  niche,
  animationStyle = "slide-in",
  width,
  height,
}: SocialCard1x1Props & { width: number; height: number }) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { panelOpacity, panelY, headlineOpacity, headlineY, subtextOpacity } =
    useSocialCardAnim(frame, fps, animationStyle);

  const accent = nicheAccent(niche);
  const grid = nicheGrid(niche);
  const glow = nicheGlow(niche);
  const isPortrait = height > width;

  // Subtle ambient particle dots — static positions seeded deterministically
  const dots = Array.from({ length: 18 }, (_, i) => ({
    x: ((i * 137.5) % 100),
    y: ((i * 97.3) % 100),
    r: 1.5 + (i % 3),
    o: 0.06 + (i % 4) * 0.03,
  }));

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg, overflow: "hidden" }}>
      {/* Grid */}
      <AbsoluteFill
        style={{
          backgroundImage: `linear-gradient(${grid} 1px, transparent 1px), linear-gradient(90deg, ${grid} 1px, transparent 1px)`,
          backgroundSize: "80px 80px",
          pointerEvents: "none",
        }}
      />

      {/* Ambient dots */}
      <AbsoluteFill style={{ pointerEvents: "none" }}>
        <svg width={width} height={height} style={{ position: "absolute" }}>
          {dots.map((d, i) => (
            <circle
              key={i}
              cx={`${d.x}%`}
              cy={`${d.y}%`}
              r={d.r}
              fill={accent}
              opacity={d.o}
            />
          ))}
        </svg>
      </AbsoluteFill>

      {/* Glow bloom */}
      <div
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          width: "60%",
          height: "60%",
          background: `radial-gradient(ellipse, ${glow} 0%, transparent 70%)`,
          pointerEvents: "none",
        }}
      />

      {/* Main glass panel */}
      <div
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: `translate(-50%, calc(-50% + ${panelY}px))`,
          opacity: panelOpacity,
          width: isPortrait ? "82%" : "76%",
          background: COLORS.surface,
          border: `1px solid ${COLORS.surfaceBorder}`,
          borderRadius: RADIUS.lg,
          padding: isPortrait ? "56px 48px" : "48px 56px",
        }}
      >
        {/* Accent top bar */}
        <div
          style={{
            width: 56,
            height: 3,
            backgroundColor: accent,
            borderRadius: 2,
            marginBottom: 28,
            boxShadow: `0 0 10px ${accent}`,
          }}
        />

        <div
          style={{
            opacity: headlineOpacity,
            transform: `translateY(${headlineY}px)`,
            color: COLORS.text,
            fontSize: isPortrait ? 52 : 46,
            fontFamily: FONTS.heading,
            fontWeight: FONTS.headingWeight,
            lineHeight: 1.2,
            letterSpacing: "-0.015em",
            marginBottom: subtext ? 20 : 0,
          }}
        >
          {headline}
        </div>

        {subtext && (
          <div
            style={{
              opacity: subtextOpacity,
              color: COLORS.textMuted,
              fontSize: isPortrait ? 26 : 22,
              fontFamily: FONTS.body,
              fontWeight: FONTS.bodyWeight,
              lineHeight: 1.5,
              marginTop: 16,
            }}
          >
            {subtext}
          </div>
        )}

        {/* Bottom accent line */}
        <div
          style={{
            marginTop: 32,
            height: 1,
            background: `linear-gradient(to right, ${accent}, transparent)`,
            opacity: 0.4,
          }}
        />
      </div>
    </AbsoluteFill>
  );
}

export function SocialCard1x1(props: SocialCard1x1Props) {
  return <SocialCardBase {...props} width={1080} height={1080} />;
}

export function SocialCard9x16(props: SocialCard9x16Props) {
  return <SocialCardBase {...props} width={1080} height={1920} />;
}
