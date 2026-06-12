import { useState, useEffect, useCallback, type ReactNode, type CSSProperties } from "react";
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
import { TitleCard } from "./TitleCard";
import { LowerThird } from "./LowerThird";
import { OutroCard } from "./OutroCard";
import type { EditPlan, CutSegment, ScenePlan } from "../types";
import type { Niche } from "../styles/chronixel";
import { SceneRenderer } from "./SceneRenderer";

const SWITCH_CAPTIONS_EVERY_MS = 1500;
const MAIN_VIDEO_VOLUME = 1.6;

const CUT_PUNCH_SCALE = 1.035;
const CUT_PUNCH_FRAMES = 7;

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

function resolveGrading(plan: EditPlan): Grading {
  if (plan.colorGrading) {
    const { saturate, hueRotate, contrast, brightness, overlayColor } = plan.colorGrading;
    return {
      filter: `contrast(${contrast}) saturate(${saturate}) brightness(${brightness}) hue-rotate(${hueRotate}deg)`,
      overlayColor,
    };
  }
  return gradingFor(plan.niche);
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

const PANEL_TRANSITION_FRAMES = 12;
const PANEL_FRACTION = 1 / 3;
const PANEL_TOP_FRACTION = 0.30;

interface PanelRange {
  from: number;
  duration: number;
  side: "left" | "right" | "top";
}

function PanelShiftWrapper({ children, ranges }: { children: ReactNode; ranges: PanelRange[] }) {
  const frame = useCurrentFrame();
  const active = ranges.find((r) => frame >= r.from && frame < r.from + r.duration) ?? null;

  let frac = 0;
  if (active) {
    const t =
      Math.min(frame - active.from, active.from + active.duration - frame, PANEL_TRANSITION_FRAMES) /
      PANEL_TRANSITION_FRAMES;
    const targetFrac = active.side === "top" ? PANEL_TOP_FRACTION : PANEL_FRACTION;
    frac = interpolate(t, [0, 1], [0, targetFrac], {
      easing: Easing.out(Easing.cubic),
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
  }

  const style: CSSProperties =
    frac > 0 && active
      ? active.side === "left"
        ? { position: "absolute", left: `${frac * 100}%`, top: 0, bottom: 0, right: 0 }
        : active.side === "right"
        ? { position: "absolute", left: 0, top: 0, bottom: 0, right: `${frac * 100}%` }
        : { position: "absolute", left: 0, right: 0, top: `${frac * 100}%`, bottom: 0 }
      : { position: "absolute", inset: 0 };

  return <div style={style}>{children}</div>;
}

export interface TalkingHeadEditProps extends Record<string, unknown> {
  editPlanFile: string;
}

interface CameraSegmentProps {
  src: string;
  trimBefore: number;
  trimAfter: number;
  filter: string;
  punchIn: boolean;
}

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
  const [overlayScenes, setOverlayScenes] = useState<ScenePlan[] | null>(null);
  const { delayRender, continueRender, cancelRender } = useDelayRender();
  const [handle] = useState(() => delayRender());

  const load = useCallback(async () => {
    try {
      const planRes = await fetch(staticFile(editPlanFile));
      const planData: EditPlan = await planRes.json();
      setPlan(planData);

      const captionRes = await fetch(staticFile(planData.captionsFile));
      const captionData: Caption[] = captionRes.ok ? await captionRes.json() : [];
      setCaptions(captionData);

      if (planData.scenePlanFile) {
        try {
          const sceneRes = await fetch(staticFile(planData.scenePlanFile));
          const sceneData: ScenePlan[] = await sceneRes.json();
          setOverlayScenes(sceneData.filter((s) => s.atSec !== undefined));
        } catch {
          // overlay scene plan is optional — skip silently if missing or malformed
        }
      }

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
  const grading = resolveGrading(plan);

  const titleCardFrames = plan.titleCard?.durationFrames ?? 0;

  // Split overlay scenes into panel (side/top) and fullscreen
  const panelRanges: PanelRange[] = [];
  const fullscreenOverlays: ScenePlan[] = [];
  if (overlayScenes) {
    for (const scene of overlayScenes) {
      const ef = originalSecToEditFrame(scene.atSec!, segments, fps);
      if (ef === null || ef < 0) continue;
      const from = ef + titleCardFrames;
      const duration = Math.ceil(scene.durationSec * fps);
      if (scene.layout === "panel-left" || scene.layout === "panel-right" || scene.layout === "panel-top") {
        const side = scene.layout === "panel-left" ? "left" : scene.layout === "panel-right" ? "right" : "top";
        panelRanges.push({ from, duration, side });
      } else {
        fullscreenOverlays.push(scene);
      }
    }
  }
  const outroCardFrames = plan.outroCard?.durationFrames ?? 0;

  // Build segment layout with optional titleCard offset
  const segmentLayouts = (() => {
    let cumulative = titleCardFrames;
    return segments.map((seg) => {
      const startFrame = Math.floor(seg.startSec * fps);
      const endFrame = Math.ceil(seg.endSec * fps);
      const durationFrames = endFrame - startFrame;
      const editOffset = cumulative;
      cumulative += durationFrames;
      return { seg, startFrame, endFrame, durationFrames, editOffset };
    });
  })();

  const editBodyEnd =
    segmentLayouts.length > 0
      ? segmentLayouts[segmentLayouts.length - 1].editOffset +
        segmentLayouts[segmentLayouts.length - 1].durationFrames
      : titleCardFrames;

  const { pages } = createTikTokStyleCaptions({
    captions,
    combineTokensWithinMilliseconds: SWITCH_CAPTIONS_EVERY_MS,
  });

  const bgColor = plan.greenScreen ? "#00FF00" : "#000";

  return (
    <AbsoluteFill style={{ backgroundColor: bgColor }}>
      {/* Optional TitleCard at start */}
      {plan.titleCard && (
        <Sequence from={plan.titleCard.insertAtFrame} durationInFrames={titleCardFrames}>
          <TitleCard
            titleText={plan.titleCard.titleText}
            showName={plan.titleCard.showName}
            durationInFrames={titleCardFrames}
            niche={plan.niche}
          />
        </Sequence>
      )}

      {/* Stitched camera footage — shifts to make room for panel overlays */}
      <PanelShiftWrapper ranges={panelRanges}>
        {segmentLayouts.map(({ seg, startFrame, endFrame, durationFrames, editOffset }, i) => (
          <Sequence key={`seg-${i}`} from={editOffset} durationInFrames={durationFrames}>
            <CameraSegment
              src={staticFile(plan.rawVideo)}
              trimBefore={startFrame}
              trimAfter={endFrame}
              filter={plan.greenScreen ? "none" : grading.filter}
              punchIn={i > 0}
            />
          </Sequence>
        ))}
      </PanelShiftWrapper>

      {/* Per-niche color tint (above camera, below b-roll) */}
      {!plan.greenScreen && grading.overlayColor && (
        <AbsoluteFill
          style={{
            backgroundColor: grading.overlayColor,
            mixBlendMode: "soft-light",
            pointerEvents: "none",
          }}
        />
      )}

      {/* B-roll overlays */}
      {plan.brollCues.map((cue) => {
        const editFrame = originalSecToEditFrame(cue.startSec, segments, fps);
        if (editFrame === null || editFrame < 0) return null;
        const durationFrames = Math.ceil(cue.durationSec * fps);
        const isImage = IMAGE_EXT_RE.test(cue.clipFile);
        const mediaStyle = {
          width: "100%",
          height: "100%",
          objectFit: "contain" as const,
          opacity: 1,
        };

        return (
          <Sequence key={cue.id} from={editFrame + titleCardFrames} durationInFrames={durationFrames}>
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

      {/* Panel overlays — scene in constrained 1/3 div; camera shifts via PanelShiftWrapper */}
      {overlayScenes && overlayScenes
        .filter((s) => s.layout === "panel-left" || s.layout === "panel-right" || s.layout === "panel-top")
        .map((scene) => {
          const ef = originalSecToEditFrame(scene.atSec!, segments, fps);
          if (ef === null || ef < 0) return null;
          const panelStyle: CSSProperties =
            scene.layout === "panel-top"
              ? { position: "absolute", top: 0, left: 0, right: 0, height: `${PANEL_TOP_FRACTION * 100}%`, overflow: "hidden" }
              : {
                  position: "absolute",
                  ...(scene.layout === "panel-left" ? { left: 0 } : { right: 0 }),
                  top: 0,
                  bottom: 0,
                  width: `${PANEL_FRACTION * 100}%`,
                  overflow: "hidden",
                };
          return (
            <Sequence key={`panel-${scene.sceneId}`} from={ef + titleCardFrames} durationInFrames={Math.ceil(scene.durationSec * fps)}>
              <div style={panelStyle}>
                <SceneRenderer plan={scene} niche={plan.niche} />
              </div>
            </Sequence>
          );
        })
      }

      {/* Fullscreen overlays — replace talking head entirely */}
      {fullscreenOverlays.map((scene) => {
        const ef = originalSecToEditFrame(scene.atSec!, segments, fps);
        if (ef === null || ef < 0) return null;
        return (
          <Sequence key={`fs-${scene.sceneId}`} from={ef + titleCardFrames} durationInFrames={Math.ceil(scene.durationSec * fps)}>
            <AbsoluteFill>
              <SceneRenderer plan={scene} niche={plan.niche} />
            </AbsoluteFill>
          </Sequence>
        );
      })}

      {/* Film grain + vignette */}
      {!plan.greenScreen && <FilmGrainOverlay niche={plan.niche} />}

      {/* Optional LowerThird overlay */}
      {plan.lowerThird && (
        <Sequence
          from={plan.lowerThird.insertAtFrame + titleCardFrames}
          durationInFrames={plan.lowerThird.durationFrames}
        >
          <LowerThird
            text={plan.lowerThird.text}
            durationInFrames={plan.lowerThird.durationFrames}
            niche={plan.niche}
          />
        </Sequence>
      )}

      {/* Animated captions */}
      {plan.showSubtitles && pages.map((page, index) => {
        const rawEditFrame = originalSecToEditFrame(page.startMs / 1000, segments, fps);
        if (rawEditFrame === null) return null;
        const editFrame = rawEditFrame + titleCardFrames;

        const nextPage = pages[index + 1] ?? null;
        const nextRawFrame = nextPage
          ? originalSecToEditFrame(nextPage.startMs / 1000, segments, fps)
          : null;

        const endFrame =
          nextRawFrame !== null
            ? nextRawFrame + titleCardFrames
            : editFrame + Math.ceil((SWITCH_CAPTIONS_EVERY_MS / 1000) * fps);

        const durationInFrames = endFrame - editFrame;
        if (durationInFrames <= 0) return null;

        return (
          <Sequence key={index} from={editFrame} durationInFrames={durationInFrames}>
            <CaptionPage page={page} />
          </Sequence>
        );
      })}

      {/* Optional OutroCard appended after edit body */}
      {plan.outroCard && (
        <Sequence from={editBodyEnd} durationInFrames={outroCardFrames}>
          <OutroCard
            nextText={plan.outroCard.nextText}
            episodeTitle={plan.outroCard.episodeTitle}
            durationInFrames={outroCardFrames}
            niche={plan.niche}
          />
        </Sequence>
      )}
    </AbsoluteFill>
  );
}
