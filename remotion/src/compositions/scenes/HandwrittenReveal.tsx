import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, FONTS, type Niche, nicheAccent, gridOverlay } from "../../styles/chronixel";

export interface HandwrittenRevealProps extends Record<string, unknown> {
  lines: string[];
  niche: Niche;
}

const FONT_SIZE = 88;
const LINE_HEIGHT = 144;
const STROKE_FRAMES = 20;
const STAGGER_FRAMES = 14;
const STROKE_WIDTH = 5;
const UNDERLINE_GAP = 12;

function makePath(width: number, y: number, seed: number): string {
  const x0 = width * 0.08;
  const x1 = width * 0.92;
  const span = x1 - x0;
  // Gentle cubic bezier wave — unique per line via seed
  const cp1x = x0 + span * 0.28;
  const cp1y = y + (seed % 2 === 0 ? -7 : 5);
  const cp2x = x0 + span * 0.72;
  const cp2y = y + (seed % 2 === 0 ? 9 : -5);
  return `M ${x0} ${y} C ${cp1x} ${cp1y} ${cp2x} ${cp2y} ${x1} ${y}`;
}

export function HandwrittenReveal({ lines, niche }: HandwrittenRevealProps) {
  const frame = useCurrentFrame();
  const { width, height, fps } = useVideoConfig();
  const accent = nicheAccent(niche);

  const safeLines = lines.slice(0, 4);
  const totalHeight = safeLines.length * LINE_HEIGHT;
  const groupTopY = (height - totalHeight) / 2;

  // Entrance spring for the whole block
  const entrance = spring({ frame, fps, config: { damping: 18, stiffness: 80 } });

  const lineData = safeLines.map((line, i) => {
    const strokeStart = i * STAGGER_FRAMES;
    const strokeEnd = strokeStart + STROKE_FRAMES;

    const strokeProgress = interpolate(frame, [strokeStart, strokeEnd], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });

    const textOpacity = interpolate(frame, [strokeStart, strokeStart + 12], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });

    // Text center within its row; underline sits just below
    const lineTopY = groupTopY + i * LINE_HEIGHT;
    const textBottomY = lineTopY + (LINE_HEIGHT + FONT_SIZE) / 2;
    const underlineY = textBottomY + UNDERLINE_GAP;

    const svgPath = makePath(width, underlineY, i);

    return { line, strokeProgress, textOpacity, svgPath };
  });

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg }}>
      <AbsoluteFill style={gridOverlay(niche)} />

      {/* SVG underlines with stroke animation */}
      <svg style={{ position: "absolute", inset: 0, width, height, pointerEvents: "none" }}>
        {lineData.map(({ svgPath, strokeProgress }, i) => (
          <path
            key={i}
            d={svgPath}
            stroke={accent}
            strokeWidth={STROKE_WIDTH}
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
            style={{
              strokeDasharray: 2000,
              strokeDashoffset: interpolate(strokeProgress, [0, 1], [2000, 0]),
            }}
          />
        ))}
      </svg>

      {/* Text overlay */}
      <AbsoluteFill
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          transform: `translateY(${interpolate(entrance, [0, 1], [24, 0])}px)`,
        }}
      >
        {lineData.map(({ line, textOpacity }, i) => (
          <div
            key={i}
            style={{
              color: COLORS.text,
              fontFamily: FONTS.heading,
              fontWeight: FONTS.headingWeight,
              fontSize: FONT_SIZE,
              lineHeight: `${LINE_HEIGHT}px`,
              letterSpacing: "-0.02em",
              textAlign: "center",
              opacity: textOpacity,
              paddingLeft: 80,
              paddingRight: 80,
              whiteSpace: "nowrap",
            }}
          >
            {line}
          </div>
        ))}
      </AbsoluteFill>
    </AbsoluteFill>
  );
}
