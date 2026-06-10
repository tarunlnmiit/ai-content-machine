import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import * as THREE from "three";
import { useMemo } from "react";
import { COLORS } from "../../styles/chronixel";

const ACCENT = "#f59e0b";
const PARTICLE_COUNT = 220;

function pr(seed: number): number {
  const x = Math.sin(seed + 1) * 43758.5453;
  return x - Math.floor(x);
}

const BASE_PARTICLES = Array.from({ length: PARTICLE_COUNT }, (_, i) => ({
  x: (pr(i * 5) * 2 - 1) * 3.2,
  y: (pr(i * 5 + 1) * 2 - 1) * 2.4,
  z: (pr(i * 5 + 2) * 2 - 1) * 1.8,
  speed: 0.08 + pr(i * 5 + 3) * 0.12,
  phase: pr(i * 5 + 4) * Math.PI * 2,
}));

interface ParticleFieldProps {
  frame: number;
  fps: number;
}

function ParticleField({ frame, fps }: ParticleFieldProps) {
  const t = frame / fps;

  const positions = useMemo(() => {
    const arr = new Float32Array(PARTICLE_COUNT * 3);
    BASE_PARTICLES.forEach((b, i) => {
      arr[i * 3]     = b.x + Math.sin(t * b.speed + b.phase) * 0.12;
      arr[i * 3 + 1] = b.y + Math.cos(t * b.speed * 0.8 + b.phase) * 0.09;
      arr[i * 3 + 2] = b.z + Math.sin(t * 0.05 + i * 0.22) * 0.05;
    });
    return arr;
  }, [t]);

  return (
    <>
      <points>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={PARTICLE_COUNT}
            array={positions}
            itemSize={3}
          />
        </bufferGeometry>
        <pointsMaterial
          color={ACCENT}
          size={0.055}
          sizeAttenuation
          transparent
          opacity={0.75}
        />
      </points>
      <mesh>
        <sphereGeometry args={[0.3, 16, 16]} />
        <meshStandardMaterial
          color={ACCENT}
          emissive={ACCENT}
          emissiveIntensity={0.4}
          transparent
          opacity={0.15}
        />
      </mesh>
    </>
  );
}

export interface AbstractLifeProps extends Record<string, unknown> {
  _placeholder?: boolean;
}

export function AbstractLife(_props: AbstractLifeProps) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg }}>
      <ThreeCanvas>
        <ambientLight intensity={0.2} color={ACCENT} />
        <pointLight position={[0, 0, 0]} intensity={4} color={ACCENT} distance={8} />
        <ParticleField frame={frame} fps={fps} />
      </ThreeCanvas>

      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse 60% 55% at 50% 50%, rgba(245,158,11,0.07) 0%, transparent 70%)`,
          pointerEvents: "none",
        }}
      />
      <AbsoluteFill
        style={{
          background: "radial-gradient(ellipse 65% 65% at 50% 50%, transparent 40%, rgba(10,10,15,0.75) 100%)",
          pointerEvents: "none",
        }}
      />
    </AbsoluteFill>
  );
}
