import {
  AbsoluteFill,
  OffthreadVideo,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
} from "remotion";

/**
 * ProgressBar
 * A thin bar across the bottom that fills as the clip plays. Edit `accent` + `thickness`.
 */
export const ProgressBar: React.FC<{
  src?: string;
  accent?: string;
  thickness?: number;
}> = ({ src = "clip.mp4", accent = "#ffd400", thickness = 10 }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const width = interpolate(frame, [0, durationInFrames], [0, 100], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill>
      <OffthreadVideo src={staticFile(src)} />
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          height: thickness,
          width: `${width}%`,
          background: accent,
        }}
      />
    </AbsoluteFill>
  );
};
