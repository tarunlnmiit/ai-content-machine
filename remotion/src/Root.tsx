import "./index.css";
import { Composition, staticFile } from "remotion";
import { TalkingHeadEdit } from "./compositions/TalkingHeadEdit";
import type { TalkingHeadEditProps } from "./compositions/TalkingHeadEdit";
import type { CalculateMetadataFunction } from "remotion";
import type { EditPlan } from "./types";

const FPS = 30;

async function loadEditPlan(editPlanFile: string): Promise<EditPlan> {
  const res = await fetch(staticFile(editPlanFile));
  return res.json();
}

const calcMeta: CalculateMetadataFunction<TalkingHeadEditProps> = async ({
  props,
}) => {
  const plan = await loadEditPlan(props.editPlanFile);
  const segments =
    plan.cutSegments && plan.cutSegments.length > 0
      ? plan.cutSegments
      : [{ startSec: plan.silenceTrimStartSec, endSec: plan.silenceTrimEndSec }];
  const totalSec = segments.reduce(
    (sum, seg) => sum + (seg.endSec - seg.startSec),
    0
  );
  return { durationInFrames: Math.ceil(totalSec * FPS) };
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="LifeHabits"
        component={TalkingHeadEdit}
        fps={FPS}
        width={1920}
        height={1080}
        durationInFrames={900}
        defaultProps={{ editPlanFile: "edit-plans/life_habits.json" }}
        calculateMetadata={calcMeta}
      />
      <Composition
        id="PoetryLove"
        component={TalkingHeadEdit}
        fps={FPS}
        width={1920}
        height={1080}
        durationInFrames={900}
        defaultProps={{ editPlanFile: "edit-plans/poetry_love.json" }}
        calculateMetadata={calcMeta}
      />
      <Composition
        id="PoetryWhenDreamsSpeak"
        component={TalkingHeadEdit}
        fps={FPS}
        width={1920}
        height={1080}
        durationInFrames={900}
        defaultProps={{ editPlanFile: "edit-plans/2026-05-21-poetry-quotes-when-dreams-speak-of-love.json" }}
        calculateMetadata={calcMeta}
      />
      <Composition
        id="DsCompletePythonCourse"
        component={TalkingHeadEdit}
        fps={FPS}
        width={1920}
        height={1080}
        durationInFrames={900}
        defaultProps={{ editPlanFile: "edit-plans/2026-05-21-ds-complete-python-course.json" }}
        calculateMetadata={calcMeta}
      />
      {/* Generic comp for ANY new talking-head video (course lessons, weekly videos).
          No need to register a new Composition per slug — render with --props override:
            npx remotion render CourseLesson out.mp4 --props='{"editPlanFile":"edit-plans/<slug>.json"}'
          Niche grading/grain come from the loaded plan, so any niche works through this one comp. */}
      <Composition
        id="CourseLesson"
        component={TalkingHeadEdit}
        fps={FPS}
        width={1920}
        height={1080}
        durationInFrames={900}
        defaultProps={{ editPlanFile: "edit-plans/life_habits.json" }}
        calculateMetadata={calcMeta}
      />
    </>
  );
};
