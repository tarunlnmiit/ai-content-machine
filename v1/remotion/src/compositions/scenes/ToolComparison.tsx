import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, FONTS, type Niche, nicheAccent, nicheGlow } from "../../styles/chronixel";

export interface ComparisonSide {
  label: string;
  points: string[];
  badge?: string;
}

export interface ToolComparisonProps extends Record<string, unknown> {
  leftSide: ComparisonSide;
  rightSide: ComparisonSide;
  niche: Niche;
  vsLabel?: string;
}

export function ToolComparison({
  leftSide,
  rightSide,
  niche,
  vsLabel = "VS",
}: ToolComparisonProps) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const accent = nicheAccent(niche);
  const glow = nicheGlow(niche);

  const leftIn = spring({ frame, fps, config: { damping: 18, stiffness: 70 } });
  const rightDelay = Math.max(0, frame - 10);
  const rightIn = spring({ frame: rightDelay, fps, config: { damping: 18, stiffness: 70 } });

  const dividerDelay = Math.max(0, frame - 8);
  const dividerIn = spring({ frame: dividerDelay, fps, config: { damping: 16, stiffness: 80 } });

  const leftX = interpolate(leftIn, [0, 1], [-80, 0]);
  const rightX = interpolate(rightIn, [0, 1], [80, 0]);
  const opacity = interpolate(leftIn, [0, 1], [0, 1]);
  const dividerH = interpolate(dividerIn, [0, 1], [0, 1]);

  const maxPoints = Math.max(leftSide.points.length, rightSide.points.length);
  const panelH = 120 + maxPoints * 60 + 40;

  function SidePanel({
    side,
    align,
    x,
    highlighted,
  }: {
    side: ComparisonSide;
    align: "left" | "right";
    x: number;
    highlighted: boolean;
  }) {
    return (
      <div
        style={{
          flex: 1,
          opacity,
          transform: `translateX(${x}px)`,
          background: highlighted ? `rgba(255,255,255,0.07)` : COLORS.surface,
          border: `1px solid ${highlighted ? accent : COLORS.surfaceBorder}`,
          borderRadius: 20,
          padding: "40px 36px",
          display: "flex",
          flexDirection: "column",
          gap: 20,
          position: "relative",
          overflow: "hidden",
          height: panelH,
        }}
      >
        {/* Top glow for highlighted */}
        {highlighted && (
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              height: 100,
              background: `linear-gradient(180deg, ${glow} 0%, transparent 100%)`,
              pointerEvents: "none",
            }}
          />
        )}

        {/* Label */}
        <div
          style={{
            fontFamily: FONTS.heading,
            fontWeight: FONTS.headingWeight,
            fontSize: 32,
            color: highlighted ? accent : COLORS.text,
            letterSpacing: "-0.01em",
            position: "relative",
          }}
        >
          {side.label}
          {side.badge && (
            <span
              style={{
                marginLeft: 12,
                background: accent,
                color: "#000",
                borderRadius: 6,
                padding: "2px 10px",
                fontSize: 13,
                fontWeight: FONTS.semibold,
                verticalAlign: "middle",
                letterSpacing: "0.04em",
              }}
            >
              {side.badge}
            </span>
          )}
        </div>

        {/* Divider */}
        <div
          style={{
            height: 1,
            background: highlighted ? accent : COLORS.surfaceBorder,
            opacity: highlighted ? 0.6 : 1,
            borderRadius: 1,
          }}
        />

        {/* Points */}
        <div style={{ display: "flex", flexDirection: "column", gap: 14, position: "relative" }}>
          {side.points.map((point, i) => {
            const ptDelay = Math.max(0, frame - 18 - i * 8);
            const ptIn = spring({ frame: ptDelay, fps, config: { damping: 18, stiffness: 100 } });
            const ptOpacity = interpolate(ptIn, [0, 1], [0, 1]);
            const ptX = interpolate(ptIn, [0, 1], [align === "left" ? -16 : 16, 0]);

            return (
              <div
                key={i}
                style={{
                  opacity: ptOpacity,
                  transform: `translateX(${ptX}px)`,
                  display: "flex",
                  alignItems: "flex-start",
                  gap: 12,
                }}
              >
                <div
                  style={{
                    width: 8,
                    height: 8,
                    borderRadius: "50%",
                    background: highlighted ? accent : COLORS.textMuted,
                    flexShrink: 0,
                    marginTop: 8,
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
                  {point}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.bg,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "0 80px",
        fontFamily: FONTS.body,
        overflow: "hidden",
      }}
    >
      {/* Background glow */}
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "50%",
          width: 600,
          height: 400,
          background: glow,
          borderRadius: "50%",
          filter: "blur(120px)",
          transform: "translate(-50%,-50%)",
          opacity: 0.35,
          pointerEvents: "none",
        }}
      />

      <div
        style={{
          display: "flex",
          alignItems: "stretch",
          gap: 0,
          width: "100%",
          maxWidth: 1600,
          position: "relative",
        }}
      >
        <SidePanel side={leftSide} align="left" x={leftX} highlighted={false} />

        {/* VS divider */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            width: 80,
            flexShrink: 0,
            position: "relative",
          }}
        >
          <div
            style={{
              width: 2,
              height: `${dividerH * 100}%`,
              background: `linear-gradient(180deg, transparent, ${accent}, transparent)`,
              position: "absolute",
            }}
          />
          <div
            style={{
              opacity: interpolate(dividerIn, [0, 1], [0, 1]),
              background: COLORS.bg,
              border: `2px solid ${accent}`,
              borderRadius: "50%",
              width: 48,
              height: 48,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: accent,
              fontFamily: FONTS.heading,
              fontWeight: FONTS.headingWeight,
              fontSize: 14,
              letterSpacing: "0.06em",
              boxShadow: `0 0 20px ${glow}`,
              position: "relative",
              zIndex: 1,
            }}
          >
            {vsLabel}
          </div>
        </div>

        <SidePanel side={rightSide} align="right" x={rightX} highlighted />
      </div>
    </AbsoluteFill>
  );
}
