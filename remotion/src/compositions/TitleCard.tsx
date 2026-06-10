import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import {
  COLORS,
  FONTS,
  type Niche,
  nicheAccent,
  nicheGrid,
  nicheShowName,
} from "../styles/chronixel";

interface TitleCardProps extends Record<string, unknown> {
  titleText: string;
  showName?: string;
  durationInFrames: number;
  niche: Niche;
}

export function TitleCard({ titleText, showName, durationInFrames, niche }: TitleCardProps) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const bgOpacity = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: "clamp" });

  const lineX = interpolate(frame, [0, 14], [-100, 0], { extrapolateRight: "clamp" });

  const showNameOpacity = interpolate(frame, [8, 22], [0, 1], { extrapolateRight: "clamp" });
  const showNameSpring = spring({ frame: frame - 8, fps, config: { damping: 80, stiffness: 200 } });
  const showNameY = interpolate(showNameSpring, [0, 1], [20, 0]);

  const titleOpacity = interpolate(frame, [16, 34], [0, 1], { extrapolateRight: "clamp" });
  const titleSpring = spring({ frame: frame - 16, fps, config: { damping: 80, stiffness: 200 } });
  const titleY = interpolate(titleSpring, [0, 1], [24, 0]);

  const outroOpacity = interpolate(frame, [durationInFrames - 10, durationInFrames], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const label = showName ?? nicheShowName(niche);
  const accent = nicheAccent(niche);
  const grid = nicheGrid(niche);

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        backgroundColor: COLORS.bg,
        opacity: bgOpacity * outroOpacity,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* grid overlay */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage: `linear-gradient(${grid} 1px, transparent 1px), linear-gradient(90deg, ${grid} 1px, transparent 1px)`,
          backgroundSize: "80px 80px",
          pointerEvents: "none",
        }}
      />

      {/* glass panel */}
      <div
        style={{
          position: "relative",
          background: COLORS.surface,
          border: `1px solid ${COLORS.surfaceBorder}`,
          borderRadius: 20,
          padding: "56px 80px",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 0,
          minWidth: 640,
          maxWidth: "62%",
        }}
      >
        {/* accent line */}
        <div
          style={{
            width: "50%",
            height: 2,
            backgroundColor: accent,
            transform: `translateX(${lineX}%)`,
            marginBottom: 32,
            borderRadius: 1,
            boxShadow: `0 0 12px ${accent}`,
          }}
        />

        <div
          style={{
            opacity: showNameOpacity,
            transform: `translateY(${showNameY}px)`,
            color: COLORS.textMuted,
            fontSize: 16,
            fontFamily: FONTS.body,
            fontWeight: FONTS.semibold,
            letterSpacing: "0.14em",
            textTransform: "uppercase",
            marginBottom: 20,
          }}
        >
          {label}
        </div>

        <div
          style={{
            opacity: titleOpacity,
            transform: `translateY(${titleY}px)`,
            color: COLORS.text,
            fontSize: 52,
            fontFamily: FONTS.heading,
            fontWeight: FONTS.headingWeight,
            textAlign: "center",
            lineHeight: 1.2,
            letterSpacing: "-0.01em",
          }}
        >
          {titleText}
        </div>
      </div>
    </div>
  );
}
