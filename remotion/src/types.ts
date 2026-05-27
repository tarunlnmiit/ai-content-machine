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

export interface EditPlan {
  slug: string;
  niche: "ds" | "life" | "poetry";
  rawVideo: string; // relative to public/
  durationSec: number;
  silenceTrimStartSec: number;
  silenceTrimEndSec: number;
  cutSegments?: CutSegment[]; // if present, overrides silenceTrim fields
  brollCues: BrollCue[];
  captionsFile: string; // relative to public/
}
