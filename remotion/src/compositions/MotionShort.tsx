import { useState, useEffect, useCallback } from "react";
import {
  AbsoluteFill,
  Audio,
  interpolate,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  useDelayRender,
} from "remotion";
import { COLORS, FONTS, type Niche, nicheAccent, nicheGrid } from "../styles/chronixel";
import type { ScenePlan } from "../types";

// Fade-between-scenes crossfade (12 frames)
const CROSSFADE_FRAMES = 12;

function SceneFade({ durationInFrames }: { durationInFrames: number }) {
  const frame = useCurrentFrame();
  const fadeIn = interpolate(frame, [0, CROSSFADE_FRAMES], [0, 1], { extrapolateRight: "clamp" });
  const fadeOut = interpolate(
    frame,
    [durationInFrames - CROSSFADE_FRAMES, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const opacity = Math.min(fadeIn, fadeOut);
  return (
    <AbsoluteFill
      style={{ backgroundColor: COLORS.bg, opacity: 1 - opacity, pointerEvents: "none" }}
    />
  );
}

interface PlaceholderSceneProps {
  plan: ScenePlan;
  niche: Niche;
}

function PlaceholderScene({ plan, niche }: PlaceholderSceneProps) {
  const accent = nicheAccent(niche);
  const grid = nicheGrid(niche);
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
          gap: 16,
          padding: 80,
          textAlign: "center",
        }}
      >
        <div
          style={{
            color: accent,
            fontSize: 13,
            fontFamily: FONTS.body,
            fontWeight: 600,
            letterSpacing: "0.14em",
            textTransform: "uppercase",
            opacity: 0.7,
          }}
        >
          {plan.componentName}
        </div>
        <div
          style={{
            color: COLORS.text,
            fontSize: 72,
            fontFamily: FONTS.heading,
            fontWeight: FONTS.headingWeight,
            lineHeight: 1.2,
            letterSpacing: "-0.02em",
          }}
        >
          {plan.script}
        </div>
      </div>
    </AbsoluteFill>
  );
}

export interface MotionShortProps extends Record<string, unknown> {
  scenePlanFile: string;
  niche: Niche;
  audioFile?: string;
}

export function MotionShort({ scenePlanFile, niche, audioFile }: MotionShortProps) {
  const { fps } = useVideoConfig();
  const [scenes, setScenes] = useState<ScenePlan[] | null>(null);
  const { delayRender, continueRender, cancelRender } = useDelayRender();
  const [handle] = useState(() => delayRender());

  const load = useCallback(async () => {
    try {
      const res = await fetch(staticFile(scenePlanFile));
      const data: ScenePlan[] = await res.json();
      setScenes(data);
      continueRender(handle);
    } catch (e) {
      cancelRender(e);
    }
  }, [scenePlanFile, handle, continueRender, cancelRender]);

  useEffect(() => {
    load();
  }, [load]);

  if (!scenes) return null;

  let offset = 0;
  const sceneLayouts = scenes.map((scene) => {
    const durationFrames = Math.round(scene.durationSec * fps);
    const from = offset;
    offset += durationFrames;
    return { scene, from, durationFrames };
  });

  const totalFrames = offset;

  return (
    <AbsoluteFill>
      {audioFile && (
        <Audio src={staticFile(audioFile)} startFrom={0} endAt={totalFrames} volume={1} />
      )}

      {sceneLayouts.map(({ scene, from, durationFrames }) => (
        <Sequence key={scene.sceneId} from={from} durationInFrames={durationFrames}>
          <PlaceholderScene plan={scene} niche={niche} />
          <SceneFade durationInFrames={durationFrames} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
}

// Niche-specific wrappers registered as distinct compositions
export interface DSMotionShortProps extends Record<string, unknown> {
  scenePlanFile: string;
  audioFile?: string;
}

export function DSMotionShort({ scenePlanFile, audioFile }: DSMotionShortProps) {
  return <MotionShort scenePlanFile={scenePlanFile} niche="ds" audioFile={audioFile} />;
}

export function LifeMotionShort({ scenePlanFile, audioFile }: DSMotionShortProps) {
  return <MotionShort scenePlanFile={scenePlanFile} niche="life" audioFile={audioFile} />;
}

export function PoetryMotionShort({ scenePlanFile, audioFile }: DSMotionShortProps) {
  return <MotionShort scenePlanFile={scenePlanFile} niche="poetry" audioFile={audioFile} />;
}
