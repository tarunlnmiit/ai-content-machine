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
 * WordPopCaption
 * Plays a full-screen clip and pops each word of a caption in, one at a time.
 * Drop your clip in /public and set `src`. Edit `text`, `position`, and colors.
 */
export const WordPopCaption: React.FC<{
  src?: string;
  text?: string;
  position?: "top" | "center" | "bottom";
  color?: string;
}> = ({
  src = "clip.mp4",
  text = "MADE WITH CLAUDE",
  position = "bottom",
  color = "#ffffff",
}) => {
  const frame = useCurrentFrame();
  const { fps, height } = useVideoConfig();
  const words = text.split(" ");

  const top =
    position === "top" ? "12%" : position === "center" ? "44%" : "78%";

  return (
    <AbsoluteFill>
      <OffthreadVideo src={staticFile(src)} />
      <AbsoluteFill
        style={{
          top,
          height: 0,
          flexDirection: "row",
          justifyContent: "center",
          gap: "0.3em",
          flexWrap: "wrap",
          paddingLeft: 40,
          paddingRight: 40,
        }}
      >
        {words.map((word, i) => {
          const start = i * 4; // 4 frames between words
          const enter = spring({
            frame: frame - start,
            fps,
            config: { damping: 12, stiffness: 200 },
          });
          return (
            <span
              key={i}
              style={{
                fontFamily: "Inter, Arial, sans-serif",
                fontWeight: 800,
                fontSize: height * 0.045,
                color,
                opacity: enter,
                transform: `translateY(${(1 - enter) * 30}px) scale(${enter})`,
                textShadow: "0 4px 18px rgba(0,0,0,0.6)",
                lineHeight: 1.1,
              }}
            >
              {word}
            </span>
          );
        })}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
