import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";

const ACCENT = "#a78bfa";

function pr(seed: number): number {
  const x = Math.sin(seed + 1) * 43758.5453;
  return x - Math.floor(x);
}

export interface AbstractPoetryProps extends Record<string, unknown> {
  _placeholder?: boolean;
}

export function AbstractPoetry(_props: AbstractPoetryProps) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  // Aurora-style sweeping gradients — 3 layers, slow drift
  const aurora = [
    {
      cx: 20 + 30 * Math.sin(t * 0.08),
      cy: 40 + 20 * Math.cos(t * 0.05),
      color: "#a78bfa",
      opacity: 0.12 + 0.04 * Math.sin(t * 0.2),
    },
    {
      cx: 60 + 25 * Math.cos(t * 0.07),
      cy: 55 + 15 * Math.sin(t * 0.06),
      color: "#c4b5fd",
      opacity: 0.08 + 0.03 * Math.cos(t * 0.15),
    },
    {
      cx: 80 + 15 * Math.sin(t * 0.09 + 1),
      cy: 30 + 20 * Math.cos(t * 0.04),
      color: "#818cf8",
      opacity: 0.07 + 0.03 * Math.sin(t * 0.18),
    },
  ];

  // Floating dust motes
  const motes = Array.from({ length: 50 }, (_, i) => {
    const baseX = pr(i * 9) * 100;
    const baseY = pr(i * 9 + 1) * 100;
    const driftY = -(t * (0.3 + pr(i * 9 + 2) * 0.5)) % 100;
    const flicker = 0.3 + 0.4 * Math.sin(t * (1 + pr(i * 9 + 3) * 2) + i);
    return {
      cx: baseX + Math.sin(t * 0.25 + i * 0.7) * 1.5,
      cy: ((baseY + driftY) % 100 + 100) % 100,
      r: 0.3 + pr(i * 9 + 4) * 0.5,
      opacity: flicker * 0.35,
    };
  });

  // Ink diffusion blobs — organic shapes that grow slowly
  const blobs = Array.from({ length: 5 }, (_, i) => {
    const baseX = 15 + i * 18;
    const baseY = 20 + pr(i * 3) * 60;
    const scale = 0.6 + 0.4 * Math.sin(t * 0.12 + i * 1.2);
    const rx = (6 + pr(i * 3 + 1) * 8) * scale;
    const ry = (4 + pr(i * 3 + 2) * 6) * scale;
    const rotation = t * (2 + i) * (pr(i * 3 + 1) > 0.5 ? 1 : -1);
    return { cx: baseX, cy: baseY, rx, ry, rotation, opacity: 0.04 + pr(i * 3) * 0.04 };
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#06040f", overflow: "hidden" }}>
      <svg
        width="100%"
        height="100%"
        viewBox="0 0 100 56.25"
        preserveAspectRatio="xMidYMid slice"
        style={{ position: "absolute", inset: 0 }}
      >
        <defs>
          <filter id="blur-aurora">
            <feGaussianBlur stdDeviation="4" />
          </filter>
          <filter id="blur-blob">
            <feGaussianBlur stdDeviation="2.5" />
          </filter>
        </defs>

        {/* Aurora sweeps */}
        {aurora.map((a, i) => (
          <ellipse
            key={i}
            cx={a.cx}
            cy={a.cy * 0.5625}
            rx={35}
            ry={18}
            fill={a.color}
            opacity={a.opacity}
            filter="url(#blur-aurora)"
          />
        ))}

        {/* Ink blobs */}
        {blobs.map((b, i) => (
          <ellipse
            key={i}
            cx={b.cx}
            cy={b.cy * 0.5625}
            rx={b.rx}
            ry={b.ry * 0.5625}
            fill={ACCENT}
            opacity={b.opacity}
            filter="url(#blur-blob)"
            transform={`rotate(${b.rotation}, ${b.cx}, ${b.cy * 0.5625})`}
          />
        ))}

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

      {/* Deep center vignette */}
      <AbsoluteFill
        style={{
          background: "radial-gradient(ellipse 60% 60% at 50% 50%, transparent 35%, rgba(6,4,15,0.85) 100%)",
          pointerEvents: "none",
        }}
      />
    </AbsoluteFill>
  );
}
