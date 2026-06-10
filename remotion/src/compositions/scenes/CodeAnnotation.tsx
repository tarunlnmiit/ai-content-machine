import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, FONTS, type Niche, nicheAccent, nicheGlow } from "../../styles/chronixel";

export interface CodeAnnotationProps extends Record<string, unknown> {
  code: string[];
  highlightLine: number;
  annotationText: string;
  language?: string;
  niche: Niche;
  fontSize?: number;
}

export function CodeAnnotation({
  code,
  highlightLine,
  annotationText,
  language = "python",
  niche,
  fontSize = 22,
}: CodeAnnotationProps) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const accent = nicheAccent(niche);
  const glow = nicheGlow(niche);

  const blockIn = spring({ frame, fps, config: { damping: 18, stiffness: 80 } });
  const annotationDelay = Math.max(0, frame - 20);
  const annotationIn = spring({ frame: annotationDelay, fps, config: { damping: 16, stiffness: 90 } });

  const codeOpacity = interpolate(blockIn, [0, 1], [0, 1]);
  const codeY = interpolate(blockIn, [0, 1], [30, 0]);

  const annotationOpacity = interpolate(annotationIn, [0, 1], [0, 1]);
  const annotationX = interpolate(annotationIn, [0, 1], [-20, 0]);

  const lineH = fontSize * 1.7;
  const padV = 32;
  const padH = 40;
  const blockH = code.length * lineH + padV * 2;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.bg,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontFamily: FONTS.body,
      }}
    >
      {/* Background glow at highlight line */}
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: `calc(50% - ${blockH / 2}px + ${padV + highlightLine * lineH}px)`,
          transform: "translateX(-50%)",
          width: 900,
          height: lineH,
          background: glow,
          filter: "blur(24px)",
          opacity: annotationOpacity,
          pointerEvents: "none",
        }}
      />

      {/* Code block */}
      <div
        style={{
          opacity: codeOpacity,
          transform: `translateY(${codeY}px)`,
          background: COLORS.surface,
          border: `1px solid ${COLORS.surfaceBorder}`,
          borderRadius: 16,
          padding: `${padV}px ${padH}px`,
          minWidth: 800,
          maxWidth: 900,
          position: "relative",
        }}
      >
        {/* Language badge */}
        <div
          style={{
            position: "absolute",
            top: -1,
            right: 24,
            background: accent,
            color: "#000",
            fontSize: 12,
            fontWeight: FONTS.semibold,
            padding: "3px 12px",
            borderBottomLeftRadius: 8,
            borderBottomRightRadius: 8,
            letterSpacing: "0.06em",
            textTransform: "uppercase",
          }}
        >
          {language}
        </div>

        {/* Code lines */}
        {code.map((line, i) => {
          const isHighlighted = i === highlightLine;
          return (
            <div
              key={i}
              style={{
                height: lineH,
                display: "flex",
                alignItems: "center",
                paddingLeft: 8,
                borderRadius: 6,
                background: isHighlighted
                  ? `rgba(255,255,255,0.06)`
                  : "transparent",
                borderLeft: isHighlighted
                  ? `3px solid ${accent}`
                  : "3px solid transparent",
                transition: "background 0.2s",
              }}
            >
              {/* Line number */}
              <span
                style={{
                  color: COLORS.textDim,
                  fontFamily: FONTS.mono,
                  fontSize: fontSize * 0.85,
                  width: 32,
                  textAlign: "right",
                  marginRight: 20,
                  userSelect: "none",
                  flexShrink: 0,
                }}
              >
                {i + 1}
              </span>
              {/* Code text */}
              <span
                style={{
                  fontFamily: FONTS.mono,
                  fontSize,
                  color: isHighlighted ? COLORS.text : COLORS.textMuted,
                  whiteSpace: "pre",
                }}
              >
                {line}
              </span>
            </div>
          );
        })}
      </div>

      {/* Annotation tooltip */}
      <div
        style={{
          position: "absolute",
          left: `calc(50% + 460px)`,
          top: `calc(50% - ${blockH / 2}px + ${padV + highlightLine * lineH + lineH / 2}px)`,
          transform: `translateY(-50%) translateX(${annotationX}px)`,
          opacity: annotationOpacity,
          display: "flex",
          alignItems: "center",
          gap: 12,
        }}
      >
        {/* Arrow */}
        <div
          style={{
            width: 0,
            height: 0,
            borderTop: "8px solid transparent",
            borderBottom: "8px solid transparent",
            borderRight: `12px solid ${accent}`,
            flexShrink: 0,
          }}
        />
        {/* Bubble */}
        <div
          style={{
            background: accent,
            color: "#000",
            borderRadius: 12,
            padding: "12px 20px",
            maxWidth: 280,
            fontFamily: FONTS.body,
            fontWeight: FONTS.semibold,
            fontSize: 18,
            lineHeight: 1.4,
            boxShadow: `0 0 24px ${glow}`,
          }}
        >
          {annotationText}
        </div>
      </div>
    </AbsoluteFill>
  );
}
