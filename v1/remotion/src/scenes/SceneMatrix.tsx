import {AbsoluteFill, useCurrentFrame, interpolate, Easing} from 'remotion';
import {T} from '../theme';
import {rise} from './util';

const GLYPHS = 'ABCDEFGHKMNPRSTUVXYZ01<>/#=$*';

// Beat 2 & 9 — statement with a char-scramble "decode" reveal, in a glass card.
export const SceneMatrix: React.FC<{text: string}> = ({text}) => {
  const f = useCurrentFrame();
  const card = rise(f, 2, 18);
  // decode progress 0→1 over frames [15, 48]
  const p = interpolate(f, [15, 48], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.quad),
  });
  const n = Math.floor(p * text.length);
  let out = '';
  for (let i = 0; i < text.length; i++) {
    if (i < n || text[i] === ' ' || text[i] === '.' || text[i] === "'") out += text[i];
    else out += GLYPHS[(Math.floor(p * 97) + i * 7) % GLYPHS.length];
  }
  const cursorOn = Math.floor(f / 12) % 2 === 0 && f > 16;

  return (
    <AbsoluteFill style={{fontFamily: T.font}}>
      <div
        style={{
          position: 'absolute',
          left: 60,
          right: 60,
          top: 560,
          padding: '44px 52px',
          borderRadius: 30,
          background: T.glass,
          backdropFilter: 'blur(24px) saturate(150%)',
          border: `1px solid ${T.hair}`,
          boxShadow: '0 30px 90px rgba(0,0,0,0.55), inset 0 1px 0 rgba(255,255,255,0.06)',
          opacity: card,
          transform: `translateY(${(1 - card) * 40}px) scale(${0.97 + card * 0.03})`,
        }}
      >
        <div
          style={{
            fontFamily: T.mono,
            fontSize: 24,
            letterSpacing: '0.36em',
            textTransform: 'uppercase',
            color: T.accent,
            marginBottom: 24,
          }}
        >
          // the tension
        </div>
        <div
          style={{
            fontWeight: 800,
            fontSize: 72,
            lineHeight: 1.12,
            letterSpacing: '-0.03em',
            color: T.ink,
            minHeight: 170,
          }}
        >
          {out}
          <span
            style={{
              display: 'inline-block',
              width: 18,
              height: 64,
              verticalAlign: '-12px',
              marginLeft: 8,
              background: T.accent2,
              boxShadow: `0 0 18px ${T.accent2}`,
              opacity: cursorOn ? 1 : 0.15,
            }}
          />
        </div>
      </div>
    </AbsoluteFill>
  );
};
