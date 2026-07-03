import {AbsoluteFill, useCurrentFrame, interpolate} from 'remotion';
import {T} from '../theme';
import {rise} from './util';

// Beat 1 — cold-open hook. Upper-centre, above the caption band.
export const SceneHook: React.FC = () => {
  const f = useCurrentFrame();
  const a1 = rise(f, 4);
  const a2 = rise(f, 22, 20);
  const rule = interpolate(f, [16, 34], [0, 240], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  return (
    <AbsoluteFill style={{fontFamily: T.font}}>
      <div
        style={{
          position: 'absolute',
          top: 470,
          left: 84,
          display: 'flex',
          alignItems: 'center',
          gap: 16,
          opacity: rise(f, 2, 12),
        }}
      >
        <div style={{width: 46, height: 2, background: T.accent, boxShadow: `0 0 14px ${T.accent}`}} />
        <div
          style={{
            fontFamily: T.mono,
            fontSize: 26,
            letterSpacing: '0.42em',
            textTransform: 'uppercase',
            color: T.muted,
            fontWeight: 600,
          }}
        >
          Prompt Anatomy
        </div>
      </div>
      <div
        style={{
          position: 'absolute',
          top: 540,
          left: 84,
          fontWeight: 700,
          fontSize: 58,
          letterSpacing: '-0.02em',
          color: T.muted,
          opacity: a1,
          transform: `translateY(${(1 - a1) * 24}px)`,
        }}
      >
        One prompt.
      </div>
      <div
        style={{
          position: 'absolute',
          top: 632,
          left: 84,
          width: rule,
          height: 2,
          background: `linear-gradient(to right, ${T.accent}, transparent)`,
          boxShadow: `0 0 16px ${T.accent}`,
        }}
      />
      <div
        style={{
          position: 'absolute',
          top: 668,
          left: 84,
          width: 940,
          fontWeight: 800,
          fontSize: 132,
          lineHeight: 0.98,
          letterSpacing: '-0.045em',
          color: T.ink,
          opacity: a2,
          transform: `translateY(${(1 - a2) * 30}px)`,
          filter: `blur(${(1 - a2) * 12}px)`,
        }}
      >
        A private <span style={{color: T.accent}}>historian.</span>
      </div>
    </AbsoluteFill>
  );
};
