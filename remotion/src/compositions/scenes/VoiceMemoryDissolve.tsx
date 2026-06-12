import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, FONTS, RADIUS, type Niche,
           nicheAccent, nicheGlowStrong, nicheGlow,
           gridOverlay } from "../../styles/chronixel";

export interface VoiceMemoryDissolveProps extends Record<string, unknown> {
  niche: Niche;
  voiceName?: string;
  particleCount?: number;
}

export function VoiceMemoryDissolve({
  niche = "poetry",
  voiceName = "Echo",
  particleCount = 56,
}: VoiceMemoryDissolveProps) {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();

  const centerX = width / 2;
  const centerY = height / 2;
  const accent = nicheAccent(niche);
  const glowColor = nicheGlow(niche);
  const glowStrong = nicheGlowStrong(niche);

  // Timing phases
  const waveformPulseEnd = 140;
  const burstStart = 140;
  const reformStart = 260;
  const reformEnd = 380;
  const dissolveFinalEnd = 420;

  // === WAVEFORM PULSE ===
  const waveformFrame = Math.min(frame, waveformPulseEnd);
  const waveformAmplitude = spring({
    frame: waveformFrame,
    fps: 30,
    config: { damping: 0.75, mass: 1 },
  }) * 48;

  const wavePoints: Array<{ x: number; y: number }> = [];
  const waveLength = 80;
  for (let i = 0; i < waveLength; i++) {
    const xOffset = centerX - (waveLength / 2) * 6 + i * 6;
    const baseWave = Math.sin((i * 0.08 + waveformFrame * 0.05) * Math.PI) * waveformAmplitude;
    const pulseModulation = Math.sin(waveformFrame * 0.015) * 0.6 + 0.4;
    const harmonic = Math.sin((i * 0.12 + waveformFrame * 0.08) * Math.PI) * waveformAmplitude * 0.4 * pulseModulation;
    const yPos = centerY + baseWave + harmonic;
    wavePoints.push({ x: xOffset, y: yPos });
  }

  const waveOpacity = interpolate(
    frame,
    [0, waveformPulseEnd / 3, waveformPulseEnd],
    [0.2, 1, 0.4]
  );

  // === PARTICLES BURST ===
  const particles = Array.from({ length: particleCount }, (_, idx) => {
    const angle = (idx / particleCount) * Math.PI * 2;
    const baseDistance = 60 + Math.sin(idx * 0.5) * 40;
    const maxDistance = baseDistance + 140;

    const burstFrame = Math.max(0, frame - burstStart);
    const burstProgress = spring({
      frame: burstFrame,
      fps: 30,
      config: { damping: 0.6, mass: 0.9 },
    });

    const distance = baseDistance + (maxDistance - baseDistance) * burstProgress;
    const x = centerX + Math.cos(angle) * distance;
    const y = centerY + Math.sin(angle) * distance;

    // Particle rotation
    const rotationVel = angle * (180 / Math.PI) + burstFrame * 3;

    // Fade in burst, fade out during reform
    const reformPhase = Math.max(0, frame - reformStart) / (reformEnd - reformStart);
    const particleOpacity = Math.max(0, 1 - reformPhase * 1.2);

    const size = 5 + Math.random() * 11;

    return { x, y, rotation: rotationVel, opacity: particleOpacity, size };
  });

  // === MEMORY REFORMATION ===
  const reformProgress = Math.max(0, frame - reformStart) / (reformEnd - reformStart);

  // Handwriting emerges
  const handwritingY = interpolate(reformProgress, [0, 0.35], [centerY + 120, centerY - 40]);
  const handwritingOpacity = interpolate(
    reformProgress,
    [0, 0.2, 0.35, 0.55],
    [0, 0.8, 0.8, 0]
  );
  const handwritingScale = interpolate(reformProgress, [0, 0.35], [0.2, 1]);

  // Color swatch emerges
  const swatchX = interpolate(reformProgress, [0.2, 0.55], [centerX + 180, centerX - 60]);
  const swatchOpacity = interpolate(
    reformProgress,
    [0.2, 0.4, 0.55, 0.75],
    [0, 0.85, 0.85, 0]
  );
  const swatchScale = interpolate(reformProgress, [0.2, 0.55], [0.15, 1]);

  // Silhouette emerges
  const silhouetteY = interpolate(reformProgress, [0.4, 0.75], [centerY + 100, centerY - 80]);
  const silhouetteOpacity = interpolate(
    reformProgress,
    [0.4, 0.6, 0.75, 0.95],
    [0, 0.75, 0.75, 0]
  );
  const silhouetteScale = interpolate(reformProgress, [0.4, 0.75], [0.1, 0.85]);

  // === FINAL DISSOLVE ===
  const dissolveProgress = Math.max(0, frame - reformEnd) / (dissolveFinalEnd - reformEnd);
  const masterOpacity = 1 - dissolveProgress * 0.8;

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg, opacity: masterOpacity, overflow: "hidden" }}>
      {/* Grid overlay */}
      <AbsoluteFill style={gridOverlay(niche)} />

      {/* Ambient glow aura */}
      <div
        style={{
          position: "absolute",
          left: centerX - 240,
          top: centerY - 240,
          width: 480,
          height: 480,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${glowColor} 0%, transparent 65%)`,
          opacity: interpolate(
            frame,
            [0, 70, (70 + waveformPulseEnd) / 2, waveformPulseEnd, reformEnd],
            [0.15, 0.4, 0.6, 0.3, 0.1]
          ),
          pointerEvents: "none",
        }}
      />

      {/* Waveform visualization */}
      {frame < waveformPulseEnd && (
        <svg
          width={width}
          height={height}
          style={{ position: "absolute", opacity: waveOpacity }}
        >
          {/* Wave line */}
          <polyline
            points={wavePoints.map((p) => `${p.x},${p.y}`).join(" ")}
            fill="none"
            stroke={accent}
            strokeWidth="2.5"
            opacity="0.9"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Wave pulse points */}
          {wavePoints.map((point, idx) => {
            const pointPulse = Math.sin(waveformFrame * 0.04 + idx * 0.3) * 0.5 + 0.5;
            return (
              <circle
                key={`wave-pt-${idx}`}
                cx={point.x}
                cy={point.y}
                r={1.5 + pointPulse * 2.5}
                fill={accent}
                opacity={0.6 + pointPulse * 0.4}
              />
            );
          })}
        </svg>
      )}

      {/* Particle burst */}
      {frame >= burstStart && frame < reformEnd && (
        <div style={{ position: "absolute", width, height }}>
          {particles.map((p, idx) => (
            <div
              key={`particle-${idx}`}
              style={{
                position: "absolute",
                left: p.x - p.size / 2,
                top: p.y - p.size / 2,
                width: p.size,
                height: p.size,
                backgroundColor: accent,
                borderRadius: RADIUS.sm,
                opacity: p.opacity,
                transform: `rotate(${p.rotation}deg)`,
                boxShadow: `0 0 8px ${glowColor}`,
              }}
            />
          ))}
        </div>
      )}

      {/* Memory 1: Handwritten name */}
      {frame >= reformStart && (
        <div
          style={{
            position: "absolute",
            left: centerX - 60,
            top: handwritingY,
            fontSize: "20px",
            fontFamily: FONTS.mono,
            fontWeight: 500,
            color: accent,
            opacity: handwritingOpacity,
            transform: `scale(${handwritingScale})`,
            transformOrigin: "center center",
            whiteSpace: "nowrap",
            letterSpacing: "1px",
          }}
        >
          {voiceName}
        </div>
      )}

      {/* Memory 2: Color swatch */}
      {frame >= reformStart && (
        <div
          style={{
            position: "absolute",
            left: swatchX - 32,
            top: centerY - 80,
            width: 64,
            height: 64,
            backgroundColor: accent,
            borderRadius: RADIUS.md,
            opacity: swatchOpacity,
            transform: `scale(${swatchScale})`,
            transformOrigin: "center center",
            boxShadow: `0 0 20px ${glowStrong}`,
          }}
        />
      )}

      {/* Memory 3: Silhouette figure */}
      {frame >= reformStart && (
        <div
          style={{
            position: "absolute",
            left: centerX - 32,
            top: silhouetteY - 48,
            width: 64,
            height: 96,
            backgroundColor: accent,
            borderRadius: "50% 50% 40% 40%",
            opacity: silhouetteOpacity,
            transform: `scale(${silhouetteScale})`,
            transformOrigin: "center center",
            maskImage: "radial-gradient(ellipse 45% 50% at 50% 35%, black 0%, transparent 100%)",
            WebkitMaskImage: "radial-gradient(ellipse 45% 50% at 50% 35%, black 0%, transparent 100%)",
          }}
        />
      )}
    </AbsoluteFill>
  );
}