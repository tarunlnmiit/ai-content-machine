import React from "react";
import {
  AbsoluteFill,
  OffthreadVideo,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from "remotion";

/**
 * OverlayDemo — drops an animated title + subtitle over a recorded clip.
 * The clip must live at  public/clip.mp4
 * This is the "edit" Remotion performs in the reel demo.
 */
export const OverlayDemo: React.FC<{ title: string; subtitle: string }> = ({
  title,
  subtitle,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Title springs up ~0.5s in
  const enter = spring({ frame: frame - 15, fps, config: { damping: 200 } });
  const y = interpolate(enter, [0, 1], [80, 0]);
  const opacity = interpolate(frame, [15, 32], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill>
      {/* the recorded dummy clip */}
      <OffthreadVideo src={staticFile("clip.mp4")} />

      {/* dark gradient at the bottom so white text stays legible */}
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(to top, rgba(0,0,0,0.65) 0%, rgba(0,0,0,0) 45%)",
        }}
      />

      {/* animated overlay text */}
      <AbsoluteFill
        style={{
          justifyContent: "flex-end",
          alignItems: "center",
          paddingBottom: 240,
          transform: `translateY(${y}px)`,
          opacity,
        }}
      >
        <div
          style={{
            fontFamily: "Helvetica, Arial, sans-serif",
            fontWeight: 800,
            fontSize: 100,
            color: "white",
            textAlign: "center",
            lineHeight: 1.05,
            textShadow: "0 4px 24px rgba(0,0,0,0.5)",
            padding: "0 60px",
          }}
        >
          {title}
        </div>
        <div
          style={{
            marginTop: 24,
            fontFamily: "Helvetica, Arial, sans-serif",
            fontWeight: 600,
            fontSize: 46,
            color: "#7fe3ff",
            textAlign: "center",
          }}
        >
          {subtitle}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
