import { useState, useEffect, useCallback } from "react";
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  OffthreadVideo,
  Sequence,
  staticFile,
  useVideoConfig,
  useCurrentFrame,
  useDelayRender,
} from "remotion";

const IMAGE_EXT_RE = /\.(png|jpe?g|webp|gif|avif)$/i;
import { createTikTokStyleCaptions } from "@remotion/captions";
import type { Caption } from "@remotion/captions";
import { CaptionPage } from "./CaptionPage";
import type { EditPlan, CutSegment } from "../types";

const SWITCH_CAPTIONS_EVERY_MS = 1500;
const MAIN_VIDEO_VOLUME = 1.6;

// Subtle punch-in at each cut point. A human editor nudges the scale on a cut so
// the jump reads as intentional rather than a jarring jump-cut. Kept gentle —
// ~3.5% over ~0.23s, easing out. Applied only to segments after the first.
const CUT_PUNCH_SCALE = 1.035;
const CUT_PUNCH_FRAMES = 7;

type Niche = "ds" | "life" | "poetry";

interface Grading {
  filter: string;
  overlayColor: string | null;
}

function gradingFor(niche: Niche): Grading {
  if (niche === "ds") {
    return {
      filter: "contrast(1.08) saturate(1.10) brightness(1.0) hue-rotate(3deg)",
      overlayColor: "rgba(120, 180, 255, 0.05)",
    };
  }
  return {
    filter: "contrast(1.06) saturate(1.18) brightness(1.02) hue-rotate(-3deg)",
    overlayColor: "rgba(255, 180, 120, 0.05)",
  };
}

const NOISE_SVG_URL =
  "url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/></filter><rect width='100%25' height='100%25' filter='url(%23n)'/></svg>\")";

interface FilmGrainOverlayProps {
  niche: Niche;
}

function FilmGrainOverlay({ niche }: FilmGrainOverlayProps) {
  const frame = useCurrentFrame();
  if (niche === "ds") return null;

  const grainOpacity = niche === "poetry" ? 0.08 : 0.04;
  const vignetteOpacity = niche === "poetry" ? 0.18 : 0.10;
  const offset = (frame % 8) * 2;

  return (
    <>
      <AbsoluteFill
        style={{
          backgroundImage: NOISE_SVG_URL,
          backgroundSize: "300px 300px",
          backgroundPosition: `${offset}px ${offset}px`,
          opacity: grainOpacity,
          mixBlendMode: "overlay",
          pointerEvents: "none",
        }}
      />
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,${vignetteOpacity}) 100%)`,
          pointerEvents: "none",
        }}
      />
    </>
  );
}

export interface TalkingHeadEditProps extends Record<string, unknown> {
  editPlanFile: string;
}

interface CameraSegmentProps {
  src: string;
  trimBefore: number;
  trimAfter: number;
  filter: string;
  /** True for cut points (every segment after the first) — applies the punch-in. */
  punchIn: boolean;
}

/** One keep-segment of camera footage, with a subtle scale punch-in on cuts. */
function CameraSegment({ src, trimBefore, trimAfter, filter, punchIn }: CameraSegmentProps) {
  const frame = useCurrentFrame();
  const scale = punchIn
    ? interpolate(frame, [0, CUT_PUNCH_FRAMES], [CUT_PUNCH_SCALE, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
        easing: Easing.out(Easing.cubic),
      })
    : 1;

  return (
    <OffthreadVideo
      src={src}
      trimBefore={trimBefore}
      trimAfter={trimAfter}
      volume={MAIN_VIDEO_VOLUME}
      style={{
        width: "100%",
        height: "100%",
        objectFit: "cover",
        filter,
        transform: `scale(${scale})`,
      }}
    />
  );
}

function getSegments(plan: EditPlan): CutSegment[] {
  if (plan.cutSegments && plan.cutSegments.length > 0) return plan.cutSegments;
  return [{ startSec: plan.silenceTrimStartSec, endSec: plan.silenceTrimEndSec }];
}

/**
 * Maps a timestamp in original video time to a frame in the edit timeline.
 * Returns null if the timestamp falls inside a cut region.
 */
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

export function TalkingHeadEdit({ editPlanFile }: TalkingHeadEditProps) {
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
  const grading = gradingFor(plan.niche);

  // Build segment layout: each segment's position in the edit timeline
  const segmentLayouts = (() => {
    let cumulative = 0;
    return segments.map((seg) => {
      const startFrame = Math.floor(seg.startSec * fps);
      const endFrame = Math.ceil(seg.endSec * fps);
      const durationFrames = endFrame - startFrame;
      const editOffset = cumulative;
      cumulative += durationFrames;
      return { seg, startFrame, endFrame, durationFrames, editOffset };
    });
  })();

  const { pages } = createTikTokStyleCaptions({
    captions,
    combineTokensWithinMilliseconds: SWITCH_CAPTIONS_EVERY_MS,
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {/* Stitched camera footage — one <Video> per keep-segment */}
      {segmentLayouts.map(({ seg, startFrame, endFrame, durationFrames, editOffset }, i) => (
        <Sequence key={`seg-${i}`} from={editOffset} durationInFrames={durationFrames}>
          <CameraSegment
            src={staticFile(plan.rawVideo)}
            trimBefore={startFrame}
            trimAfter={endFrame}
            filter={grading.filter}
            punchIn={i > 0}
          />
        </Sequence>
      ))}

      {/* Per-niche color tint overlay (above camera, below b-roll) */}
      {grading.overlayColor && (
        <AbsoluteFill
          style={{
            backgroundColor: grading.overlayColor,
            mixBlendMode: "soft-light",
            pointerEvents: "none",
          }}
        />
      )}

      {/* B-roll overlays — full opacity, hides talking head completely.
          Images (.png/.jpg/etc.) for ds [SCREEN:] cues use <Img>; videos use <OffthreadVideo>. */}
      {plan.brollCues.map((cue) => {
        const editFrame = originalSecToEditFrame(cue.startSec, segments, fps);
        if (editFrame === null || editFrame < 0) return null;
        const durationFrames = Math.ceil(cue.durationSec * fps);
        const isImage = IMAGE_EXT_RE.test(cue.clipFile);
        const mediaStyle = {
          width: "100%",
          height: "100%",
          objectFit: "contain" as const,  // contain for code screenshots, avoid crop
          opacity: 1,
        };

        return (
          <Sequence key={cue.id} from={editFrame} durationInFrames={durationFrames}>
            <AbsoluteFill style={{ backgroundColor: "#000" }}>
              {isImage ? (
                <Img src={staticFile(cue.clipFile)} style={mediaStyle} />
              ) : (
                <OffthreadVideo
                  src={staticFile(cue.clipFile)}
                  muted
                  style={{ ...mediaStyle, objectFit: "cover" }}
                />
              )}
            </AbsoluteFill>
          </Sequence>
        );
      })}

      {/* Film grain + vignette (poetry strong, life subtle, ds none). Under captions. */}
      <FilmGrainOverlay niche={plan.niche} />

      {/* Animated captions — only rendered when showSubtitles: true in edit plan */}
      {plan.showSubtitles && pages.map((page, index) => {
        const editFrame = originalSecToEditFrame(page.startMs / 1000, segments, fps);
        if (editFrame === null) return null;

        const nextPage = pages[index + 1] ?? null;
        const nextEditFrame = nextPage
          ? originalSecToEditFrame(nextPage.startMs / 1000, segments, fps)
          : null;

        const endFrame =
          nextEditFrame !== null
            ? nextEditFrame
            : editFrame + Math.ceil((SWITCH_CAPTIONS_EVERY_MS / 1000) * fps);

        const durationInFrames = endFrame - editFrame;
        if (durationInFrames <= 0) return null;

        return (
          <Sequence key={index} from={editFrame} durationInFrames={durationInFrames}>
            <CaptionPage page={page} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
}
