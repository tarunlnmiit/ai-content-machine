import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, FONTS, RADIUS, type Niche, nicheAccent, nicheGrid } from "../../styles/chronixel";

export interface DataPoint {
  label: string;
  value: number; // 0–100 for bar height percentage
}

export interface DataVizRevealProps extends Record<string, unknown> {
  data: DataPoint[];
  niche: Niche;
  title?: string;
  chartType?: "bar" | "line";
}

export function DataVizReveal({
  data,
  niche,
  title,
  chartType = "bar",
}: DataVizRevealProps) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const accent = nicheAccent(niche);
  const grid = nicheGrid(niche);

  const titleOpacity = interpolate(frame, [0, 18], [0, 1], { extrapolateRight: "clamp" });
  const titleSpring = spring({ frame, fps, config: { damping: 80, stiffness: 200 } });
  const titleY = interpolate(titleSpring, [0, 1], [20, 0]);

  const MAX_BARS = 8;
  const items = data.slice(0, MAX_BARS);
  const staggerFrames = 8;

  if (chartType === "line") {
    // Line chart — all bars reveal together as a path
    const chartProgress = spring({
      frame: frame - 10,
      fps,
      config: { damping: 90, stiffness: 100 },
    });
    const chartW = 900;
    const chartH = 320;
    const maxVal = Math.max(...items.map((d) => d.value), 1);
    const points = items.map((d, i) => ({
      x: (i / (items.length - 1)) * chartW,
      y: chartH - (d.value / maxVal) * chartH * chartProgress,
    }));
    const pathD = points
      .map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`)
      .join(" ");

    return (
      <AbsoluteFill style={{ backgroundColor: COLORS.bg, overflow: "hidden" }}>
        <AbsoluteFill
          style={{
            backgroundImage: `linear-gradient(${grid} 1px, transparent 1px), linear-gradient(90deg, ${grid} 1px, transparent 1px)`,
            backgroundSize: "80px 80px",
            pointerEvents: "none",
          }}
        />
        <div
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            padding: "60px 100px",
            gap: 32,
          }}
        >
          {title && (
            <div
              style={{
                opacity: titleOpacity,
                transform: `translateY(${titleY}px)`,
                color: COLORS.text,
                fontSize: 42,
                fontFamily: FONTS.heading,
                fontWeight: FONTS.headingWeight,
                letterSpacing: "-0.01em",
                alignSelf: "flex-start",
              }}
            >
              {title}
            </div>
          )}
          <svg width={chartW} height={chartH + 40} style={{ overflow: "visible" }}>
            {/* Baseline */}
            <line
              x1={0}
              y1={chartH}
              x2={chartW}
              y2={chartH}
              stroke={COLORS.surfaceBorder}
              strokeWidth="1.5"
            />
            {/* Line */}
            <path
              d={pathD}
              fill="none"
              stroke={accent}
              strokeWidth="3"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            {/* Dots at data points */}
            {points.map((p, i) => (
              <circle key={i} cx={p.x} cy={p.y} r={5} fill={accent} />
            ))}
            {/* Labels */}
            {items.map((d, i) => (
              <text
                key={i}
                x={points[i].x}
                y={chartH + 28}
                textAnchor="middle"
                fill={COLORS.textMuted}
                fontSize={16}
                fontFamily={FONTS.body}
              >
                {d.label}
              </text>
            ))}
          </svg>
        </div>
      </AbsoluteFill>
    );
  }

  // Bar chart (default)
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg, overflow: "hidden" }}>
      <AbsoluteFill
        style={{
          backgroundImage: `linear-gradient(${grid} 1px, transparent 1px), linear-gradient(90deg, ${grid} 1px, transparent 1px)`,
          backgroundSize: "80px 80px",
          pointerEvents: "none",
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "60px 100px",
          gap: 32,
        }}
      >
        {title && (
          <div
            style={{
              opacity: titleOpacity,
              transform: `translateY(${titleY}px)`,
              color: COLORS.text,
              fontSize: 42,
              fontFamily: FONTS.heading,
              fontWeight: FONTS.headingWeight,
              letterSpacing: "-0.01em",
              alignSelf: "flex-start",
            }}
          >
            {title}
          </div>
        )}

        <div
          style={{
            display: "flex",
            alignItems: "flex-end",
            gap: 16,
            height: 320,
            width: "100%",
          }}
        >
          {items.map((d, i) => {
            const delay = i * staggerFrames + 10;
            const s = spring({
              frame: frame - delay,
              fps,
              config: { damping: 70, stiffness: 120 },
            });
            const barH = (d.value / 100) * 300 * s;
            const opacity = interpolate(frame - delay, [0, 10], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });

            return (
              <div
                key={i}
                style={{
                  flex: 1,
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  gap: 12,
                  justifyContent: "flex-end",
                  height: "100%",
                  opacity,
                }}
              >
                <div
                  style={{
                    color: COLORS.textMuted,
                    fontSize: 20,
                    fontFamily: FONTS.body,
                    fontWeight: FONTS.semibold,
                  }}
                >
                  {d.value}
                </div>
                <div
                  style={{
                    width: "100%",
                    height: barH,
                    backgroundColor: accent,
                    borderRadius: `${RADIUS.sm}px ${RADIUS.sm}px 0 0`,
                    boxShadow: `0 0 16px ${accent}44`,
                  }}
                />
                <div
                  style={{
                    color: COLORS.textMuted,
                    fontSize: 18,
                    fontFamily: FONTS.body,
                    fontWeight: FONTS.bodyWeight,
                    textAlign: "center",
                    maxWidth: "100%",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                >
                  {d.label}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
}
