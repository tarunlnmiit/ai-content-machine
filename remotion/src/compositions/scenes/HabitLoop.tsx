import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, FONTS, type Niche, nicheAccent, nicheGlow } from "../../styles/chronixel";

export interface HabitStep {
  label: string;
  sublabel?: string;
}

export interface HabitLoopProps extends Record<string, unknown> {
  steps: HabitStep[];
  title?: string;
  progress?: number;
  niche: Niche;
}

export function HabitLoop({ steps, title = "The Habit Loop", progress = 1, niche }: HabitLoopProps) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const accent = nicheAccent(niche);
  const glow = nicheGlow(niche);

  const titleIn = spring({ frame, fps, config: { damping: 20, stiffness: 80 } });
  const titleOpacity = interpolate(titleIn, [0, 1], [0, 1]);
  const titleY = interpolate(titleIn, [0, 1], [-20, 0]);

  const clampedSteps = steps.slice(0, 5);
  const N = clampedSteps.length;
  const R = 260;
  const centerX = 960;
  const centerY = 560;

  const arcDelay = Math.max(0, frame - 10);
  const arcIn = spring({ frame: arcDelay, fps, config: { damping: 22, stiffness: 60 } });
  const arcProgress = interpolate(arcIn, [0, 1], [0, progress]);

  const circumference = 2 * Math.PI * R;
  const arcLength = circumference * arcProgress;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.bg,
        fontFamily: FONTS.body,
        overflow: "hidden",
      }}
    >
      {/* Center ambient glow */}
      <div
        style={{
          position: "absolute",
          left: centerX,
          top: centerY,
          width: 500,
          height: 500,
          background: glow,
          borderRadius: "50%",
          filter: "blur(120px)",
          transform: "translate(-50%,-50%)",
          opacity: 0.4,
          pointerEvents: "none",
        }}
      />

      {/* Title */}
      <div
        style={{
          position: "absolute",
          top: 80,
          left: 0,
          right: 0,
          textAlign: "center",
          opacity: titleOpacity,
          transform: `translateY(${titleY}px)`,
        }}
      >
        <div
          style={{
            color: COLORS.text,
            fontFamily: FONTS.heading,
            fontWeight: FONTS.headingWeight,
            fontSize: 48,
            letterSpacing: "-0.02em",
          }}
        >
          {title}
        </div>
        <div
          style={{
            width: 48,
            height: 3,
            background: accent,
            borderRadius: 2,
            margin: "12px auto 0",
            boxShadow: `0 0 12px ${accent}`,
          }}
        />
      </div>

      {/* Ring SVG */}
      <svg
        style={{ position: "absolute", inset: 0 }}
        width={1920}
        height={1080}
        viewBox="0 0 1920 1080"
      >
        {/* Track ring */}
        <circle
          cx={centerX}
          cy={centerY}
          r={R}
          fill="none"
          stroke={COLORS.surfaceBorder}
          strokeWidth={3}
        />
        {/* Progress arc */}
        <circle
          cx={centerX}
          cy={centerY}
          r={R}
          fill="none"
          stroke={accent}
          strokeWidth={4}
          strokeLinecap="round"
          strokeDasharray={`${arcLength} ${circumference}`}
          strokeDashoffset={circumference * 0.25}
          style={{ filter: `drop-shadow(0 0 8px ${accent})` }}
        />

        {/* Connecting lines between nodes */}
        {clampedSteps.map((_, i) => {
          const angle = (i / N) * 2 * Math.PI - Math.PI / 2;
          const nextAngle = ((i + 1) / N) * 2 * Math.PI - Math.PI / 2;
          const x1 = centerX + R * Math.cos(angle);
          const y1 = centerY + R * Math.sin(angle);
          const x2 = centerX + R * Math.cos(nextAngle);
          const y2 = centerY + R * Math.sin(nextAngle);

          const lineDelay = Math.max(0, frame - 20 - i * 10);
          const lineIn = spring({ frame: lineDelay, fps, config: { damping: 20, stiffness: 80 } });
          const lineOp = interpolate(lineIn, [0, 1], [0, 0.15]);

          return (
            <line
              key={i}
              x1={x1}
              y1={y1}
              x2={x2}
              y2={y2}
              stroke={accent}
              strokeWidth={1}
              opacity={lineOp}
              strokeDasharray="4 6"
            />
          );
        })}
      </svg>

      {/* Step nodes */}
      {clampedSteps.map((step, i) => {
        const angle = (i / N) * 2 * Math.PI - Math.PI / 2;
        const x = centerX + R * Math.cos(angle);
        const y = centerY + R * Math.sin(angle);

        const nodeDelay = Math.max(0, frame - 20 - i * 10);
        const nodeIn = spring({ frame: nodeDelay, fps, config: { damping: 18, stiffness: 85 } });
        const nodeScale = interpolate(nodeIn, [0, 1], [0, 1]);
        const nodeOpacity = interpolate(nodeIn, [0, 1], [0, 1]);

        const nodeR = 52;
        const isActive = arcProgress > (i + 0.5) / N;

        // Label positioning — push away from center
        const labelDist = 90;
        const labelX = x + Math.cos(angle) * labelDist;
        const labelY = y + Math.sin(angle) * labelDist;

        const textAnchor =
          Math.abs(Math.cos(angle)) < 0.3
            ? "middle"
            : Math.cos(angle) > 0
            ? "start"
            : "end";

        return (
          <svg
            key={i}
            style={{ position: "absolute", inset: 0, overflow: "visible" }}
            width={1920}
            height={1080}
            viewBox="0 0 1920 1080"
          >
            {/* Glow */}
            {isActive && (
              <circle
                cx={x}
                cy={y}
                r={nodeR + 16}
                fill={glow}
                opacity={nodeOpacity * 0.5}
                style={{ filter: `blur(8px)` }}
              />
            )}

            {/* Node circle */}
            <circle
              cx={x}
              cy={y}
              r={nodeR}
              fill={isActive ? `${accent}22` : COLORS.surface}
              stroke={isActive ? accent : COLORS.surfaceBorder}
              strokeWidth={isActive ? 2.5 : 1.5}
              opacity={nodeOpacity}
              transform={`scale(${nodeScale})`}
              style={{ transformOrigin: `${x}px ${y}px` }}
            />

            {/* Step number */}
            <text
              x={x}
              y={y - 6}
              textAnchor="middle"
              dominantBaseline="middle"
              fill={isActive ? accent : COLORS.textMuted}
              fontFamily={FONTS.heading}
              fontWeight={FONTS.headingWeight}
              fontSize={22}
              opacity={nodeOpacity}
            >
              {String(i + 1).padStart(2, "0")}
            </text>

            {/* Label */}
            <text
              x={labelX}
              y={labelY - (step.sublabel ? 10 : 0)}
              textAnchor={textAnchor}
              dominantBaseline="middle"
              fill={isActive ? COLORS.text : COLORS.textMuted}
              fontFamily={FONTS.body}
              fontWeight={FONTS.semibold}
              fontSize={18}
              opacity={nodeOpacity}
            >
              {step.label}
            </text>

            {step.sublabel && (
              <text
                x={labelX}
                y={labelY + 16}
                textAnchor={textAnchor}
                dominantBaseline="middle"
                fill={COLORS.textDim}
                fontFamily={FONTS.body}
                fontSize={14}
                opacity={nodeOpacity}
              >
                {step.sublabel}
              </text>
            )}
          </svg>
        );
      })}
    </AbsoluteFill>
  );
}
