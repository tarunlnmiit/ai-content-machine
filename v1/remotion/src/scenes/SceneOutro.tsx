import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {T} from '../theme';
import {rise} from './util';

// Beat 10 — simple comment CTA. No logo, no subscribe.
export const SceneOutro: React.FC = () => {
  const f = useCurrentFrame();
  const a = rise(f, 4, 16);
  const sub = rise(f, 16, 14);
  return (
    <AbsoluteFill style={{fontFamily: T.font, alignItems: 'center', justifyContent: 'center'}}>
      <div style={{transform: 'translateY(-120px)', textAlign: 'center'}}>
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 20,
            padding: '30px 52px',
            borderRadius: 100,
            background: T.accent,
            color: '#04121f',
            fontFamily: T.mono,
            fontWeight: 700,
            fontSize: 46,
            letterSpacing: '0.04em',
            boxShadow: '0 0 48px rgba(77,163,255,0.5)',
            opacity: a,
            transform: `scale(${0.9 + a * 0.1})`,
          }}
        >
          Comment{' '}
          <span style={{background: '#04121f', color: T.accent, padding: '6px 22px', borderRadius: 14}}>
            PROMPT
          </span>
        </div>
        <div
          style={{
            marginTop: 40,
            fontSize: 40,
            color: T.ink,
            opacity: sub,
            transform: `translateY(${(1 - sub) * 14}px)`,
          }}
        >
          → I'll DM the full copy-paste prompt
        </div>
      </div>
    </AbsoluteFill>
  );
};
