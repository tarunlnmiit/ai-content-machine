import type { Niche } from "./styles/chronixel";

export type { Niche };

export interface BrollCue {
  id: string;
  description: string;
  startSec: number;
  durationSec: number;
  clipFile: string; // relative to public/
}

export interface CutSegment {
  startSec: number; // original video time
  endSec: number;
}

export interface TitleCardConfig {
  titleText: string;
  showName?: string;
  durationFrames: number;
  insertAtFrame: number; // 0 = video start
}

export interface LowerThirdConfig {
  text: string;
  durationFrames: number;
  insertAtFrame: number; // e.g. 90 = 3s in at 30fps
}

export interface OutroCardConfig {
  nextText: string;
  episodeTitle?: string;
  durationFrames: number; // appended after last segment
}

export interface EditPlan {
  slug: string;
  niche: Niche;
  rawVideo: string; // relative to public/
  durationSec: number;
  silenceTrimStartSec: number;
  silenceTrimEndSec: number;
  cutSegments?: CutSegment[]; // if present, overrides silenceTrim fields
  brollCues: BrollCue[];
  captionsFile: string; // relative to public/
  showSubtitles?: boolean;
  titleCard?: TitleCardConfig;
  lowerThird?: LowerThirdConfig;
  outroCard?: OutroCardConfig;
  scenePlanFile?: string;
  colorGrading?: ColorGrading;
  greenScreen?: boolean; // replace bg with #00FF00 for DaVinci keying
  webcamSplit?: "left" | "right" | null;
  outputSize?: "16x9" | "9x16" | "1x1";
}

export interface ColorGrading {
  saturate: number;
  hueRotate: number;
  contrast: number;
  brightness: number;
  overlayColor: string | null;
}

export interface ScenePlan {
  sceneId: string;
  componentName: string;
  script: string;
  niche: Niche;
  durationSec: number;
  props: Record<string, unknown>;
  atSec?: number;
  layout?: "fullscreen" | "panel-left" | "panel-right" | "panel-top";
}

export interface AudiogramPlan {
  audioFile: string; // relative to public/
  startSec: number;
  endSec: number;
  quote: string;
  speakerLabel?: string;
  niche: Niche;
  podcastName: string;
  outputSize: "1x1" | "9x16";
}
