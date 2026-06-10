import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, FONTS, type Niche, nicheAccent, nicheGlow } from "../../styles/chronixel";

export interface LineRevealProps extends Record<string, unknown> {
  lines: string[];
  attribution?: string;
  niche: Niche;
  staggerMs?: number;
  fontSize?: number;
}

function pr(seed: number): number {
  const x = Math.sin(seed + 1) * 43758.5453;
  return x - Math.floor(x);
}

export function LineReveal({
  lines,
  attribution,
  niche,
  staggerMs = 400,
  fontSize = 52,
}: LineRevealProps) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const accent = nicheAccent(niche);
  const glow = nicheGlow(niche);

  const staggerFrames = (staggerMs / 1000) * fps;

  const particles = Array.from({ length: 30 }, (_, i) => {
    const baseX = pr(i * 7) * 100;
    const baseY = pr(i * 7 + 1) * 100;
    const driftY = -(frame / fps) * (0.4 + pr(i * 7 + 2) * 0.6);
    return {
      cx: baseX + Math.sin((frame / fps) * 0.4 + i * 0.9) * 1.2,
      cy: ((baseY + driftY) % 100 + 100) % 100,
      r: 0.4 + pr(i * 7 + 3) * 0.6,
      opacity: (0.15 + 0.25 * Math.sin((frame / fps) * (0.8 + pr(i * 7 + 4)) + i)) * 0.6,
    };
  });

  const totalLines = lines.length;
  const lineHeight = fontSize * 1.8;
  const totalH = totalLines * lineHeight + (attribution ? 80 : 0);
  const startY = (1080 - totalH) / 2;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#06040f",
        fontFamily: FONTS.body,
        overflow: "hidden",
      }}
    >
      {/* Ambient particles */}
      <svg
        style={{ position: "absolute", inset: 0 }}
        width="100%"
        height="100%"
        viewBox="0 0 100 56.25"
        preserveAspectRatio="xMidYMid slice"
      >
        {particles.map((p, i) => (
          <circle
            key={i}
            cx={p.cx}
            cy={p.cy * 0.5625}
            r={p.r}
            fill={accent}
            opacity={p.opacity}
          />
        ))}
      </svg>

      {/* Center glow bloom */}
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "50%",
          width: 600,
          height: 400,
          background: glow,
          borderRadius: "50%",
          filter: "blur(100px)",
          transform: "translate(-50%,-50%)",
          opacity: 0.25,
          pointerEvents: "none",
        }}
      />

      {/* Lines container */}
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: startY,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 0,
          padding: "0 120px",
        }}
      >
        {lines.map((line, i) => {
          const delay = Math.max(0, frame - i * staggerFrames);
          const lineIn = spring({ frame: delay, fps, config: { damping: 22, stiffness: 60 } });

          const lineOpacity = interpolate(lineIn, [0, 1], [0, 1]);
          const lineY = interpolate(lineIn, [0, 1], [24, 0]);

          const isLast = i === lines.length - 1;
          const isFirst = i === 0;

          return (
            <div
              key={i}
              style={{
                height: lineHeight,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                opacity: lineOpacity,
                transform: `translateY(${lineY}px)`,
                position: "relative",
                width: "100%",
              }}
            >
              {/* Accent bar on first line */}
              {isFirst && (
                <div
                  style={{
                    position: "absolute",
                    left: "50%",
                    top: -6,
                    transform: "translateX(-50%)",
                    width: 40,
                    height: 3,
                    background: accent,
                    borderRadius: 2,
                    boxShadow: `0 0 10px ${accent}`,
                  }}
                />
              )}

              <div
                style={{
                  color: isLast ? COLORS.textMuted : COLORS.text,
                  fontFamily: FONTS.heading,
                  fontWeight: isLast ? FONTS.semibold : FONTS.headingWeight,
                  fontSize: isLast ? fontSize * 0.88 : fontSize,
                  letterSpacing: "-0.01em",
                  textAlign: "center",
                  fontStyle: isLast ? "italic" : "normal",
                }}
              >
                {line}
              </div>

              {/* Accent bar on last content line */}
              {isLast && !attribution && (
                <div
                  style={{
                    position: "absolute",
                    left: "50%",
                    bottom: -6,
                    transform: "translateX(-50%)",
                    width: 40,
                    height: 3,
                    background: accent,
                    borderRadius: 2,
                    boxShadow: `0 0 10px ${accent}`,
                  }}
                />
              )}
            </div>
          );
        })}

        {/* Attribution */}
        {attribution && (
          <div
            style={{
              height: 80,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: 16,
              width: "100%",
            }}
          >
            {(() => {
              const delay = Math.max(0, frame - lines.length * staggerFrames);
              const attrIn = spring({ frame: delay, fps, config: { damping: 20, stiffness: 70 } });
              const attrOp = interpolate(attrIn, [0, 1], [0, 1]);

              return (
                <div
                  style={{
                    opacity: attrOp,
                    display: "flex",
                    alignItems: "center",
                    gap: 16,
                  }}
                >
                  <div
                    style={{
                      width: 32,
                      height: 1,
                      background: accent,
                      opacity: 0.7,
                    }}
                  />
                  <div
                    style={{
                      color: accent,
                      fontFamily: FONTS.body,
                      fontWeight: FONTS.semibold,
                      fontSize: 20,
                      letterSpacing: "0.04em",
                    }}
                  >
                    {attribution}
                  </div>
                  <div
                    style={{
                      width: 32,
                      height: 1,
                      background: accent,
                      opacity: 0.7,
                    }}
                  />
                </div>
              );
            })()}
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
}
