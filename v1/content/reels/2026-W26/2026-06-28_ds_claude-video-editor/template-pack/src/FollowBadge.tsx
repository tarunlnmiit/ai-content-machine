import {
  AbsoluteFill,
  OffthreadVideo,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  spring,
} from "remotion";

/**
 * FollowBadge
 * A "Follow for more" badge that bounces in at `appearAt` seconds. Edit `handle` + `appearAt`.
 */
export const FollowBadge: React.FC<{
  src?: string;
  handle?: string;
  appearAt?: number;
}> = ({ src = "clip.mp4", handle = "@breathofdatascience", appearAt = 4 }) => {
  const frame = useCurrentFrame();
  const { fps, height } = useVideoConfig();
  const start = appearAt * fps;
  const pop = spring({
    frame: frame - start,
    fps,
    config: { damping: 9, stiffness: 220 },
  });

  return (
    <AbsoluteFill>
      <OffthreadVideo src={staticFile(src)} />
      <div
        style={{
          position: "absolute",
          top: height * 0.06,
          right: 40,
          transform: `scale(${pop})`,
          opacity: pop,
          background: "#fff",
          color: "#111",
          fontFamily: "Inter, Arial, sans-serif",
          fontWeight: 800,
          fontSize: height * 0.022,
          padding: "12px 22px",
          borderRadius: 999,
          boxShadow: "0 8px 24px rgba(0,0,0,0.35)",
        }}
      >
        Follow for more · {handle}
      </div>
    </AbsoluteFill>
  );
};
