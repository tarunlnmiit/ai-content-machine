import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { COLORS, FONTS, type Niche, nicheAccent, nicheGrid } from "../styles/chronixel";
import type { ScenePlan } from "../types";
import { DataVizReveal } from "./scenes/DataVizReveal";
import { CodeAnnotation } from "./scenes/CodeAnnotation";
import { ConceptExplainer } from "./scenes/ConceptExplainer";
import { ToolComparison } from "./scenes/ToolComparison";
import { NumberedTips } from "./scenes/NumberedTips";
import { TransformationArc } from "./scenes/TransformationArc";
import { HabitLoop } from "./scenes/HabitLoop";
import { WordReveal } from "./scenes/WordReveal";
import { AtmosphericQuote } from "./scenes/AtmosphericQuote";
import { LineReveal } from "./scenes/LineReveal";
import { CounterReveal } from "./scenes/CounterReveal";
import { ImageTextReveal } from "./scenes/ImageTextReveal";
import { HandwrittenReveal } from "./scenes/HandwrittenReveal";
import { VoiceMemoryDissolve } from "./scenes/VoiceMemoryDissolve";
import { DataPipelineFlow } from "./scenes/DataPipelineFlow";
import { BrowserTabOverload } from "./scenes/BrowserTabOverload";

const CROSSFADE_FRAMES = 12;

export function SceneFade({ durationInFrames }: { durationInFrames: number }) {
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

function PlaceholderScene({ plan, niche }: { plan: ScenePlan; niche: Niche }) {
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

export function SceneRenderer({ plan, niche }: { plan: ScenePlan; niche: Niche }) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const p = { ...plan.props, niche } as any;
  switch (plan.componentName) {
    case "DataVizReveal":     return <DataVizReveal     {...p} />;
    case "CodeAnnotation":    return <CodeAnnotation    {...p} />;
    case "ConceptExplainer":  return <ConceptExplainer  {...p} />;
    case "ToolComparison":    return <ToolComparison    {...p} />;
    case "NumberedTips":      return <NumberedTips      {...p} />;
    case "TransformationArc": return <TransformationArc {...p} />;
    case "HabitLoop":         return <HabitLoop         {...p} />;
    case "WordReveal":        return <WordReveal        {...p} />;
    case "AtmosphericQuote":  return <AtmosphericQuote  {...p} />;
    case "LineReveal":        return <LineReveal        {...p} />;
    case "CounterReveal":     return <CounterReveal     {...p} />;
    case "ImageTextReveal":    return <ImageTextReveal    {...p} />;
    case "HandwrittenReveal":  return <HandwrittenReveal  {...p} />;
    case "VoiceMemoryDissolve":        return <VoiceMemoryDissolve        {...p} />;
    case "DataPipelineFlow":        return <DataPipelineFlow        {...p} />;
    case "BrowserTabOverload":        return <BrowserTabOverload        {...p} />;
    default:                  return <PlaceholderScene plan={plan} niche={niche} />;
  }
}
