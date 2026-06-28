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
 * LowerThird
 * A name tag that slides in from the left. Good for "Name / Title" intros.
 * Edit `name`, `title`, `accent`, and `inAt` (seconds before it appears).
 */
export const LowerThird: React.FC<{
  src?: string;
  name?: string;
  title?: string;
  accent?: string;
  inAt?: number;
}> = ({
  src = "clip.mp4",
  name = "Tarun",
  title = "Data Scientist",
  accent = "#ffd400",
  inAt = 0.5,
}) => {
  const frame = useCurrentFrame();
  const { fps, height } = useVideoConfig();
  const startFrame = inAt * fps;

  const enter = spring({
    frame: frame - startFrame,
    fps,
    config: { damping: 14, stiffness: 160 },
  });
  const x = interpolate(enter, [0, 1], [-500, 0]);

  return (
    <AbsoluteFill>
      <OffthreadVideo src={staticFile(src)} />
      <div
        style={{
          position: "absolute",
          left: 48,
          bottom: height * 0.14,
          transform: `translateX(${x}px)`,
          opacity: enter,
          background: "rgba(0,0,0,0.55)",
          backdropFilter: "blur(8px)",
          borderLeft: `8px solid ${accent}`,
          borderRadius: 12,
          padding: "18px 28px",
        }}
      >
        <div
          style={{
            fontFamily: "Inter, Arial, sans-serif",
            fontWeight: 800,
            fontSize: height * 0.032,
            color: "#fff",
            lineHeight: 1.1,
          }}
        >
          {name}
        </div>
        <div
          style={{
            fontFamily: "Inter, Arial, sans-serif",
            fontWeight: 500,
            fontSize: height * 0.02,
            color: accent,
            marginTop: 4,
          }}
        >
          {title}
        </div>
      </div>
    </AbsoluteFill>
  );
};
