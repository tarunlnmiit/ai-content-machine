import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {T} from '../theme';
import {rise} from './util';

const PARTS: [string, string][] = [
  ['role', '#4da3ff'],
  ['task', '#37e0d8'],
  ['exclude', '#f6c177'],
  ['format', '#a78bfa'],
  ['verify', '#7ee787'],
];

// Beat 3 — keynote code-editor card; the 5 parts type in one by one.
export const SceneCode: React.FC = () => {
  const f = useCurrentFrame();
  const card = rise(f, 1, 12);
  const head = rise(f, 8, 10);
  return (
    <AbsoluteFill style={{fontFamily: T.font}}>
      <div
        style={{
          position: 'absolute',
          left: 70,
          right: 70,
          top: 470,
          borderRadius: 28,
          overflow: 'hidden',
          background: 'rgba(10,13,20,0.9)',
          border: `1px solid ${T.hair}`,
          boxShadow: '0 34px 100px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.05)',
          opacity: card,
          transform: `translateY(${(1 - card) * 30}px)`,
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            padding: '24px 30px',
            borderBottom: `1px solid ${T.hair}`,
            background: 'rgba(255,255,255,0.02)',
          }}
        >
          {['#ff5f57', '#febc2e', '#28c840'].map((c) => (
            <span key={c} style={{width: 17, height: 17, borderRadius: '50%', background: c}} />
          ))}
          <span style={{marginLeft: 18, fontFamily: T.mono, fontSize: 25, color: T.muted}}>
            prompt.md
          </span>
        </div>
        <div style={{padding: '34px 44px 40px'}}>
          <div
            style={{
              fontFamily: T.mono,
              fontSize: 38,
              color: T.ink,
              marginBottom: 20,
              opacity: head,
            }}
          >
            one prompt <span style={{color: T.muted}}>=</span>{' '}
            <span style={{color: T.accent}}>5 parts</span>
          </div>
          {PARTS.map(([p, hue], i) => {
            const a = rise(f, 16 + i * 7, 10);
            return (
              <div
                key={p}
                style={{
                  display: 'flex',
                  alignItems: 'baseline',
                  gap: 24,
                  padding: '11px 0',
                  fontFamily: T.mono,
                  fontSize: 44,
                  opacity: a,
                  transform: `translateX(${(1 - a) * 22}px)`,
                }}
              >
                <span style={{color: T.muted, fontSize: 28, width: 44}}>
                  {String(i + 1).padStart(2, '0')}
                </span>
                <span style={{color: hue, fontWeight: 600}}>{p}</span>
                <span style={{color: '#565f72'}}>:</span>
                <span style={{color: T.ink}}>•</span>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};
