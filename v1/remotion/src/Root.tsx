import {Composition} from 'remotion';
import {FacelessReel} from './FacelessReel';
import {FPS, W, H, DURATION_IN_FRAMES} from './theme';

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="FacelessReel"
      component={FacelessReel}
      durationInFrames={DURATION_IN_FRAMES}
      fps={FPS}
      width={W}
      height={H}
    />
  );
};
