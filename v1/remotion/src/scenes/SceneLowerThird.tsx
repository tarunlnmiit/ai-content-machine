import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {T} from '../theme';
import {rise, parseItem} from './util';

// Beats 5/7 — enumerated lower-third card (kept above the caption band).
export const SceneLowerThird: React.FC<{text: string}> = ({text}) => {
  const f = useCurrentFrame();
  const {num, label, val} = parseItem(text);
  const a = rise(f, 2, 16);
  const tick = rise(f, 6, 12);
  return (
    <AbsoluteFill style={{fontFamily: T.font}}>
      <div
        style={{
          position: 'absolute',
          left: 60,
          right: 60,
          top: 1120,
          display: 'flex',
          gap: 26,
          padding: '34px 40px',
          borderRadius: 26,
          background: T.glass,
          backdropFilter: 'blur(24px) saturate(150%)',
          border: `1px solid ${T.hair}`,
          boxShadow: '0 22px 70px rgba(0,0,0,0.55), inset 0 1px 0 rgba(255,255,255,0.06)',
          opacity: a,
          transform: `translateX(${(1 - a) * -40}px)`,
        }}
      >
        <span
          style={{
            flex: '0 0 auto',
            width: 6,
            borderRadius: 3,
            background: `linear-gradient(to bottom, ${T.accent}, ${T.accent2})`,
            boxShadow: `0 0 20px ${T.accent}`,
            transform: `scaleY(${tick})`,
            transformOrigin: 'top',
          }}
        />
        <div style={{display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 14}}>
          <div style={{display: 'flex', alignItems: 'center', gap: 20}}>
            <span style={{fontFamily: T.mono, fontSize: 28, color: T.muted}}>
              {num.padStart(2, '0')}
            </span>
            <span
              style={{
                fontFamily: T.mono,
                fontWeight: 700,
                fontSize: 42,
                letterSpacing: '0.12em',
                textTransform: 'uppercase',
                color: T.ink,
              }}
            >
              {label}
            </span>
          </div>
          <span style={{fontWeight: 600, fontSize: 42, color: T.muted}}>{val}</span>
        </div>
      </div>
    </AbsoluteFill>
  );
};
