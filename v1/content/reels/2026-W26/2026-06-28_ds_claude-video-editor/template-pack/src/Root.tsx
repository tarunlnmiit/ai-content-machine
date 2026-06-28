import { Composition } from "remotion";
import { WordPopCaption } from "./Captions";
import { LowerThird } from "./LowerThird";
import { ProgressBar } from "./ProgressBar";
import { FollowBadge } from "./FollowBadge";

// 5s @ 30fps, vertical. Change durationInFrames if your clip is longer/shorter.
const FPS = 30;
const DURATION = 5 * FPS;
const W = 1080;
const H = 1920;

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="WordPopCaption"
        component={WordPopCaption}
        durationInFrames={DURATION}
        fps={FPS}
        width={W}
        height={H}
        defaultProps={{
          src: "clip.mp4",
          text: "MADE WITH CLAUDE",
          position: "bottom" as const,
          color: "#ffffff",
        }}
      />
      <Composition
        id="LowerThird"
        component={LowerThird}
        durationInFrames={DURATION}
        fps={FPS}
        width={W}
        height={H}
        defaultProps={{
          src: "clip.mp4",
          name: "Tarun",
          title: "Data Scientist",
          accent: "#ffd400",
          inAt: 0.5,
        }}
      />
      <Composition
        id="ProgressBar"
        component={ProgressBar}
        durationInFrames={DURATION}
        fps={FPS}
        width={W}
        height={H}
        defaultProps={{ src: "clip.mp4", accent: "#ffd400", thickness: 10 }}
      />
      <Composition
        id="FollowBadge"
        component={FollowBadge}
        durationInFrames={DURATION}
        fps={FPS}
        width={W}
        height={H}
        defaultProps={{
          src: "clip.mp4",
          handle: "@breathofdatascience",
          appearAt: 4,
        }}
      />
    </>
  );
};
