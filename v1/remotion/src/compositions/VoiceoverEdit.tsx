import { useState, useEffect, useCallback, type CSSProperties } from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  OffthreadVideo,
  Sequence,
  staticFile,
  useVideoConfig,
  useCurrentFrame,
  useDelayRender,
} from "remotion";
import type { EditPlan, ScenePlan } from "../types";
import type { Niche } from "../styles/chronixel";
import { SceneRenderer } from "./SceneRenderer";
import { TitleCard } from "./TitleCard";
import { OutroCard } from "./OutroCard";

const IMAGE_EXT_RE = /\.(png|jpe?g|webp|gif|avif)$/i;

interface Grading {
  filter: string;
  overlayColor: string | null;
}

// Mirrors TalkingHeadEdit's grading so the voiceover lane looks consistent.
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

function FilmGrainOverlay({ niche }: { niche: Niche }) {
  const frame = useCurrentFrame();
  if (niche === "ds") return null;
  const grainOpacity = niche === "poetry" ? 0.08 : 0.04;
  const vignetteOpacity = niche === "poetry" ? 0.18 : 0.1;
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

// ── Named looks ────────────────────────────────────────────────────────────

// Black letterbox bars. Landscape → 2.39:1 crop; portrait → thin stylistic bars.
function Letterbox() {
  const { width, height } = useVideoConfig();
  const isLandscape = width >= height;
  const barFrac = isLandscape
    ? Math.max(0, (1 - width / 2.39 / height) / 2) // (height - width/2.39)/2 as fraction
    : 0.06;
  const barPct = `${(barFrac * 100).toFixed(2)}%`;
  return (
    <>
      <AbsoluteFill style={{ top: 0, height: barPct, backgroundColor: "#000", pointerEvents: "none" }} />
      <AbsoluteFill style={{ top: "auto", bottom: 0, height: barPct, backgroundColor: "#000", pointerEvents: "none" }} />
    </>
  );
}

// Teal shadows / orange highlights + vignette. Letterbox added separately above.
function CinematicGrade() {
  return (
    <>
      <AbsoluteFill style={{ backgroundColor: "rgba(0,80,100,0.12)", mixBlendMode: "multiply", pointerEvents: "none" }} />
      <AbsoluteFill
        style={{
          background: "radial-gradient(ellipse 75% 65% at 50% 48%, rgba(255,150,60,0.12) 0%, transparent 60%)",
          mixBlendMode: "screen",
          pointerEvents: "none",
        }}
      />
      <AbsoluteFill
        style={{
          background: "radial-gradient(ellipse at center, transparent 45%, rgba(0,0,0,0.50) 100%)",
          pointerEvents: "none",
        }}
      />
    </>
  );
}

// Warm dreamy bloom + soft vignette + gentle grain.
function PoetryBloom() {
  const frame = useCurrentFrame();
  const offset = (frame % 8) * 2;
  return (
    <>
      <AbsoluteFill
        style={{
          background: "radial-gradient(ellipse 80% 70% at 50% 45%, rgba(255,200,140,0.18) 0%, transparent 62%)",
          mixBlendMode: "screen",
          pointerEvents: "none",
        }}
      />
      <AbsoluteFill
        style={{
          backgroundImage: NOISE_SVG_URL,
          backgroundSize: "300px 300px",
          backgroundPosition: `${offset}px ${offset}px`,
          opacity: 0.06,
          mixBlendMode: "overlay",
          pointerEvents: "none",
        }}
      />
      <AbsoluteFill
        style={{
          background: "radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,0.22) 100%)",
          pointerEvents: "none",
        }}
      />
    </>
  );
}

export interface VoiceoverEditProps extends Record<string, unknown> {
  editPlanFile: string;
}

// Audio-driven, B-roll-montage long-form / short composition.
// Captions are NOT rendered here — they are burned in later by hyperframes_render.py.
export function VoiceoverEdit({ editPlanFile }: VoiceoverEditProps) {
  const { fps } = useVideoConfig();
  const [plan, setPlan] = useState<EditPlan | null>(null);
  const [overlayScenes, setOverlayScenes] = useState<ScenePlan[]>([]);
  const { delayRender, continueRender, cancelRender } = useDelayRender();
  const [handle] = useState(() => delayRender());

  const load = useCallback(async () => {
    try {
      const planRes = await fetch(staticFile(editPlanFile));
      const planData: EditPlan = await planRes.json();
      setPlan(planData);

      if (planData.scenePlanFile) {
        try {
          const sceneRes = await fetch(staticFile(planData.scenePlanFile));
          const sceneData: ScenePlan[] = await sceneRes.json();
          setOverlayScenes(sceneData.filter((s) => s.atSec !== undefined));
        } catch {
          // overlay scene plan is optional — skip silently if missing/malformed
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

  if (!plan) return null;

  const grading = resolveGrading(plan);
  const titleCardFrames = plan.titleCard?.durationFrames ?? 0;
  const bodyFrames = Math.ceil(plan.durationSec * fps);
  const outroCardFrames = plan.outroCard?.durationFrames ?? 0;

  // Direct atSec → frame (no cutSegment remap in the voiceover lane).
  const atSecToFrame = (atSec: number) => Math.round(atSec * fps) + titleCardFrames;

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {/* Voiceover audio track — rides the whole body, after any title card */}
      {plan.audioFile && (
        <Sequence from={titleCardFrames} durationInFrames={bodyFrames}>
          <Audio src={staticFile(plan.audioFile)} volume={1} />
        </Sequence>
      )}

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

      {/* Full-screen B-roll montage — base layer tiling the whole timeline */}
      {plan.brollCues.map((cue) => {
        const from = Math.round(cue.startSec * fps) + titleCardFrames;
        const durationFrames = Math.ceil(cue.durationSec * fps);
        if (durationFrames <= 0) return null;
        const isImage = IMAGE_EXT_RE.test(cue.clipFile);
        return (
          <Sequence key={cue.id} from={from} durationInFrames={durationFrames}>
            <AbsoluteFill style={{ backgroundColor: "#000" }}>
              {isImage ? (
                <Img
                  src={staticFile(cue.clipFile)}
                  style={{ width: "100%", height: "100%", objectFit: "cover", filter: grading.filter }}
                />
              ) : (
                <OffthreadVideo
                  src={staticFile(cue.clipFile)}
                  muted
                  style={{ width: "100%", height: "100%", objectFit: "cover", filter: grading.filter }}
                />
              )}
            </AbsoluteFill>
          </Sequence>
        );
      })}

      {/* Per-niche color tint (above montage, below overlays) */}
      {grading.overlayColor && (
        <AbsoluteFill
          style={{
            backgroundColor: grading.overlayColor,
            mixBlendMode: "soft-light",
            pointerEvents: "none",
          }}
        />
      )}

      {/* Named look — duotone/bloom graded over the montage (below overlays) */}
      {plan.look === "cinematic" && <CinematicGrade />}
      {plan.look === "poetry" && <PoetryBloom />}

      {/* Overlay scenes — fullscreen replaces montage; lower-third sits in a bottom band */}
      {overlayScenes.map((scene) => {
        const from = atSecToFrame(scene.atSec!);
        if (from < 0) return null;
        const durationFrames = Math.ceil(scene.durationSec * fps);
        if (durationFrames <= 0) return null;
        const isLowerThird = scene.layout === "lower-third";
        // Sits in the lower-MIDDLE band (30%–56% from bottom) so it clears the caption
        // zone that hyperframes burns near the bottom (default caption_y ≈ 0.82 → ~18% up).
        const containerStyle: CSSProperties = isLowerThird
          ? { position: "absolute", left: 0, right: 0, bottom: "30%", height: "26%", overflow: "hidden" }
          : { position: "absolute", inset: 0 };
        return (
          <Sequence key={`ov-${scene.sceneId}`} from={from} durationInFrames={durationFrames}>
            <div style={containerStyle}>
              <SceneRenderer plan={scene} niche={plan.niche} />
            </div>
          </Sequence>
        );
      })}

      {/* Film grain + vignette (only when no named look owns its own grade) */}
      {(plan.look === undefined || plan.look === "none") && <FilmGrainOverlay niche={plan.niche} />}

      {/* Optional OutroCard appended after body */}
      {plan.outroCard && (
        <Sequence from={titleCardFrames + bodyFrames} durationInFrames={outroCardFrames}>
          <OutroCard
            nextText={plan.outroCard.nextText}
            episodeTitle={plan.outroCard.episodeTitle}
            durationInFrames={outroCardFrames}
            niche={plan.niche}
          />
        </Sequence>
      )}

      {/* Letterbox bars frame the whole composition (above all layers) */}
      {plan.look === "cinematic" && <Letterbox />}
    </AbsoluteFill>
  );
}

// Niche-agnostic wrappers; size is driven by the registered Composition (16x9 vs 9x16).
export function VoiceoverLong(props: VoiceoverEditProps) {
  return <VoiceoverEdit {...props} />;
}

export function VoiceoverShort(props: VoiceoverEditProps) {
  return <VoiceoverEdit {...props} />;
}
