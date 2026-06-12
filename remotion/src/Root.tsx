import "./index.css";
import { Composition, staticFile } from "remotion";

// Compositions
import { TalkingHeadEdit } from "./compositions/TalkingHeadEdit";
import type { TalkingHeadEditProps } from "./compositions/TalkingHeadEdit";
import { TitleCard } from "./compositions/TitleCard";
import { LowerThird } from "./compositions/LowerThird";
import { OutroCard } from "./compositions/OutroCard";
import { ShortClip } from "./compositions/ShortClip";
import type { ShortClipProps } from "./compositions/ShortClip";
import { DSMotionShort, LifeMotionShort, PoetryMotionShort } from "./compositions/MotionShort";
import type { DSMotionShortProps } from "./compositions/MotionShort";
import { AudiogramFeed, AudiogramStory } from "./compositions/Audiogram";
import { SocialCard1x1, SocialCard9x16 } from "./compositions/SocialCard";
import { Thumbnail } from "./compositions/Thumbnail";
import { AbstractDS } from "./compositions/abstract/AbstractDS";
import { AbstractLife } from "./compositions/abstract/AbstractLife";
import { AbstractPoetry } from "./compositions/abstract/AbstractPoetry";

// Scene library
import { WordReveal } from "./compositions/scenes/WordReveal";
import { AtmosphericQuote } from "./compositions/scenes/AtmosphericQuote";
import { NumberedTips } from "./compositions/scenes/NumberedTips";
import { DataVizReveal } from "./compositions/scenes/DataVizReveal";
import { CodeAnnotation } from "./compositions/scenes/CodeAnnotation";
import { ConceptExplainer } from "./compositions/scenes/ConceptExplainer";
import { ToolComparison } from "./compositions/scenes/ToolComparison";
import { TransformationArc } from "./compositions/scenes/TransformationArc";
import { HabitLoop } from "./compositions/scenes/HabitLoop";
import { LineReveal } from "./compositions/scenes/LineReveal";
import { CounterReveal } from "./compositions/scenes/CounterReveal";
import { ImageTextReveal } from "./compositions/scenes/ImageTextReveal";
import { HandwrittenReveal } from "./compositions/scenes/HandwrittenReveal";
import { BrowserTabOverload } from "./compositions/scenes/BrowserTabOverload";
import { DataPipelineFlow } from "./compositions/scenes/DataPipelineFlow";
import { VoiceMemoryDissolve } from "./compositions/scenes/VoiceMemoryDissolve";
import { ScenePreview } from "./compositions/ScenePreview";
import type { ScenePreviewProps } from "./compositions/ScenePreview";

import type { CalculateMetadataFunction } from "remotion";
import type { EditPlan, ScenePlan } from "./types";

const FPS = 30;

async function loadEditPlan(editPlanFile: string): Promise<EditPlan> {
  const res = await fetch(staticFile(editPlanFile));
  if (!res.ok) throw new Error(`Edit plan not found: ${editPlanFile} (${res.status})`);
  return res.json();
}

const calcMetaTalkingHead: CalculateMetadataFunction<TalkingHeadEditProps> = async ({
  props,
}) => {
  try {
    const plan = await loadEditPlan(props.editPlanFile);
    const segments =
      plan.cutSegments && plan.cutSegments.length > 0
        ? plan.cutSegments
        : [{ startSec: plan.silenceTrimStartSec, endSec: plan.silenceTrimEndSec }];
    const editSec = segments.reduce((sum, seg) => sum + (seg.endSec - seg.startSec), 0);
    const titleCardSec = plan.titleCard ? plan.titleCard.durationFrames / FPS : 0;
    const outroCardSec = plan.outroCard ? plan.outroCard.durationFrames / FPS : 0;
    return { durationInFrames: Math.ceil((editSec + titleCardSec + outroCardSec) * FPS) };
  } catch {
    return { durationInFrames: 900 };
  }
};

const calcMetaScenePreview: CalculateMetadataFunction<ScenePreviewProps> = async ({ props }) => {
  try {
    const res = await fetch(staticFile(props.scenePlanFile));
    if (!res.ok) return { durationInFrames: 180 };
    const data: ScenePlan[] = await res.json();
    return { durationInFrames: Math.ceil((data[0]?.durationSec ?? 6) * FPS) };
  } catch {
    return { durationInFrames: 180 };
  }
};

const calcMetaMotionShort: CalculateMetadataFunction<DSMotionShortProps> = async ({ props }) => {
  try {
    const res = await fetch(staticFile(props.scenePlanFile));
    if (!res.ok) return { durationInFrames: 450 };
    const scenes: ScenePlan[] = await res.json();
    const total = scenes.reduce((sum, s) => sum + Math.round(s.durationSec * FPS), 0);
    return { durationInFrames: total };
  } catch {
    return { durationInFrames: 450 };
  }
};

const calcMetaShortClip: CalculateMetadataFunction<ShortClipProps> = async ({ props }) => {
  const dur = props.clipEndSec - props.clipStartSec;
  return { durationInFrames: Math.ceil(dur * FPS) };
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* ── Long-form talking head ── */}
      <Composition
        id="LifeHabits"
        component={TalkingHeadEdit}
        fps={FPS}
        width={1920}
        height={1080}
        durationInFrames={900}
        defaultProps={{ editPlanFile: "edit-plans/2026-W24/2026-06-10_2026-06-08-life-self-dev-the-simple-habit-that-changed-my-pr.json" }}
        calculateMetadata={calcMetaTalkingHead}
      />
      <Composition
        id="PoetryLove"
        component={TalkingHeadEdit}
        fps={FPS}
        width={1920}
        height={1080}
        durationInFrames={900}
        defaultProps={{ editPlanFile: "edit-plans/2026-W24/2026-06-08_2026-06-08-poetry-quotes-poetry-dips-its-fingers-in-every-co.json" }}
        calculateMetadata={calcMetaTalkingHead}
      />
      {/* Generic workhorse — render any slug with --props override */}
      <Composition
        id="CourseLesson"
        component={TalkingHeadEdit}
        fps={FPS}
        width={1920}
        height={1080}
        durationInFrames={900}
        defaultProps={{ editPlanFile: "edit-plans/2026-W24/2026-06-10_2026-06-08-life-self-dev-the-simple-habit-that-changed-my-pr.json" }}
        calculateMetadata={calcMetaTalkingHead}
      />

      {/* ── Overlay components (preview in studio) ── */}
      <Composition
        id="TitleCard"
        component={TitleCard}
        fps={FPS}
        width={1920}
        height={1080}
        durationInFrames={90}
        defaultProps={{ titleText: "Preview Title", niche: "ds" as const, durationInFrames: 90 }}
      />
      <Composition
        id="LowerThird"
        component={LowerThird}
        fps={FPS}
        width={1920}
        height={1080}
        durationInFrames={90}
        defaultProps={{ text: "Preview Lower Third", niche: "ds" as const, durationInFrames: 90 }}
      />
      <Composition
        id="OutroCard"
        component={OutroCard}
        fps={FPS}
        width={1920}
        height={1080}
        durationInFrames={150}
        defaultProps={{ nextText: "Up Next: Preview", niche: "ds" as const, durationInFrames: 150 }}
      />

      {/* ── Short-form ── */}
      <Composition
        id="ShortClip"
        component={ShortClip}
        fps={FPS}
        width={1080}
        height={1920}
        durationInFrames={900}
        defaultProps={{
          editPlanFile: "edit-plans/2026-W24/2026-06-10_2026-06-08-life-self-dev-the-simple-habit-that-changed-my-pr.json",
          clipStartSec: 0,
          clipEndSec: 60,
        }}
        calculateMetadata={calcMetaShortClip}
      />
      <Composition
        id="DSMotionShort"
        component={DSMotionShort}
        fps={FPS}
        width={1080}
        height={1920}
        durationInFrames={450}
        defaultProps={{ scenePlanFile: "scene-plans/2026-W24/2026-06-10_2026-06-10-data-science-tech-python-for-data-science-tutoria_s01.json" }}
        calculateMetadata={calcMetaMotionShort}
      />
      <Composition
        id="LifeMotionShort"
        component={LifeMotionShort}
        fps={FPS}
        width={1080}
        height={1920}
        durationInFrames={450}
        defaultProps={{ scenePlanFile: "scene-plans/2026-W24/2026-06-10_2026-06-08-life-self-dev-the-simple-habit-that-changed-my-pr_s01.json" }}
        calculateMetadata={calcMetaMotionShort}
      />
      <Composition
        id="PoetryMotionShort"
        component={PoetryMotionShort}
        fps={FPS}
        width={1080}
        height={1920}
        durationInFrames={450}
        defaultProps={{ scenePlanFile: "scene-plans/2026-W24/2026-06-08_2026-06-08-poetry-quotes-poetry-dips-its-fingers-in-every-co_s01.json" }}
        calculateMetadata={calcMetaMotionShort}
      />

      {/* ── Audiogram ── */}
      <Composition
        id="AudiogramFeed"
        component={AudiogramFeed}
        fps={FPS}
        width={1080}
        height={1080}
        durationInFrames={300}
        defaultProps={{
          audioFile: "audio/sample.mp3",
          startSec: 0,
          endSec: 10,
          quote: "Sample quote for preview",
          niche: "ds" as const,
          podcastName: "Breath of Data Science",
        }}
      />
      <Composition
        id="AudiogramStory"
        component={AudiogramStory}
        fps={FPS}
        width={1080}
        height={1920}
        durationInFrames={300}
        defaultProps={{
          audioFile: "audio/sample.mp3",
          startSec: 0,
          endSec: 10,
          quote: "Sample quote for preview",
          niche: "ds" as const,
          podcastName: "Breath of Data Science",
        }}
      />

      {/* ── Social cards ── */}
      <Composition
        id="SocialCard1x1"
        component={SocialCard1x1}
        fps={FPS}
        width={1080}
        height={1080}
        durationInFrames={150}
        defaultProps={{ headline: "Preview Headline", niche: "ds" as const }}
      />
      <Composition
        id="SocialCard9x16"
        component={SocialCard9x16}
        fps={FPS}
        width={1080}
        height={1920}
        durationInFrames={150}
        defaultProps={{ headline: "Preview Headline", niche: "life" as const }}
      />

      {/* ── Thumbnail (still export) ── */}
      <Composition
        id="Thumbnail"
        component={Thumbnail}
        fps={FPS}
        width={1280}
        height={720}
        durationInFrames={1}
        defaultProps={{
          titleText: "Preview Thumbnail",
          niche: "ds" as const,
          variant: "a" as const,
          bgType: "dark" as const,
        }}
      />

      {/* ── Abstract B-roll (30-second loops) ── */}
      <Composition
        id="AbstractDS"
        component={AbstractDS}
        fps={FPS}
        width={1920}
        height={1080}
        durationInFrames={900}
        defaultProps={{}}
      />
      <Composition
        id="AbstractLife"
        component={AbstractLife}
        fps={FPS}
        width={1920}
        height={1080}
        durationInFrames={900}
        defaultProps={{}}
      />
      <Composition
        id="AbstractPoetry"
        component={AbstractPoetry}
        fps={FPS}
        width={1920}
        height={1080}
        durationInFrames={900}
        defaultProps={{}}
      />

      {/* ── Scene library (preview individually) ── */}
      <Composition
        id="WordReveal"
        component={WordReveal}
        fps={FPS}
        width={1920}
        height={1080}
        durationInFrames={150}
        defaultProps={{
          words: ["Every", "word", "matters", "in", "*data*"],
          niche: "ds" as const,
        }}
      />
      <Composition
        id="AtmosphericQuote"
        component={AtmosphericQuote}
        fps={FPS}
        width={1920}
        height={1080}
        durationInFrames={180}
        defaultProps={{
          quote: "The best insights hide in plain sight.",
          niche: "ds" as const,
        }}
      />
      <Composition
        id="NumberedTips"
        component={NumberedTips}
        fps={FPS}
        width={1920}
        height={1080}
        durationInFrames={210}
        defaultProps={{
          tips: [
            { number: 1, headline: "Start with the data", body: "Clean before you explore" },
            { number: 2, headline: "Ask the right question", body: "Framing matters most" },
            { number: 3, headline: "Tell the story", body: "Visuals over tables" },
          ],
          niche: "ds" as const,
        }}
      />
      <Composition
        id="DataVizReveal"
        component={DataVizReveal}
        fps={FPS}
        width={1920}
        height={1080}
        durationInFrames={180}
        defaultProps={{
          data: [
            { label: "2020", value: 42 },
            { label: "2021", value: 61 },
            { label: "2022", value: 75 },
            { label: "2023", value: 88 },
            { label: "2024", value: 95 },
          ],
          niche: "ds" as const,
          title: "Model Accuracy Over Years",
        }}
      />
      <Composition
        id="CodeAnnotation"
        component={CodeAnnotation}
        fps={FPS}
        width={1920}
        height={1080}
        durationInFrames={150}
        defaultProps={{
          code: [
            "import pandas as pd",
            "",
            "df = pd.read_csv('data.csv')",
            "df['score'] = df['score'].fillna(0)",
            "result = df.groupby('category').mean()",
          ],
          highlightLine: 3,
          annotationText: "fillna prevents NaN errors downstream",
          language: "python",
          niche: "ds" as const,
        }}
      />
      <Composition
        id="ConceptExplainer"
        component={ConceptExplainer}
        fps={FPS}
        width={1920}
        height={1080}
        durationInFrames={180}
        defaultProps={{
          headline: "Three Core Concepts",
          cards: [
            { term: "Precision", definition: "Of all predicted positives, how many are actually positive?" },
            { term: "Recall", definition: "Of all actual positives, how many did we catch?" },
            { term: "F1 Score", definition: "Harmonic mean of precision and recall." },
          ],
          niche: "ds" as const,
        }}
      />
      <Composition
        id="ToolComparison"
        component={ToolComparison}
        fps={FPS}
        width={1920}
        height={1080}
        durationInFrames={180}
        defaultProps={{
          leftSide: {
            label: "Pandas",
            points: ["In-memory only", "Single threaded", "Great for < 1M rows"],
          },
          rightSide: {
            label: "Polars",
            badge: "Faster",
            points: ["Lazy evaluation", "Multi-threaded", "Handles 100M+ rows"],
          },
          niche: "ds" as const,
        }}
      />
      <Composition
        id="TransformationArc"
        component={TransformationArc}
        fps={FPS}
        width={1920}
        height={1080}
        durationInFrames={210}
        defaultProps={{
          beforeLabel: "Scattered",
          afterLabel: "Intentional",
          beforePoints: ["No morning routine", "Reactive all day", "Energy depletes by noon"],
          afterPoints: ["Anchored 3 habits", "Proactive focus blocks", "Energy compounds"],
          niche: "life" as const,
        }}
      />
      <Composition
        id="HabitLoop"
        component={HabitLoop}
        fps={FPS}
        width={1920}
        height={1080}
        durationInFrames={180}
        defaultProps={{
          title: "The Habit Loop",
          steps: [
            { label: "Cue", sublabel: "Trigger" },
            { label: "Craving", sublabel: "Motivation" },
            { label: "Response", sublabel: "The habit" },
            { label: "Reward", sublabel: "Reinforcement" },
          ],
          progress: 1,
          niche: "life" as const,
        }}
      />
      <Composition
        id="LineReveal"
        component={LineReveal}
        fps={FPS}
        width={1920}
        height={1080}
        durationInFrames={180}
        defaultProps={{
          lines: [
            "We loved with a love",
            "that was more than love",
          ],
          attribution: "Edgar Allan Poe",
          niche: "poetry" as const,
        }}
      />
      <Composition
        id="CounterReveal"
        component={CounterReveal}
        fps={FPS}
        width={1920}
        height={1080}
        durationInFrames={150}
        defaultProps={{ value: 42, label: "preview", niche: "ds" as const }}
      />
      <Composition
        id="ImageTextReveal"
        component={ImageTextReveal}
        fps={FPS}
        width={1920}
        height={1080}
        durationInFrames={180}
        defaultProps={{ headline: "Preview Headline", subtext: "subtext", niche: "ds" as const }}
      />
      <Composition
        id="HandwrittenReveal"
        component={HandwrittenReveal}
        fps={FPS}
        width={1920}
        height={1080}
        durationInFrames={210}
        defaultProps={{ lines: ["Preview line"], niche: "ds" as const }}
      />
      <Composition
        id="BrowserTabOverload"
        component={BrowserTabOverload}
        fps={FPS}
        width={1920}
        height={1080}
        durationInFrames={180}
        defaultProps={{ niche: "life" as const }}
      />
      <Composition
        id="DataPipelineFlow"
        component={DataPipelineFlow}
        fps={FPS}
        width={1920}
        height={1080}
        durationInFrames={210}
        defaultProps={{ niche: "ds" as const }}
      />
      <Composition
        id="VoiceMemoryDissolve"
        component={VoiceMemoryDissolve}
        fps={FPS}
        width={1920}
        height={1080}
        durationInFrames={210}
        defaultProps={{ niche: "poetry" as const }}
      />

      {/* ── ScenePreview — render any overlay scene by scenePlanFile ── */}
      <Composition
        id="ScenePreview"
        component={ScenePreview}
        fps={FPS}
        width={1920}
        height={1080}
        durationInFrames={180}
        defaultProps={{ scenePlanFile: "scene-plans/preview/preview.json" } as ScenePreviewProps}
        calculateMetadata={calcMetaScenePreview}
      />
    </>
  );
};
