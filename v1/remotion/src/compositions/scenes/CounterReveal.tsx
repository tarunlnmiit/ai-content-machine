import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, FONTS, RADIUS, type Niche, nicheAccent, nicheGlow, nicheGrid } from "../../styles/chronixel";

export interface CounterRevealProps extends Record<string, unknown> {
  value: number;
  label: string;
  niche: Niche;
  prefix?: string;
  suffix?: string;
}

export function CounterReveal({
  value,
  label,
  niche,
  prefix = "",
  suffix = "",
}: CounterRevealProps) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const accent = nicheAccent(niche);
  const glow = nicheGlow(niche);
  const grid = nicheGrid(niche);

  // Ease-out count-up over first ~2s
  const countProgress = interpolate(frame, [0, Math.round(fps * 2)], [0, 1], {
    extrapolateRight: "clamp",
  });
  const eased = 1 - Math.pow(1 - countProgress, 3);
  const displayValue = Math.round(eased * value);

  const labelOpacity = interpolate(frame, [Math.round(fps * 2), Math.round(fps * 2.5)], [0, 1], {
    extrapolateRight: "clamp",
  });
  const labelY = interpolate(frame, [Math.round(fps * 2), Math.round(fps * 2.5)], [16, 0], {
    extrapolateRight: "clamp",
  });

  const lineWidth = interpolate(
    frame,
    [Math.round(fps * 2.5), Math.round(fps * 3)],
    [0, 200],
    { extrapolateRight: "clamp" }
  );

  const glowScale = interpolate(frame, [0, 12], [0.5, 1], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg, overflow: "hidden" }}>
      <AbsoluteFill
        style={{
          backgroundImage: `linear-gradient(${grid} 1px, transparent 1px), linear-gradient(90deg, ${grid} 1px, transparent 1px)`,
          backgroundSize: "80px 80px",
          pointerEvents: "none",
        }}
      />
      {/* Radial glow behind counter */}
      <div
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: `translate(-50%, -50%) scale(${glowScale})`,
          width: 700,
          height: 700,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${glow} 0%, transparent 65%)`,
          pointerEvents: "none",
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: 20,
        }}
      >
        {/* Big number */}
        <div
          style={{
            fontSize: 160,
            fontFamily: FONTS.heading,
            fontWeight: FONTS.headingWeight,
            color: accent,
            letterSpacing: "-0.04em",
            lineHeight: 1,
          }}
        >
          {prefix}
          {displayValue.toLocaleString()}
          {suffix}
        </div>
        {/* Accent rule */}
        <div
          style={{
            width: lineWidth,
            height: 3,
            backgroundColor: accent,
            borderRadius: RADIUS.pill,
          }}
        />
        {/* Label */}
        <div
          style={{
            opacity: labelOpacity,
            transform: `translateY(${labelY}px)`,
            fontSize: 32,
            fontFamily: FONTS.body,
            fontWeight: FONTS.semibold,
            color: COLORS.textMuted,
            letterSpacing: "0.08em",
            textTransform: "uppercase",
            textAlign: "center",
            maxWidth: 800,
            padding: "0 80px",
          }}
        >
          {label}
        </div>
      </div>
    </AbsoluteFill>
  );
}
