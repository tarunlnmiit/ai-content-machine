import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { useMemo } from "react";

const AURORA_COUNT = 300;

function pr(seed: number): number {
  const x = Math.sin(seed + 1) * 43758.5453;
  return x - Math.floor(x);
}

const BASE_AURORA = Array.from({ length: AURORA_COUNT }, (_, i) => ({
  u: pr(i * 7) * 6 - 3,
  v: pr(i * 7 + 1) * 3.6 - 1.8,
  z: pr(i * 7 + 2) * 1.6 - 0.8,
  speed: 0.25 + pr(i * 7 + 3) * 0.35,
  phase: pr(i * 7 + 4) * Math.PI * 2,
  waveFreq: 0.6 + pr(i * 7 + 5) * 0.8,
  colorMix: pr(i * 7 + 6),
}));

// Static colors — computed once
const STATIC_COLORS = (() => {
  const arr = new Float32Array(AURORA_COUNT * 3);
  BASE_AURORA.forEach((b, i) => {
    arr[i * 3]     = 0.51 + b.colorMix * 0.15;
    arr[i * 3 + 1] = 0.33 + b.colorMix * 0.22;
    arr[i * 3 + 2] = 0.98;
  });
  return arr;
})();

interface AuroraParticlesProps {
  frame: number;
  fps: number;
}

function AuroraParticles({ frame, fps }: AuroraParticlesProps) {
  const t = frame / fps;

  const positions = useMemo(() => {
    const arr = new Float32Array(AURORA_COUNT * 3);
    BASE_AURORA.forEach((b, i) => {
      const wave = 0.45 * Math.sin(b.u * b.waveFreq + t * b.speed + b.phase);
      arr[i * 3]     = b.u;
      arr[i * 3 + 1] = b.v + wave;
      arr[i * 3 + 2] = b.z;
    });
    return arr;
  }, [t]);

  return (
    <points>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={AURORA_COUNT}
          array={positions}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-color"
          count={AURORA_COUNT}
          array={STATIC_COLORS}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.048}
        sizeAttenuation
        transparent
        opacity={0.82}
        vertexColors
      />
    </points>
  );
}

export interface AbstractPoetryProps extends Record<string, unknown> {
  _placeholder?: boolean;
}

export function AbstractPoetry(_props: AbstractPoetryProps) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill style={{ backgroundColor: "#06040f" }}>
      <ThreeCanvas>
        <ambientLight intensity={0.08} color="#a78bfa" />
        <pointLight position={[0, 1, 2]} intensity={1.5} color="#a78bfa" distance={6} />
        <AuroraParticles frame={frame} fps={fps} />
      </ThreeCanvas>

      <AbsoluteFill
        style={{
          background: "radial-gradient(ellipse 60% 60% at 50% 50%, transparent 35%, rgba(6,4,15,0.85) 100%)",
          pointerEvents: "none",
        }}
      />
    </AbsoluteFill>
  );
}
