import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import * as THREE from "three";
import { COLORS } from "../../styles/chronixel";

const ACCENT = "#f97316";

function pr(seed: number): number {
  const x = Math.sin(seed + 1) * 43758.5453;
  return x - Math.floor(x);
}

const NODE_COUNT = 22;
const CONNECT_DIST = 2.2;

// Static base positions distributed on a sphere
const BASE_POSITIONS: THREE.Vector3[] = Array.from({ length: NODE_COUNT }, (_, i) => {
  const theta = pr(i * 3) * Math.PI * 2;
  const phi = Math.acos(2 * pr(i * 3 + 1) - 1);
  const r = 1.2 + pr(i * 3 + 2) * 1.4;
  return new THREE.Vector3(
    r * Math.sin(phi) * Math.cos(theta),
    r * Math.sin(phi) * Math.sin(theta),
    r * Math.cos(phi)
  );
});

const DATA_FRAGMENTS = [
  "0x4f2a", "3.14", "import", "df.head()", "model.fit()", "[]", "{}",
  "lambda", "→", "0.98", "GPU", "API", "json", "pd", "np", "sklearn",
];

interface NetworkSceneProps {
  frame: number;
  fps: number;
}

function NetworkScene({ frame, fps }: NetworkSceneProps) {
  const t = frame / fps;
  const rotation = t * 0.12;

  const nodes = BASE_POSITIONS.map((base, i) => {
    const w = 0.06;
    return new THREE.Vector3(
      base.x + Math.sin(t * (0.4 + pr(i * 3) * 0.3) + i) * w,
      base.y + Math.cos(t * (0.35 + pr(i * 3 + 1) * 0.25) + i) * w,
      base.z + Math.sin(t * 0.2 + i * 1.1) * w
    );
  });

  const edges: Array<{ points: [THREE.Vector3, THREE.Vector3]; opacity: number }> = [];
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const dist = nodes[i].distanceTo(nodes[j]);
      if (dist < CONNECT_DIST) {
        edges.push({ points: [nodes[i], nodes[j]], opacity: (1 - dist / CONNECT_DIST) * 0.35 });
      }
    }
  }

  return (
    <group rotation={[0.25, rotation, 0]}>
      <ambientLight intensity={0.15} />
      <pointLight position={[4, 4, 4]} intensity={2.5} color={ACCENT} />

      {edges.map(({ points, opacity }, i) => {
        const geo = new THREE.BufferGeometry().setFromPoints(points);
        const mat = new THREE.LineBasicMaterial({ color: ACCENT, transparent: true, opacity });
        return <primitive key={`e-${i}`} object={new THREE.Line(geo, mat)} />;
      })}

      {nodes.map((pos, i) => {
        const pulse = 0.5 + 0.5 * Math.sin(t * 2 + i * 0.8);
        return (
          <mesh key={`n-${i}`} position={pos}>
            <sphereGeometry args={[0.042 + pulse * 0.018, 10, 10]} />
            <meshStandardMaterial
              color={ACCENT}
              emissive={ACCENT}
              emissiveIntensity={0.55 + pulse * 0.45}
              roughness={0.3}
              metalness={0.7}
            />
          </mesh>
        );
      })}
    </group>
  );
}

export interface AbstractDSProps extends Record<string, unknown> {
  _placeholder?: boolean;
}

export function AbstractDS(_props: AbstractDSProps) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const columns = Array.from({ length: 6 }, (_, col) => ({
    x: 8 + col * 14.5,
    fragments: Array.from({ length: 10 }, (_, row) => {
      const idx = (col * 10 + row + Math.floor(frame / 8)) % DATA_FRAGMENTS.length;
      const opacity = 0.06 + pr(col * 100 + row + Math.floor(frame / 4)) * 0.12;
      return { text: DATA_FRAGMENTS[idx], y: ((row * 10 + frame * 0.3) % 100), opacity };
    }),
  }));

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg }}>
      <ThreeCanvas>
        <NetworkScene frame={frame} fps={fps} />
      </ThreeCanvas>

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

      <AbsoluteFill
        style={{
          background: "radial-gradient(ellipse 50% 50% at 50% 50%, transparent 30%, rgba(10,10,15,0.7) 100%)",
          pointerEvents: "none",
        }}
      />
    </AbsoluteFill>
  );
}
