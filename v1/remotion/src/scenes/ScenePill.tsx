import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {T} from '../theme';
import {rise, parseItem} from './util';

// Beats 4/6/8 — enumerated pill badge at the top.
export const ScenePill: React.FC<{text: string}> = ({text}) => {
  const f = useCurrentFrame();
  const {num, label, val} = parseItem(text);
  const a = rise(f, 2, 14);
  const chip = rise(f, 8, 12);
  return (
    <AbsoluteFill style={{fontFamily: T.font}}>
      <div
        style={{
          position: 'absolute',
          top: 150,
          left: 60,
          right: 60,
          display: 'flex',
          alignItems: 'center',
          gap: 22,
          padding: '22px 34px',
          borderRadius: 100,
          background: T.glass,
          backdropFilter: 'blur(20px) saturate(160%)',
          border: `1px solid ${T.hair}`,
          boxShadow: '0 14px 44px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.07)',
          opacity: a,
          transform: `translateY(${(1 - a) * -22}px)`,
        }}
      >
        <span
          style={{
            flex: '0 0 auto',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: 62,
            height: 62,
            borderRadius: 18,
            background: T.accent,
            color: '#04121f',
            fontWeight: 800,
            fontSize: 36,
            boxShadow: '0 0 22px rgba(77,163,255,0.55)',
            transform: `scale(${0.3 + chip * 0.7})`,
            opacity: chip,
          }}
        >
          {num}
        </span>
        <span
          style={{
            fontFamily: T.mono,
            fontWeight: 700,
            fontSize: 36,
            letterSpacing: '0.12em',
            textTransform: 'uppercase',
            color: T.ink,
            whiteSpace: 'nowrap',
          }}
        >
          {label}
        </span>
        <span style={{width: 1, height: 44, background: T.hair}} />
        <span
          style={{
            fontWeight: 600,
            fontSize: 34,
            color: T.muted,
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
          }}
        >
          {val}
        </span>
      </div>
    </AbsoluteFill>
  );
};
