import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, FONTS, type Niche, nicheAccent, nicheGlow, nicheGrid } from "../../styles/chronixel";

export interface ConceptCard {
  term: string;
  definition: string;
  icon?: string;
}

export interface ConceptExplainerProps extends Record<string, unknown> {
  headline: string;
  cards: ConceptCard[];
  niche: Niche;
}

function pr(seed: number): number {
  const x = Math.sin(seed + 1) * 43758.5453;
  return x - Math.floor(x);
}

export function ConceptExplainer({ headline, cards, niche }: ConceptExplainerProps) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const accent = nicheAccent(niche);
  const glow = nicheGlow(niche);
  const grid = nicheGrid(niche);

  const headlineIn = spring({ frame, fps, config: { damping: 20, stiffness: 80 } });
  const headlineOpacity = interpolate(headlineIn, [0, 1], [0, 1]);
  const headlineY = interpolate(headlineIn, [0, 1], [-20, 0]);

  const visibleCards = Math.min(cards.length, 3);
  const cardWidth = visibleCards === 1 ? 600 : visibleCards === 2 ? 500 : 380;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.bg,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 60,
        fontFamily: FONTS.body,
        overflow: "hidden",
      }}
    >
      {/* Grid overlay */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage: `
            linear-gradient(${grid} 1px, transparent 1px),
            linear-gradient(90deg, ${grid} 1px, transparent 1px)
          `,
          backgroundSize: "80px 80px",
          pointerEvents: "none",
        }}
      />

      {/* Ambient glow blobs */}
      {[0, 1].map((i) => (
        <div
          key={i}
          style={{
            position: "absolute",
            left: `${20 + i * 50}%`,
            top: `${30 + i * 30}%`,
            width: 400,
            height: 300,
            background: glow,
            borderRadius: "50%",
            filter: "blur(80px)",
            transform: "translate(-50%,-50%)",
            pointerEvents: "none",
            opacity: 0.5,
          }}
        />
      ))}

      {/* Headline */}
      <div
        style={{
          opacity: headlineOpacity,
          transform: `translateY(${headlineY}px)`,
          textAlign: "center",
          position: "relative",
          zIndex: 1,
        }}
      >
        <div
          style={{
            color: COLORS.text,
            fontFamily: FONTS.heading,
            fontWeight: FONTS.headingWeight,
            fontSize: 52,
            letterSpacing: "-0.02em",
          }}
        >
          {headline}
        </div>
        <div
          style={{
            width: 60,
            height: 3,
            background: accent,
            borderRadius: 2,
            margin: "16px auto 0",
            boxShadow: `0 0 16px ${accent}`,
          }}
        />
      </div>

      {/* Cards */}
      <div
        style={{
          display: "flex",
          gap: 24,
          alignItems: "stretch",
          justifyContent: "center",
          position: "relative",
          zIndex: 1,
        }}
      >
        {cards.slice(0, 3).map((card, i) => {
          const delay = Math.max(0, frame - 15 - i * 12);
          const cardIn = spring({ frame: delay, fps, config: { damping: 18, stiffness: 85 } });
          const opacity = interpolate(cardIn, [0, 1], [0, 1]);
          const y = interpolate(cardIn, [0, 1], [40, 0]);

          return (
            <div
              key={i}
              style={{
                opacity,
                transform: `translateY(${y}px)`,
                width: cardWidth,
                background: COLORS.surface,
                border: `1px solid ${COLORS.surfaceBorder}`,
                borderTop: `3px solid ${accent}`,
                borderRadius: 20,
                padding: "36px 32px",
                display: "flex",
                flexDirection: "column",
                gap: 16,
                position: "relative",
                overflow: "hidden",
              }}
            >
              {/* Inner glow */}
              <div
                style={{
                  position: "absolute",
                  top: 0,
                  left: 0,
                  right: 0,
                  height: 80,
                  background: `linear-gradient(180deg, ${glow} 0%, transparent 100%)`,
                  pointerEvents: "none",
                }}
              />

              {/* Icon or number badge */}
              <div
                style={{
                  width: 52,
                  height: 52,
                  borderRadius: 14,
                  background: glow,
                  border: `1px solid ${accent}`,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: accent,
                  fontFamily: FONTS.heading,
                  fontWeight: FONTS.headingWeight,
                  fontSize: card.icon ? 28 : 24,
                  flexShrink: 0,
                }}
              >
                {card.icon ?? `0${i + 1}`}
              </div>

              {/* Term */}
              <div
                style={{
                  color: accent,
                  fontFamily: FONTS.heading,
                  fontWeight: FONTS.headingWeight,
                  fontSize: 26,
                  letterSpacing: "-0.01em",
                }}
              >
                {card.term}
              </div>

              {/* Definition */}
              <div
                style={{
                  color: COLORS.textMuted,
                  fontFamily: FONTS.body,
                  fontWeight: FONTS.bodyWeight,
                  fontSize: 18,
                  lineHeight: 1.6,
                }}
              >
                {card.definition}
              </div>

              {/* Deterministic dot accent */}
              {Array.from({ length: 6 }, (_, j) => (
                <div
                  key={j}
                  style={{
                    position: "absolute",
                    right: 16 + pr(i * 6 + j) * 60,
                    bottom: 16 + pr(i * 6 + j + 1) * 40,
                    width: 3 + pr(i * 6 + j + 2) * 3,
                    height: 3 + pr(i * 6 + j + 2) * 3,
                    borderRadius: "50%",
                    background: accent,
                    opacity: 0.15 + pr(i * 6 + j + 3) * 0.2,
                    pointerEvents: "none",
                  }}
                />
              ))}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
}
