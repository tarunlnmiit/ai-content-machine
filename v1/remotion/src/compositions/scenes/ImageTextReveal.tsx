import { AbsoluteFill, Img, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, FONTS, type Niche, nicheAccent, nicheGlowStrong, nicheGrid } from "../../styles/chronixel";

export interface ImageTextRevealProps extends Record<string, unknown> {
  headline: string;
  niche: Niche;
  imageUrl?: string;
  subtext?: string;
}

export function ImageTextReveal({ headline, niche, imageUrl, subtext }: ImageTextRevealProps) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const accent = nicheAccent(niche);
  const grid = nicheGrid(niche);
  const glowStrong = nicheGlowStrong(niche);

  const imageOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: "clamp" });

  const headlineSpring = spring({
    frame: frame - 8,
    fps,
    config: { damping: 70, stiffness: 150 },
  });
  const headlineY = interpolate(headlineSpring, [0, 1], [40, 0]);
  const headlineOpacity = interpolate(frame, [8, 22], [0, 1], { extrapolateRight: "clamp" });

  const subtextOpacity = interpolate(
    frame,
    [Math.round(fps * 0.8), Math.round(fps * 1.2)],
    [0, 1],
    { extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg, overflow: "hidden" }}>
      {imageUrl ? (
        <>
          <AbsoluteFill style={{ opacity: imageOpacity }}>
            <Img
              src={imageUrl}
              style={{ width: "100%", height: "100%", objectFit: "cover" }}
            />
          </AbsoluteFill>
          {/* Dark scrim — heavier at bottom for text legibility */}
          <AbsoluteFill
            style={{
              background:
                "linear-gradient(to top, rgba(10,8,20,0.93) 0%, rgba(10,8,20,0.55) 45%, rgba(10,8,20,0.25) 100%)",
              pointerEvents: "none",
            }}
          />
        </>
      ) : (
        <>
          {/* Grid fallback */}
          <AbsoluteFill
            style={{
              backgroundImage: `linear-gradient(${grid} 1px, transparent 1px), linear-gradient(90deg, ${grid} 1px, transparent 1px)`,
              backgroundSize: "80px 80px",
              pointerEvents: "none",
            }}
          />
          {/* Gradient atmosphere fallback */}
          <div
            style={{
              position: "absolute",
              bottom: 0,
              left: "50%",
              transform: "translateX(-50%)",
              width: 1400,
              height: 700,
              background: `radial-gradient(ellipse at bottom, ${glowStrong} 0%, transparent 70%)`,
              pointerEvents: "none",
            }}
          />
        </>
      )}
      {/* Accent stripe at bottom edge */}
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          right: 0,
          height: 4,
          backgroundColor: accent,
        }}
      />
      {/* Text block anchored at bottom */}
      <div
        style={{
          position: "absolute",
          bottom: 80,
          left: 80,
          right: 80,
          display: "flex",
          flexDirection: "column",
          gap: 16,
        }}
      >
        {subtext && (
          <div
            style={{
              opacity: subtextOpacity,
              color: accent,
              fontSize: 22,
              fontFamily: FONTS.body,
              fontWeight: FONTS.semibold,
              letterSpacing: "0.12em",
              textTransform: "uppercase",
            }}
          >
            {subtext}
          </div>
        )}
        <div
          style={{
            opacity: headlineOpacity,
            transform: `translateY(${headlineY}px)`,
            color: COLORS.text,
            fontSize: 72,
            fontFamily: FONTS.heading,
            fontWeight: FONTS.headingWeight,
            letterSpacing: "-0.02em",
            lineHeight: 1.1,
          }}
        >
          {headline}
        </div>
      </div>
    </AbsoluteFill>
  );
}
