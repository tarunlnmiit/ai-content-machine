import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import {
  COLORS,
  FONTS,
  RADIUS,
  type Niche,
  nicheAccent,
  gridOverlay,
} from "../../styles/chronixel";

export interface DataPipelineFlowProps extends Record<string, unknown> {
  niche: Niche;
}

function hexToRgba(hex: string, alpha: number): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

export function DataPipelineFlow({ niche }: DataPipelineFlowProps) {
  const { fps } = useVideoConfig();
  const frame = useCurrentFrame();

  const accent = nicheAccent(niche);
  const stages = ["Load", "Select", "Clean", "Aggregate"];
  const stageXPositions = [200, 550, 900, 1250];
  const rowCount = 8;
  const cellWidth = 120;
  const cellHeight = 28;
  const rowSpacing = 34;
  const startY = 300;

  const animateDataRow = (rowIdx: number, stageIdx: number) => {
    const stageDelay = stageIdx * 14;
    const rowDelay = rowIdx * 5;
    const activationFrame = stageDelay + rowDelay;

    if (frame < activationFrame) {
      return {
        opacity: 0,
        scaleY: 0.5,
        glowAlpha: 0,
      };
    }

    const elapsedFrames = frame - activationFrame;
    const springValue = spring({
      fps,
      frame: elapsedFrames,
      config: {
        damping: 8,
        mass: 1,
        stiffness: 110,
      },
    });

    const progress = Math.min(1, springValue);

    const opacity = interpolate(progress, [0, 0.2, 1], [0, 0.5, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });

    // Data compresses/aggregates across pipeline stages
    const scaleY = interpolate(stageIdx, [0, stages.length - 1], [1, 0.75], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });

    // Glow peaks on entry
    const glowAlpha = interpolate(progress, [0, 0.35, 1], [0, 0.6, 0.1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });

    return {
      opacity,
      scaleY,
      glowAlpha,
    };
  };

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg }}>
      <AbsoluteFill style={gridOverlay(niche)} />

      <div style={{ position: "relative", width: "100%", height: "100%" }}>
        {/* Stage labels */}
        <div style={{ position: "relative", paddingTop: 100 }}>
          {stages.map((name, idx) => (
            <div
              key={name}
              style={{
                position: "absolute",
                left: stageXPositions[idx],
                top: 80,
                transform: "translateX(-50%)",
                fontFamily: FONTS.heading,
                fontSize: 20,
                fontWeight: 800,
                letterSpacing: 0.5,
                color: COLORS.textMuted,
                textAlign: "center",
              }}
            >
              {name}
            </div>
          ))}
        </div>

        {/* Data flow rows */}
        {Array.from({ length: rowCount }).map((_, rowIdx) => (
          <div key={`row-${rowIdx}`} style={{ position: "relative" }}>
            {stages.map((_, stageIdx) => {
              const { opacity, scaleY, glowAlpha } = animateDataRow(
                rowIdx,
                stageIdx
              );
              const xPos = stageXPositions[stageIdx];
              const yPos = startY + rowIdx * rowSpacing;

              // Color intensity increases through stages
              const colorAlpha = interpolate(
                stageIdx,
                [0, stages.length - 1],
                [0.25, 0.65],
                { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
              );

              const glowBlur = Math.round(14 * glowAlpha);
              const glowColor = hexToRgba(accent, glowAlpha * 0.35);

              return (
                <div
                  key={`cell-${stageIdx}`}
                  style={{
                    position: "absolute",
                    left: xPos - cellWidth / 2,
                    top: yPos,
                    width: cellWidth,
                    height: cellHeight,
                    backgroundColor: hexToRgba(accent, colorAlpha * opacity),
                    border: `1.5px solid ${hexToRgba(accent, 0.3 + glowAlpha * 0.5)}`,
                    borderRadius: RADIUS.sm,
                    opacity,
                    transform: `scaleY(${scaleY})`,
                    transformOrigin: "center",
                    boxShadow:
                      glowAlpha > 0.05
                        ? `0 0 ${glowBlur}px ${glowColor}`
                        : "none",
                  }}
                />
              );
            })}
          </div>
        ))}
      </div>
    </AbsoluteFill>
  );
}