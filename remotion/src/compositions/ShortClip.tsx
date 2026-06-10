import { useState, useEffect, useCallback } from "react";
import {
  AbsoluteFill,
  OffthreadVideo,
  Sequence,
  staticFile,
  useVideoConfig,
  useDelayRender,
} from "remotion";
import { createTikTokStyleCaptions } from "@remotion/captions";
import type { Caption } from "@remotion/captions";
import { CaptionPage } from "./CaptionPage";
import type { EditPlan, CutSegment } from "../types";

const SWITCH_CAPTIONS_EVERY_MS = 1500;
const SHORT_CAPTION_FONT_SIZE = 72;

export interface ShortClipProps extends Record<string, unknown> {
  editPlanFile: string;
  clipStartSec: number;
  clipEndSec: number;
  captionFontSize?: number;
}

function getSegments(plan: EditPlan): CutSegment[] {
  if (plan.cutSegments && plan.cutSegments.length > 0) return plan.cutSegments;
  return [{ startSec: plan.silenceTrimStartSec, endSec: plan.silenceTrimEndSec }];
}

function originalSecToEditFrame(
  originalSec: number,
  segments: CutSegment[],
  fps: number
): number | null {
  let cumulativeFrames = 0;
  for (const seg of segments) {
    if (originalSec < seg.startSec) return null;
    if (originalSec <= seg.endSec) {
      return cumulativeFrames + Math.floor((originalSec - seg.startSec) * fps);
    }
    cumulativeFrames += Math.ceil((seg.endSec - seg.startSec) * fps);
  }
  return null;
}

export function ShortClip({
  editPlanFile,
  clipStartSec,
  clipEndSec,
  captionFontSize = SHORT_CAPTION_FONT_SIZE,
}: ShortClipProps) {
  const { fps } = useVideoConfig();
  const [plan, setPlan] = useState<EditPlan | null>(null);
  const [captions, setCaptions] = useState<Caption[] | null>(null);
  const { delayRender, continueRender, cancelRender } = useDelayRender();
  const [handle] = useState(() => delayRender());

  const load = useCallback(async () => {
    try {
      const planRes = await fetch(staticFile(editPlanFile));
      const planData: EditPlan = await planRes.json();
      setPlan(planData);

      const captionRes = await fetch(staticFile(planData.captionsFile));
      const captionData: Caption[] = await captionRes.json();
      setCaptions(captionData);

      continueRender(handle);
    } catch (e) {
      cancelRender(e);
    }
  }, [editPlanFile, handle, continueRender, cancelRender]);

  useEffect(() => {
    load();
  }, [load]);

  if (!plan || !captions) return null;

  const segments = getSegments(plan);
  const clipDurationFrames = Math.ceil((clipEndSec - clipStartSec) * fps);

  const { pages } = createTikTokStyleCaptions({
    captions,
    combineTokensWithinMilliseconds: SWITCH_CAPTIONS_EVERY_MS,
  });

  // Filter captions to clip window
  const clippedPages = pages.filter(
    (p) => p.startMs / 1000 >= clipStartSec && p.startMs / 1000 < clipEndSec
  );

  return (
    <AbsoluteFill style={{ backgroundColor: "#000", overflow: "hidden" }}>
      {/* 9:16 center crop — OffthreadVideo fills the container, objectFit=cover crops to portrait */}
      <AbsoluteFill>
        <OffthreadVideo
          src={staticFile(plan.rawVideo)}
          trimBefore={Math.floor(clipStartSec * fps)}
          trimAfter={Math.ceil(clipEndSec * fps)}
          volume={1.6}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            objectPosition: "center center",
          }}
        />
      </AbsoluteFill>

      {/* Captions — larger font for Shorts format */}
      {clippedPages.map((page, index) => {
        const rawEditFrame = originalSecToEditFrame(page.startMs / 1000, segments, fps);
        if (rawEditFrame === null) return null;

        // Translate to clip-local frame
        const clipLocalFrame = Math.floor((page.startMs / 1000 - clipStartSec) * fps);
        if (clipLocalFrame < 0 || clipLocalFrame >= clipDurationFrames) return null;

        const nextPage = clippedPages[index + 1] ?? null;
        const nextLocalFrame = nextPage
          ? Math.floor((nextPage.startMs / 1000 - clipStartSec) * fps)
          : null;

        const endFrame =
          nextLocalFrame !== null
            ? nextLocalFrame
            : clipLocalFrame + Math.ceil((SWITCH_CAPTIONS_EVERY_MS / 1000) * fps);

        const durationInFrames = Math.min(endFrame, clipDurationFrames) - clipLocalFrame;
        if (durationInFrames <= 0) return null;

        return (
          <Sequence key={index} from={clipLocalFrame} durationInFrames={durationInFrames}>
            <CaptionPage page={page} fontSize={captionFontSize} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
}
