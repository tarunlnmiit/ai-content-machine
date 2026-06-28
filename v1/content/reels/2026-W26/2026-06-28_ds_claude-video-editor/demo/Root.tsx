import React from "react";
import { Composition } from "remotion";
import { OverlayDemo } from "./OverlayDemo";

/**
 * Replace the contents of your project's src/Root.tsx with this,
 * or add this <Composition> next to the default one.
 *
 * durationInFrames = clip length in seconds × fps.
 * Example below = 5s at 30fps = 150 frames. Adjust to YOUR clip.
 */
export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="OverlayDemo"
      component={OverlayDemo}
      durationInFrames={150}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{
        title: "Edited by Claude",
        subtitle: "in Remotion",
      }}
    />
  );
};
