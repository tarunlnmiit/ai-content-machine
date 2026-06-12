import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, FONTS, RADIUS, SPACING, type Niche,
         nicheAccent, nicheGlow, gridOverlay } from "../../styles/chronixel";

export interface BrowserTabOverloadProps extends Record<string, unknown> {
  niche: Niche;
}

const THOUGHTS = [
  "groceries",
  "deadline",
  "call mom",
  "fix email",
  "meeting at 3",
  "pay bills",
  "reply slack",
  "dentist appt",
  "gym tomorrow?",
  "feedback needed",
  "check weather",
  "laundry",
  "battery low",
  "update resume",
  "book flight",
  "backup files",
  "podcast queue",
  "meal prep",
  "water plants",
  "stretch",
  "taxes!",
  "call dad",
  "test api",
  "code review",
  "standup notes",
  "docs TODO",
  "refactor utils",
  "type errors",
  "pr comments",
  "debug crash",
  "update deps",
  "fix bug",
  "write tests",
  "review pr",
  "merge main",
  "deploy prod",
  "monitor logs",
  "on call",
  "wake up early",
  "sleep",
  "coffee",
  "exercise",
  "read",
  "learn",
  "build",
  "ship",
  "breathe",
  "relax",
  "focus",
  "think",
];

function Tab({
  index,
  frame,
  niche,
  totalFrames,
  fps,
}: {
  index: number;
  frame: number;
  niche: Niche;
  totalFrames: number;
  fps: number;
}) {
  const spawnFrame = index * 1.2;
  const collapseStart = 180;
  const collapseEnd = 270;

  const spawnProgress = interpolate(
    frame,
    [spawnFrame, spawnFrame + 15],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const collapseProgress = interpolate(
    frame,
    [collapseStart, collapseEnd],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const alpha =
    frame < collapseStart
      ? spawnProgress
      : Math.max(0, 1 - collapseProgress);

  const seed = index * 73;
  const randomX = ((seed * 1111) % 1920) - 200;
  const randomY = ((seed * 2222) % 1080) - 150;

  let x = randomX;
  let y = randomY;

  if (frame >= collapseStart) {
    const springProg = spring({
      frame: frame - collapseStart,
      fps: fps,
      durationInFrames: collapseEnd - collapseStart,
    });
    const normalizedProg = interpolate(
      springProg,
      [0, collapseEnd - collapseStart],
      [0, 1],
      { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
    );
    x = randomX + (960 - randomX) * normalizedProg;
    y = randomY + (540 - randomY) * normalizedProg;
  }

  const scale =
    frame < collapseStart
      ? interpolate(spawnProgress, [0, 1], [0.2, 1])
      : interpolate(collapseProgress, [0, 1], [1, 0.05]);

  const chaosRotation = Math.sin(frame * 0.05 + index) * 8;
  const rotation =
    frame >= collapseStart
      ? interpolate(collapseProgress, [0, 1], [chaosRotation, 0])
      : chaosRotation;

  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        width: 280,
        height: 60,
        backgroundColor: nicheGlow(niche),
        borderRadius: RADIUS.md,
        border: `1px solid ${nicheAccent(niche)}`,
        padding: SPACING.sm,
        opacity: alpha,
        transform: `scale(${scale}) rotate(${rotation}deg)`,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "flex-start",
        overflow: "hidden",
        whiteSpace: "nowrap",
        textOverflow: "ellipsis",
      }}
    >
      <div
        style={{
          fontSize: 12,
          fontFamily: FONTS.mono,
          color: COLORS.textMuted,
          marginBottom: 4,
        }}
      >
        Tab {index + 1}
      </div>
      <div
        style={{
          fontSize: 14,
          fontFamily: FONTS.body,
          fontWeight: 600,
          color: nicheAccent(niche),
        }}
      >
        {THOUGHTS[index % THOUGHTS.length]}
      </div>
    </div>
  );
}

export function BrowserTabOverload(props: BrowserTabOverloadProps) {
  const { niche = "life" } = props;
  const frame = useCurrentFrame();
  const { durationInFrames, fps } = useVideoConfig();

  const numTabs = 50;
  const collapseEnd = 270;

  const overloadOpacity = interpolate(
    frame,
    [0, 120],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const clarityOpacity = interpolate(
    frame,
    [collapseEnd - 30, collapseEnd],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg }}>
      <AbsoluteFill style={gridOverlay(niche)} />

      <div
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          textAlign: "center",
          zIndex: 1,
        }}
      >
        <div
          style={{
            fontSize: 64,
            fontFamily: FONTS.heading,
            fontWeight: FONTS.headingWeight,
            color: nicheAccent(niche),
            opacity: overloadOpacity,
            letterSpacing: "0.1em",
            textShadow: `0 0 20px ${nicheGlow(niche)}`,
          }}
        >
          OVERLOAD
        </div>
      </div>

      {Array.from({ length: numTabs }).map((_, i) => (
        <Tab
          key={i}
          index={i}
          frame={frame}
          niche={niche}
          totalFrames={durationInFrames}
          fps={fps}
        />
      ))}

      {frame >= collapseEnd - 20 && (
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: "50%",
            transform: "translate(-50%, -50%)",
            width: 280,
            height: 60,
            backgroundColor: nicheGlow(niche),
            borderRadius: RADIUS.md,
            border: `1px solid ${nicheAccent(niche)}`,
            padding: SPACING.sm,
            opacity: Math.min(1, (frame - (collapseEnd - 20)) / 15),
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "center",
            zIndex: 100,
          }}
        >
          <div
            style={{
              fontSize: 12,
              fontFamily: FONTS.mono,
              color: COLORS.textMuted,
            }}
          >
            Tab 1
          </div>
        </div>
      )}

      <div
        style={{
          position: "absolute",
          bottom: SPACING.lg,
          left: "50%",
          transform: "translateX(-50%)",
          textAlign: "center",
          zIndex: 10,
        }}
      >
        <div
          style={{
            fontSize: 32,
            fontFamily: FONTS.body,
            fontWeight: 600,
            color: nicheAccent(niche),
            opacity: clarityOpacity,
            letterSpacing: "0.05em",
          }}
        >
          One thing at a time
        </div>
      </div>
    </AbsoluteFill>
  );
}