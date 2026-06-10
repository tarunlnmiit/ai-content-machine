import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS } from "../../styles/chronixel";

const ACCENT = "#f59e0b";

function pr(seed: number): number {
  const x = Math.sin(seed + 1) * 43758.5453;
  return x - Math.floor(x);
}

const BOKEH_COUNT = 28;

export interface AbstractLifeProps extends Record<string, unknown> {
  _placeholder?: boolean;
}

export function AbstractLife(_props: AbstractLifeProps) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  // Bokeh circles — each drifts slowly
  const bokeh = Array.from({ length: BOKEH_COUNT }, (_, i) => {
    const baseX = pr(i * 5) * 100;
    const baseY = pr(i * 5 + 1) * 100;
    const radius = 3 + pr(i * 5 + 2) * 18;
    const speed = 0.006 + pr(i * 5 + 3) * 0.008;
    const phase = pr(i * 5 + 4) * Math.PI * 2;
    const opacity = 0.04 + pr(i * 7) * 0.10;
    return {
      cx: baseX + Math.sin(t * speed + phase) * 4,
      cy: baseY + Math.cos(t * speed * 0.8 + phase) * 3,
      r: radius,
      opacity,
    };
  });

  // Floating dust motes — tiny, high count
  const motes = Array.from({ length: 40 }, (_, i) => {
    const baseX = pr(i * 11) * 100;
    const baseY = pr(i * 11 + 1) * 100;
    const driftY = (t * (0.4 + pr(i * 11 + 2) * 0.6)) % 100;
    const opacity = 0.15 + pr(i * 11 + 3) * 0.25;
    return {
      cx: baseX + Math.sin(t * 0.3 + i) * 2,
      cy: (baseY + driftY) % 100,
      r: 0.4 + pr(i * 11 + 4) * 0.6,
      opacity,
    };
  });

  // Golden ratio spiral segments — static decorative element
  const PHI = 1.6180339887;
  const spiralPoints = Array.from({ length: 120 }, (_, i) => {
    const angle = i * 0.18;
    const radius = 0.8 * Math.pow(PHI, angle * 0.08);
    return {
      x: 50 + radius * Math.cos(angle),
      y: 50 + radius * Math.sin(angle) * 0.5625,
    };
  });
  const spiralPath = spiralPoints
    .map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y * 0.5625}`)
    .join(" ");

  const spiralOpacity = 0.06 + 0.02 * Math.sin(t * 0.5);

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg, overflow: "hidden" }}>
      <svg
        width="100%"
        height="100%"
        viewBox="0 0 100 56.25"
        preserveAspectRatio="xMidYMid slice"
        style={{ position: "absolute", inset: 0 }}
      >
        <defs>
          <radialGradient id="bokeh-grad" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor={ACCENT} stopOpacity="1" />
            <stop offset="100%" stopColor={ACCENT} stopOpacity="0" />
          </radialGradient>
        </defs>

        {/* Bokeh circles */}
        {bokeh.map((b, i) => (
          <ellipse
            key={i}
            cx={b.cx}
            cy={b.cy * 0.5625}
            rx={b.r}
            ry={b.r * 0.5625}
            fill={ACCENT}
            opacity={b.opacity}
          />
        ))}

        {/* Golden ratio spiral */}
        <path
          d={spiralPath}
          fill="none"
          stroke={ACCENT}
          strokeWidth="0.12"
          opacity={spiralOpacity}
        />

        {/* Dust motes */}
        {motes.map((m, i) => (
          <circle
            key={i}
            cx={m.cx}
            cy={m.cy * 0.5625}
            r={m.r}
            fill={ACCENT}
            opacity={m.opacity}
          />
        ))}
      </svg>

      {/* Warm center glow */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse 60% 55% at 50% 50%, rgba(245,158,11,0.08) 0%, transparent 70%)`,
          pointerEvents: "none",
        }}
      />

      {/* Edge vignette */}
      <AbsoluteFill
        style={{
          background: "radial-gradient(ellipse 65% 65% at 50% 50%, transparent 40%, rgba(10,10,15,0.75) 100%)",
          pointerEvents: "none",
        }}
      />
    </AbsoluteFill>
  );
}
