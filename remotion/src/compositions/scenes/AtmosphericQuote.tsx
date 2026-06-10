import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, FONTS, type Niche, nicheAccent, nicheGlow } from "../../styles/chronixel";

export interface AtmosphericQuoteProps extends Record<string, unknown> {
  quote: string;
  attribution?: string;
  niche: Niche;
}

function pr(seed: number): number {
  const x = Math.sin(seed + 1) * 43758.5453;
  return x - Math.floor(x);
}

export function AtmosphericQuote({ quote, attribution, niche }: AtmosphericQuoteProps) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const accent = nicheAccent(niche);
  const glow = nicheGlow(niche);

  const bgOpacity = interpolate(frame, [0, 24], [0, 1], { extrapolateRight: "clamp" });

  // Accent bar sweeps in from left
  const barScale = spring({ frame: frame - 8, fps, config: { damping: 80, stiffness: 200 } });
  const barX = interpolate(barScale, [0, 1], [-100, 0]);

  // Quote fades and rises
  const quoteSpring = spring({ frame: frame - 18, fps, config: { damping: 70, stiffness: 160 } });
  const quoteOpacity = interpolate(frame, [18, 38], [0, 1], { extrapolateRight: "clamp" });
  const quoteY = interpolate(quoteSpring, [0, 1], [30, 0]);

  // Attribution follows
  const attrOpacity = interpolate(frame, [36, 52], [0, 1], { extrapolateRight: "clamp" });

  // Ambient particles
  const particles = Array.from({ length: 20 }, (_, i) => ({
    cx: pr(i * 7) * 100,
    cy: pr(i * 7 + 1) * 100,
    r: 0.8 + pr(i * 7 + 2) * 1.5,
    opacity: (0.1 + pr(i * 7 + 3) * 0.2) * bgOpacity,
  }));

  return (
    <AbsoluteFill style={{ backgroundColor: "#06040f", overflow: "hidden" }}>
      {/* Ambient glow */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse 60% 60% at 50% 50%, ${glow} 0%, transparent 70%)`,
          opacity: bgOpacity,
          pointerEvents: "none",
        }}
      />

      {/* Particles */}
      <svg
        width="100%"
        height="100%"
        viewBox="0 0 100 56.25"
        preserveAspectRatio="xMidYMid slice"
        style={{ position: "absolute", inset: 0 }}
      >
        {particles.map((p, i) => (
          <circle key={i} cx={p.cx} cy={p.cy * 0.5625} r={p.r} fill={accent} opacity={p.opacity} />
        ))}
      </svg>

      {/* Content */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "0 140px",
          opacity: bgOpacity,
        }}
      >
        {/* Top accent bar */}
        <div
          style={{
            width: 64,
            height: 3,
            backgroundColor: accent,
            borderRadius: 2,
            transform: `translateX(${barX}%)`,
            marginBottom: 48,
            boxShadow: `0 0 14px ${accent}`,
          }}
        />

        {/* Quote text */}
        <div
          style={{
            opacity: quoteOpacity,
            transform: `translateY(${quoteY}px)`,
            color: COLORS.text,
            fontSize: 72,
            fontFamily: FONTS.heading,
            fontWeight: FONTS.headingWeight,
            lineHeight: 1.25,
            letterSpacing: "-0.015em",
            textAlign: "center",
            maxWidth: "85%",
          }}
        >
          {quote}
        </div>

        {/* Attribution */}
        {attribution && (
          <div
            style={{
              opacity: attrOpacity,
              marginTop: 40,
              color: accent,
              fontSize: 22,
              fontFamily: FONTS.body,
              fontWeight: FONTS.semibold,
              letterSpacing: "0.10em",
              textTransform: "uppercase",
            }}
          >
            — {attribution}
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
}
