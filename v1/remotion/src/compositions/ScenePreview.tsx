import { useState, useEffect, useCallback } from "react";
import { staticFile, useDelayRender } from "remotion";
import type { ScenePlan } from "../types";
import { SceneRenderer } from "./SceneRenderer";

export interface ScenePreviewProps extends Record<string, unknown> {
  scenePlanFile: string;
}

export function ScenePreview({ scenePlanFile }: ScenePreviewProps) {
  const [scene, setScene] = useState<ScenePlan | null>(null);
  const { delayRender, continueRender, cancelRender } = useDelayRender();
  const [handle] = useState(() => delayRender());

  const load = useCallback(async () => {
    try {
      const res = await fetch(staticFile(scenePlanFile));
      if (!res.ok) throw new Error(`Scene plan not found: ${scenePlanFile}`);
      const data: ScenePlan[] = await res.json();
      setScene(data[0]);
      continueRender(handle);
    } catch (e) {
      cancelRender(e);
    }
  }, [scenePlanFile, handle, continueRender, cancelRender]);

  useEffect(() => {
    load();
  }, [load]);

  if (!scene) return null;
  return <SceneRenderer plan={scene} niche={scene.niche} />;
}
