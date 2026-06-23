import { useState, useEffect, useCallback } from "react";
import {
  AbsoluteFill,
  Audio,
  Sequence,
  staticFile,
  useVideoConfig,
  useDelayRender,
} from "remotion";
import type { Niche } from "../styles/chronixel";
import type { ScenePlan } from "../types";
import { SceneFade, SceneRenderer } from "./SceneRenderer";

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
          <SceneRenderer plan={scene} niche={niche} />
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
