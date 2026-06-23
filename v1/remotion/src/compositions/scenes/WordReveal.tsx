import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, FONTS, type Niche, nicheAccent, nicheGrid } from "../../styles/chronixel";

export interface WordRevealProps extends Record<string, unknown> {
  words: string[];
  niche: Niche;
  emphasis?: number[]; // 0-based indices to highlight with accent color
  staggerMs?: number; // ms between each word spring-in, default 120
  fontSize?: number;
}

export function WordReveal({
  words,
  niche,
  emphasis = [],
  staggerMs = 120,
  fontSize = 96,
}: WordRevealProps) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const accent = nicheAccent(niche);
  const grid = nicheGrid(niche);
  const staggerFrames = (staggerMs / 1000) * fps;

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
          flexWrap: "wrap",
          alignContent: "center",
          justifyContent: "center",
          padding: "0 120px",
          gap: "0.3em",
          textAlign: "center",
        }}
      >
        {words.map((word, i) => {
          const delay = i * staggerFrames;
          const s = spring({
            frame: frame - delay,
            fps,
            config: { damping: 60, stiffness: 280 },
          });
          const opacity = interpolate(s, [0, 1], [0, 1]);
          const y = interpolate(s, [0, 1], [36, 0]);
          const isAccented = word.startsWith("*") && word.endsWith("*") || emphasis.includes(i);
          const displayWord = word.startsWith("*") && word.endsWith("*") ? word.slice(1, -1) : word;

          return (
            <span
              key={i}
              style={{
                display: "inline-block",
                opacity,
                transform: `translateY(${y}px)`,
                color: isAccented ? accent : COLORS.text,
                fontSize,
                fontFamily: FONTS.heading,
                fontWeight: FONTS.headingWeight,
                lineHeight: 1.15,
                letterSpacing: "-0.02em",
              }}
            >
              {displayWord}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
}
