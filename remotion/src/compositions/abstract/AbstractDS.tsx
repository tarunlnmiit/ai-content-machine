import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS } from "../../styles/chronixel";

const ACCENT = "#f97316";
const ACCENT_DIM = "rgba(249,115,22,0.35)";
const ACCENT_FAINT = "rgba(249,115,22,0.08)";

// Deterministic pseudo-random seeded by index
function pr(seed: number): number {
  const x = Math.sin(seed + 1) * 43758.5453;
  return x - Math.floor(x);
}

interface Node {
  x: number;
  y: number;
  vx: number;
  vy: number;
}

function nodeAt(i: number, frame: number): Node {
  const baseX = pr(i * 3) * 100;
  const baseY = pr(i * 3 + 1) * 100;
  const speed = 0.008 + pr(i * 3 + 2) * 0.012;
  const angle = pr(i * 7) * Math.PI * 2;
  return {
    x: baseX + Math.sin(frame * speed + angle) * 6,
    y: baseY + Math.cos(frame * speed * 0.7 + angle) * 5,
    vx: 0,
    vy: 0,
  };
}

const NODE_COUNT = 22;
const CONNECT_DIST = 28; // percent units

const DATA_FRAGMENTS = [
  "0x4f2a", "3.14", "import", "df.head()", "model.fit()", "[]", "{}",
  "lambda", "→", "0.98", "GPU", "API", "json", "pd", "np", "sklearn",
];

export interface AbstractDSProps extends Record<string, unknown> {
  /** unused — exists so Root.tsx can register with defaultProps */
  _placeholder?: boolean;
}

export function AbstractDS(_props: AbstractDSProps) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  const nodes = Array.from({ length: NODE_COUNT }, (_, i) => nodeAt(i, frame));

  // Scrolling data stream — 6 columns
  const columns = Array.from({ length: 6 }, (_, col) => ({
    x: 8 + col * 14.5,
    fragments: Array.from({ length: 10 }, (_, row) => {
      const idx = (col * 10 + row + Math.floor(frame / 8)) % DATA_FRAGMENTS.length;
      const opacity = 0.06 + pr(col * 100 + row + Math.floor(frame / 4)) * 0.12;
      return { text: DATA_FRAGMENTS[idx], y: ((row * 10 + (frame * 0.3)) % 100), opacity };
    }),
  }));

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg, overflow: "hidden" }}>
      <svg
        width="100%"
        height="100%"
        viewBox="0 0 100 56.25"
        preserveAspectRatio="xMidYMid slice"
        style={{ position: "absolute", inset: 0 }}
      >
        {/* Ambient grid */}
        <defs>
          <pattern id="grid-ds" width="5" height="5" patternUnits="userSpaceOnUse">
            <path d="M 5 0 L 0 0 0 5" fill="none" stroke={ACCENT_FAINT} strokeWidth="0.1" />
          </pattern>
        </defs>
        <rect width="100" height="56.25" fill="url(#grid-ds)" />

        {/* Connection lines between nearby nodes */}
        {nodes.map((a, i) =>
          nodes.slice(i + 1).map((b, j) => {
            const dx = a.x - b.x;
            const dy = a.y - b.y * (56.25 / 100);
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist > CONNECT_DIST) return null;
            const opacity = (1 - dist / CONNECT_DIST) * 0.3;
            return (
              <line
                key={`${i}-${j}`}
                x1={a.x}
                y1={a.y * 0.5625}
                x2={b.x}
                y2={b.y * 0.5625}
                stroke={ACCENT_DIM}
                strokeWidth="0.08"
                opacity={opacity}
              />
            );
          })
        )}

        {/* Nodes */}
        {nodes.map((n, i) => {
          const pulse = 0.5 + 0.5 * Math.sin(t * 2 + i * 0.8);
          return (
            <circle
              key={i}
              cx={n.x}
              cy={n.y * 0.5625}
              r={0.25 + pulse * 0.15}
              fill={ACCENT}
              opacity={0.6 + pulse * 0.4}
            />
          );
        })}
      </svg>

      {/* Scrolling data fragments */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          overflow: "hidden",
          pointerEvents: "none",
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: 11,
          color: ACCENT,
        }}
      >
        {columns.map((col, ci) =>
          col.fragments.map((frag, fi) => (
            <div
              key={`${ci}-${fi}`}
              style={{
                position: "absolute",
                left: `${col.x}%`,
                top: `${frag.y}%`,
                opacity: frag.opacity,
                whiteSpace: "nowrap",
                letterSpacing: "0.04em",
                transform: "translateY(-50%)",
              }}
            >
              {frag.text}
            </div>
          ))
        )}
      </div>

      {/* Center vignette */}
      <AbsoluteFill
        style={{
          background: "radial-gradient(ellipse 50% 50% at 50% 50%, transparent 30%, rgba(10,10,15,0.7) 100%)",
          pointerEvents: "none",
        }}
      />
    </AbsoluteFill>
  );
}
