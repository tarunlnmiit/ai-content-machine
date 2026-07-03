import {AbsoluteFill, Audio, Sequence, staticFile} from 'remotion';
import {FPS, T, DURATION_IN_FRAMES} from './theme';
import {AnimatedBg} from './AnimatedBg';
import {Captions} from './Captions';
import {SceneHook} from './scenes/SceneHook';
import {SceneMatrix} from './scenes/SceneMatrix';
import {SceneCode} from './scenes/SceneCode';
import {ScenePill} from './scenes/ScenePill';
import {SceneLowerThird} from './scenes/SceneLowerThird';
import {SceneOutro} from './scenes/SceneOutro';
import storyboard from './data/storyboard.json';

type Beat = {
  beat_id: number;
  beat_type: string;
  start_sec: number;
  end_sec: number;
  overlay_block: string;
  overlay_content: string | null;
};

function sceneFor(beat: Beat) {
  const txt = beat.overlay_content ?? '';
  switch (beat.overlay_block) {
    case 'code-particle-assemble':
      return <SceneHook />;
    case 'matrix-decode':
      return <SceneMatrix text={txt} />;
    case 'code-typing':
      return <SceneCode />;
    case 'floating-pill-badge':
      return <ScenePill text={txt} />;
    case 'lower-third-minimal':
      return <SceneLowerThird text={txt} />;
    default:
      // outro / macos-notification / logo-outro
      return <SceneOutro />;
  }
}

export const FacelessReel: React.FC = () => {
  const beats = (storyboard as {beats: Beat[]}).beats;
  return (
    <AbsoluteFill style={{backgroundColor: T.bg}}>
      <AnimatedBg />
      <Audio src={staticFile('voice.m4a')} />
      {beats.map((b, i) => {
        const from = Math.round(b.start_sec * FPS);
        const isLast = i === beats.length - 1;
        // Stretch the final beat to the audio end so nothing goes blank.
        const dur = isLast
          ? Math.max(1, DURATION_IN_FRAMES - from)
          : Math.max(1, Math.round((b.end_sec - b.start_sec) * FPS));
        return (
          <Sequence key={b.beat_id} from={from} durationInFrames={dur} name={`beat-${b.beat_id}`}>
            {sceneFor(b)}
          </Sequence>
        );
      })}
      <Captions />
    </AbsoluteFill>
  );
};
