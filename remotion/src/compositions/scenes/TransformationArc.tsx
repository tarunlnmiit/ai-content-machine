import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, FONTS, type Niche, nicheAccent, nicheGlow } from "../../styles/chronixel";

export interface TransformationArcProps extends Record<string, unknown> {
  beforeLabel: string;
  afterLabel: string;
  beforePoints: string[];
  afterPoints: string[];
  transformLabel?: string;
  niche: Niche;
}

export function TransformationArc({
  beforeLabel,
  afterLabel,
  beforePoints,
  afterPoints,
  transformLabel = "transforms to",
  niche,
}: TransformationArcProps) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const accent = nicheAccent(niche);
  const glow = nicheGlow(niche);

  const beforeIn = spring({ frame, fps, config: { damping: 18, stiffness: 75 } });
  const arrowDelay = Math.max(0, frame - 20);
  const arrowIn = spring({ frame: arrowDelay, fps, config: { damping: 20, stiffness: 90 } });
  const afterDelay = Math.max(0, frame - 30);
  const afterIn = spring({ frame: afterDelay, fps, config: { damping: 18, stiffness: 75 } });

  const beforeOpacity = interpolate(beforeIn, [0, 1], [0, 1]);
  const beforeX = interpolate(beforeIn, [0, 1], [-60, 0]);
  const afterOpacity = interpolate(afterIn, [0, 1], [0, 1]);
  const afterX = interpolate(afterIn, [0, 1], [60, 0]);
  const arrowScale = interpolate(arrowIn, [0, 1], [0, 1]);
  const arrowOpacity = interpolate(arrowIn, [0, 1], [0, 1]);

  const CHAOS_COLOR = "rgba(255,100,80,0.7)";
  const CHAOS_BORDER = "rgba(255,100,80,0.3)";

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.bg,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        gap: 0,
        fontFamily: FONTS.body,
        overflow: "hidden",
        padding: "0 60px",
      }}
    >
      {/* Ambient glow */}
      <div
        style={{
          position: "absolute",
          right: "25%",
          top: "50%",
          width: 500,
          height: 400,
          background: glow,
          borderRadius: "50%",
          filter: "blur(100px)",
          transform: "translate(50%, -50%)",
          opacity: 0.4,
          pointerEvents: "none",
        }}
      />

      {/* BEFORE panel */}
      <div
        style={{
          flex: 1,
          opacity: beforeOpacity,
          transform: `translateX(${beforeX}px)`,
          background: "rgba(255,100,80,0.05)",
          border: `1px solid ${CHAOS_BORDER}`,
          borderRadius: 20,
          padding: "40px 36px",
          maxWidth: 560,
          position: "relative",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            height: 3,
            background: CHAOS_COLOR,
            borderRadius: "20px 20px 0 0",
          }}
        />

        <div
          style={{
            color: CHAOS_COLOR,
            fontFamily: FONTS.heading,
            fontWeight: FONTS.headingWeight,
            fontSize: 28,
            marginBottom: 8,
            letterSpacing: "-0.01em",
          }}
        >
          BEFORE
        </div>
        <div
          style={{
            color: COLORS.text,
            fontFamily: FONTS.heading,
            fontWeight: FONTS.headingWeight,
            fontSize: 36,
            marginBottom: 32,
            letterSpacing: "-0.02em",
          }}
        >
          {beforeLabel}
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {beforePoints.map((pt, i) => {
            const ptDelay = Math.max(0, frame - 8 - i * 8);
            const ptIn = spring({ frame: ptDelay, fps, config: { damping: 20, stiffness: 100 } });
            const ptOp = interpolate(ptIn, [0, 1], [0, 1]);
            return (
              <div
                key={i}
                style={{ opacity: ptOp, display: "flex", alignItems: "flex-start", gap: 12 }}
              >
                <div
                  style={{
                    width: 6,
                    height: 6,
                    borderRadius: "50%",
                    background: CHAOS_COLOR,
                    flexShrink: 0,
                    marginTop: 9,
                    opacity: 0.8,
                  }}
                />
                <div
                  style={{
                    color: COLORS.textMuted,
                    fontFamily: FONTS.body,
                    fontSize: 20,
                    lineHeight: 1.5,
                  }}
                >
                  {pt}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Arrow + transform label */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "0 40px",
          opacity: arrowOpacity,
          transform: `scale(${arrowScale})`,
          flexShrink: 0,
        }}
      >
        <div
          style={{
            color: COLORS.textDim,
            fontFamily: FONTS.body,
            fontSize: 14,
            letterSpacing: "0.06em",
            textTransform: "uppercase",
            marginBottom: 12,
          }}
        >
          {transformLabel}
        </div>
        <svg width="80" height="24" viewBox="0 0 80 24" fill="none">
          <path
            d="M0 12 H64"
            stroke={accent}
            strokeWidth="2.5"
            strokeLinecap="round"
          />
          <path
            d="M60 4 L76 12 L60 20"
            stroke={accent}
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            fill="none"
          />
        </svg>
      </div>

      {/* AFTER panel */}
      <div
        style={{
          flex: 1,
          opacity: afterOpacity,
          transform: `translateX(${afterX}px)`,
          background: `${accent}0a`,
          border: `1px solid ${accent}40`,
          borderRadius: 20,
          padding: "40px 36px",
          maxWidth: 560,
          position: "relative",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            height: 3,
            background: accent,
            borderRadius: "20px 20px 0 0",
            boxShadow: `0 0 16px ${accent}`,
          }}
        />

        {/* Glow overlay */}
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

        <div
          style={{
            color: accent,
            fontFamily: FONTS.heading,
            fontWeight: FONTS.headingWeight,
            fontSize: 28,
            marginBottom: 8,
            letterSpacing: "-0.01em",
            position: "relative",
          }}
        >
          AFTER
        </div>
        <div
          style={{
            color: COLORS.text,
            fontFamily: FONTS.heading,
            fontWeight: FONTS.headingWeight,
            fontSize: 36,
            marginBottom: 32,
            letterSpacing: "-0.02em",
            position: "relative",
          }}
        >
          {afterLabel}
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 16, position: "relative" }}>
          {afterPoints.map((pt, i) => {
            const ptDelay = Math.max(0, frame - 35 - i * 8);
            const ptIn = spring({ frame: ptDelay, fps, config: { damping: 20, stiffness: 100 } });
            const ptOp = interpolate(ptIn, [0, 1], [0, 1]);
            return (
              <div
                key={i}
                style={{ opacity: ptOp, display: "flex", alignItems: "flex-start", gap: 12 }}
              >
                <div
                  style={{
                    width: 6,
                    height: 6,
                    borderRadius: "50%",
                    background: accent,
                    flexShrink: 0,
                    marginTop: 9,
                  }}
                />
                <div
                  style={{
                    color: COLORS.textMuted,
                    fontFamily: FONTS.body,
                    fontSize: 20,
                    lineHeight: 1.5,
                  }}
                >
                  {pt}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
}
