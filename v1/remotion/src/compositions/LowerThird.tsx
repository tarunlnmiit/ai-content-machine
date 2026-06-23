import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, FONTS, type Niche, nicheAccent } from "../styles/chronixel";

interface LowerThirdProps extends Record<string, unknown> {
  text: string;
  durationInFrames: number;
  niche: Niche;
}

export function LowerThird({ text, durationInFrames, niche }: LowerThirdProps) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const barWipeIn = interpolate(frame, [0, 10], [0, 1], { extrapolateRight: "clamp" });
  const barWipeOut = interpolate(frame, [durationInFrames - 10, durationInFrames], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const barScaleX = frame < durationInFrames - 10 ? barWipeIn : barWipeOut;

  const textSpring = spring({ frame: frame - 5, fps, config: { damping: 80, stiffness: 200 } });
  const textOpacityIn = interpolate(frame, [5, 18], [0, 1], { extrapolateRight: "clamp" });
  const textOpacityOut = interpolate(frame, [durationInFrames - 10, durationInFrames], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const textOpacity = frame < durationInFrames - 10 ? textOpacityIn : textOpacityOut;
  const textY = interpolate(textSpring, [0, 1], [20, 0]);

  const accent = nicheAccent(niche);

  return (
    <div
      style={{
        position: "absolute",
        bottom: 80,
        left: 60,
        right: 60,
      }}
    >
      <div
        style={{
          width: "100%",
          height: 3,
          backgroundColor: accent,
          transformOrigin: "left center",
          transform: `scaleX(${barScaleX})`,
          marginBottom: 12,
          borderRadius: 2,
          boxShadow: `0 0 8px ${accent}`,
        }}
      />
      <div
        style={{
          opacity: textOpacity,
          transform: `translateY(${textY}px)`,
          color: COLORS.text,
          fontSize: 28,
          fontFamily: FONTS.body,
          fontWeight: FONTS.semibold,
          letterSpacing: "0.01em",
        }}
      >
        {text}
      </div>
    </div>
  );
}
