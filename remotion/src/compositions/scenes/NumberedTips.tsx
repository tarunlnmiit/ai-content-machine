import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, FONTS, RADIUS, type Niche, nicheAccent, nicheGrid } from "../../styles/chronixel";

export interface Tip {
  number: number;
  headline: string;
  body?: string;
}

export interface NumberedTipsProps extends Record<string, unknown> {
  tips: Tip[];
  niche: Niche;
  title?: string;
}

export function NumberedTips({ tips, niche, title }: NumberedTipsProps) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const accent = nicheAccent(niche);
  const grid = nicheGrid(niche);

  // Title entrance
  const titleSpring = spring({ frame, fps, config: { damping: 80, stiffness: 200 } });
  const titleOpacity = interpolate(frame, [0, 16], [0, 1], { extrapolateRight: "clamp" });
  const titleY = interpolate(titleSpring, [0, 1], [20, 0]);

  // Each card staggers in at 20-frame intervals
  const staggerFrames = 20;

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

      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "0 100px",
          gap: 24,
        }}
      >
        {title && (
          <div
            style={{
              opacity: titleOpacity,
              transform: `translateY(${titleY}px)`,
              color: COLORS.textMuted,
              fontSize: 18,
              fontFamily: FONTS.body,
              fontWeight: FONTS.semibold,
              letterSpacing: "0.14em",
              textTransform: "uppercase",
              marginBottom: 8,
            }}
          >
            {title}
          </div>
        )}

        {tips.map((tip, i) => {
          const delay = (i + 1) * staggerFrames;
          const s = spring({
            frame: frame - delay,
            fps,
            config: { damping: 70, stiffness: 220 },
          });
          const opacity = interpolate(s, [0, 1], [0, 1]);
          const x = interpolate(s, [0, 1], [-40, 0]);

          return (
            <div
              key={i}
              style={{
                opacity,
                transform: `translateX(${x}px)`,
                display: "flex",
                alignItems: "flex-start",
                gap: 24,
                width: "100%",
                background: COLORS.surface,
                border: `1px solid ${COLORS.surfaceBorder}`,
                borderRadius: RADIUS.md,
                padding: "24px 32px",
              }}
            >
              {/* Number badge */}
              <div
                style={{
                  flexShrink: 0,
                  width: 52,
                  height: 52,
                  borderRadius: "50%",
                  backgroundColor: accent,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: COLORS.bg,
                  fontSize: 22,
                  fontFamily: FONTS.heading,
                  fontWeight: FONTS.headingWeight,
                  boxShadow: `0 0 16px ${accent}55`,
                }}
              >
                {tip.number}
              </div>

              <div style={{ flex: 1 }}>
                <div
                  style={{
                    color: COLORS.text,
                    fontSize: 34,
                    fontFamily: FONTS.heading,
                    fontWeight: FONTS.headingWeight,
                    lineHeight: 1.2,
                    letterSpacing: "-0.01em",
                  }}
                >
                  {tip.headline}
                </div>
                {tip.body && (
                  <div
                    style={{
                      color: COLORS.textMuted,
                      fontSize: 22,
                      fontFamily: FONTS.body,
                      fontWeight: FONTS.bodyWeight,
                      lineHeight: 1.5,
                      marginTop: 8,
                    }}
                  >
                    {tip.body}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
}
