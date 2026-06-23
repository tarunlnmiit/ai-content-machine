import { AbsoluteFill, Audio, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { useAudioData, visualizeAudio } from "@remotion/media-utils";
import {
  COLORS,
  FONTS,
  type Niche,
  nicheAccent,
  nicheGlow,
  nicheGrid,
  nicheShowName,
} from "../styles/chronixel";

const BAR_COUNT = 64;

export interface AudiogramFeedProps extends Record<string, unknown> {
  audioFile: string;
  startSec: number;
  endSec: number;
  quote: string;
  speakerLabel?: string;
  niche: Niche;
  podcastName: string;
}

export interface AudiogramStoryProps extends AudiogramFeedProps {}

function AudiogramBase({
  audioFile,
  startSec,
  endSec,
  quote,
  speakerLabel,
  niche,
  podcastName,
  width,
  height,
}: AudiogramFeedProps & { width: number; height: number }) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const audioData = useAudioData(staticFile(audioFile));

  const accent = nicheAccent(niche);
  const glow = nicheGlow(niche);
  const grid = nicheGrid(niche);
  const showName = nicheShowName(niche);

  const bars = audioData
    ? visualizeAudio({
        audioData,
        frame,
        fps,
        numberOfSamples: BAR_COUNT,
        dataOffsetInSeconds: startSec,
        smoothing: true,
      })
    : new Array(BAR_COUNT).fill(0) as number[];

  const isPortrait = height > width;
  const barAreaHeight = isPortrait ? height * 0.22 : height * 0.28;
  const barMaxHeight = barAreaHeight * 0.85;
  const barWidth = (width * 0.78) / BAR_COUNT;
  const barGap = barWidth * 0.35;

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg, overflow: "hidden" }}>
      {/* Audio element (renders as data source only — no visible output) */}
      <Audio
        src={staticFile(audioFile)}
        startFrom={Math.floor(startSec * fps)}
        endAt={Math.ceil(endSec * fps)}
        volume={1}
      />

      {/* Grid overlay */}
      <AbsoluteFill
        style={{
          backgroundImage: `linear-gradient(${grid} 1px, transparent 1px), linear-gradient(90deg, ${grid} 1px, transparent 1px)`,
          backgroundSize: "80px 80px",
          pointerEvents: "none",
        }}
      />

      {/* Glow bloom behind waveform */}
      <div
        style={{
          position: "absolute",
          bottom: isPortrait ? "8%" : "10%",
          left: "50%",
          transform: "translateX(-50%)",
          width: "70%",
          height: barAreaHeight,
          background: `radial-gradient(ellipse 80% 80% at 50% 100%, ${glow}, transparent)`,
          pointerEvents: "none",
        }}
      />

      {/* Podcast name (top) */}
      <div
        style={{
          position: "absolute",
          top: isPortrait ? 64 : 40,
          left: 0,
          right: 0,
          textAlign: "center",
          color: COLORS.textMuted,
          fontSize: isPortrait ? 22 : 18,
          fontFamily: FONTS.body,
          fontWeight: FONTS.semibold,
          letterSpacing: "0.12em",
          textTransform: "uppercase",
        }}
      >
        {podcastName || showName}
      </div>

      {/* Quote (center) */}
      <div
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -60%)",
          width: "78%",
          textAlign: "center",
        }}
      >
        <div
          style={{
            background: COLORS.surface,
            border: `1px solid ${COLORS.surfaceBorder}`,
            borderRadius: 16,
            padding: isPortrait ? "40px 40px" : "32px 40px",
          }}
        >
          {/* accent top border */}
          <div
            style={{
              width: 48,
              height: 3,
              backgroundColor: accent,
              borderRadius: 2,
              margin: "0 auto 24px",
              boxShadow: `0 0 10px ${accent}`,
            }}
          />
          <p
            style={{
              color: COLORS.text,
              fontSize: isPortrait ? 34 : 28,
              fontFamily: FONTS.heading,
              fontWeight: FONTS.headingWeight,
              lineHeight: 1.4,
              margin: 0,
              letterSpacing: "-0.01em",
            }}
          >
            {quote}
          </p>
          {speakerLabel && (
            <p
              style={{
                color: accent,
                fontSize: isPortrait ? 18 : 15,
                fontFamily: FONTS.body,
                fontWeight: FONTS.semibold,
                letterSpacing: "0.08em",
                marginTop: 20,
                marginBottom: 0,
                textTransform: "uppercase",
              }}
            >
              — {speakerLabel}
            </p>
          )}
        </div>
      </div>

      {/* Waveform bars (bottom) */}
      <div
        style={{
          position: "absolute",
          bottom: isPortrait ? "6%" : "8%",
          left: "50%",
          transform: "translateX(-50%)",
          display: "flex",
          alignItems: "flex-end",
          gap: barGap,
          height: barAreaHeight,
          width: width * 0.78,
        }}
      >
        {bars.map((amplitude, i) => {
          const barH = Math.max(3, amplitude * barMaxHeight);
          const isMid = Math.abs(i - BAR_COUNT / 2) < BAR_COUNT * 0.15;
          return (
            <div
              key={i}
              style={{
                flex: 1,
                height: barH,
                backgroundColor: accent,
                borderRadius: 2,
                opacity: isMid ? 1 : 0.5 + amplitude * 0.5,
                boxShadow: amplitude > 0.5 ? `0 0 6px ${accent}` : "none",
              }}
            />
          );
        })}
      </div>
    </AbsoluteFill>
  );
}

export function AudiogramFeed(props: AudiogramFeedProps) {
  return <AudiogramBase {...props} width={1080} height={1080} />;
}

export function AudiogramStory(props: AudiogramStoryProps) {
  return <AudiogramBase {...props} width={1080} height={1920} />;
}
