import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import {
  COLORS,
  FONTS,
  type Niche,
  nicheCTA,
  nicheAccent,
  nicheGrid,
} from "../styles/chronixel";

interface OutroCardProps extends Record<string, unknown> {
  nextText: string;
  episodeTitle?: string;
  durationInFrames: number;
  niche: Niche;
}

export function OutroCard({ nextText, episodeTitle, durationInFrames, niche }: OutroCardProps) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const bgOpacity = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: "clamp" });

  // animated subscribe ring: circle stroke draws in
  const ringProgress = interpolate(frame, [0, 22], [0, 1], { extrapolateRight: "clamp" });
  const circumference = 2 * Math.PI * 28;
  const strokeDashoffset = circumference * (1 - ringProgress);

  const ringOpacity = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: "clamp" });

  // checkmark inside ring
  const checkSpring = spring({ frame: frame - 18, fps, config: { damping: 60, stiffness: 300 } });
  const checkScale = interpolate(checkSpring, [0, 1], [0, 1]);
  const checkOpacity = interpolate(frame, [18, 28], [0, 1], { extrapolateRight: "clamp" });

  const labelOpacity = interpolate(frame, [10, 25], [0, 1], { extrapolateRight: "clamp" });

  const nextSpring = spring({ frame: frame - 20, fps, config: { damping: 80, stiffness: 200 } });
  const nextOpacity = interpolate(frame, [20, 38], [0, 1], { extrapolateRight: "clamp" });
  const nextY = interpolate(nextSpring, [0, 1], [20, 0]);

  const ctaOpacity = interpolate(frame, [30, 46], [0, 1], { extrapolateRight: "clamp" });

  const outroOpacity = interpolate(frame, [durationInFrames - 12, durationInFrames], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const accent = nicheAccent(niche);
  const grid = nicheGrid(niche);
  const cta = nicheCTA(niche);

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        backgroundColor: COLORS.bg,
        opacity: bgOpacity * outroOpacity,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        position: "relative",
        overflow: "hidden",
        gap: 28,
      }}
    >
      {/* grid overlay */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage: `linear-gradient(${grid} 1px, transparent 1px), linear-gradient(90deg, ${grid} 1px, transparent 1px)`,
          backgroundSize: "80px 80px",
          pointerEvents: "none",
        }}
      />

      {/* animated subscribe ring */}
      <svg
        width={72}
        height={72}
        viewBox="0 0 64 64"
        style={{ opacity: ringOpacity, position: "relative" }}
      >
        <circle
          cx={32}
          cy={32}
          r={28}
          fill="none"
          stroke={`rgba(255,255,255,0.08)`}
          strokeWidth={2}
        />
        <circle
          cx={32}
          cy={32}
          r={28}
          fill="none"
          stroke={accent}
          strokeWidth={2.5}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          transform="rotate(-90 32 32)"
          style={{ filter: `drop-shadow(0 0 6px ${accent})` }}
        />
        {/* checkmark */}
        <path
          d="M20 32 L28 40 L44 24"
          fill="none"
          stroke={accent}
          strokeWidth={2.5}
          strokeLinecap="round"
          strokeLinejoin="round"
          opacity={checkOpacity}
          style={{ transform: `scale(${checkScale})`, transformOrigin: "32px 32px" }}
        />
      </svg>

      <div
        style={{
          opacity: labelOpacity,
          color: COLORS.textMuted,
          fontSize: 13,
          fontFamily: FONTS.body,
          fontWeight: FONTS.semibold,
          letterSpacing: "0.16em",
          textTransform: "uppercase",
        }}
      >
        Up next
      </div>

      <div
        style={{
          opacity: nextOpacity,
          transform: `translateY(${nextY}px)`,
          color: COLORS.text,
          fontSize: 38,
          fontFamily: FONTS.heading,
          fontWeight: FONTS.headingWeight,
          textAlign: "center",
          maxWidth: "60%",
          lineHeight: 1.3,
          letterSpacing: "-0.01em",
          position: "relative",
        }}
      >
        {nextText}
      </div>

      <div
        style={{
          opacity: ctaOpacity,
          color: accent,
          fontSize: 18,
          fontFamily: FONTS.body,
          fontWeight: FONTS.semibold,
          letterSpacing: "0.04em",
        }}
      >
        {cta}
      </div>
    </div>
  );
}
