import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {T} from './theme';

const GRAIN =
  "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E\")";

// Generated, animated DS background: near-black, two slow-drifting spotlights,
// a faint grid, grain, and a vignette. Deterministic (frame-driven) → seek-safe.
export const AnimatedBg: React.FC = () => {
  const f = useCurrentFrame();
  const t = f / 30;
  const x1 = 26 + Math.sin(t * 0.18) * 8;
  const y1 = 28 + Math.cos(t * 0.13) * 6;
  const x2 = 78 + Math.cos(t * 0.11) * 7;
  const y2 = 74 + Math.sin(t * 0.16) * 6;
  const gridShift = (t * 6) % 64;

  return (
    <AbsoluteFill style={{backgroundColor: T.bg}}>
      {/* drifting spotlights */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(1200px 900px at ${x1}% ${y1}%, rgba(77,163,255,0.16), transparent 60%), radial-gradient(1000px 1200px at ${x2}% ${y2}%, rgba(55,224,216,0.08), transparent 58%)`,
        }}
      />
      {/* faint drifting grid */}
      <AbsoluteFill
        style={{
          backgroundImage:
            'linear-gradient(rgba(255,255,255,0.035) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px)',
          backgroundSize: '64px 64px',
          backgroundPosition: `${gridShift}px ${gridShift}px`,
          maskImage:
            'radial-gradient(1200px 1400px at 50% 42%, black 30%, transparent 78%)',
          WebkitMaskImage:
            'radial-gradient(1200px 1400px at 50% 42%, black 30%, transparent 78%)',
        }}
      />
      {/* grain */}
      <AbsoluteFill
        style={{
          backgroundImage: GRAIN,
          backgroundSize: '320px 320px',
          opacity: 0.05,
          mixBlendMode: 'overlay',
        }}
      />
      {/* vignette */}
      <AbsoluteFill
        style={{
          background:
            'radial-gradient(1500px 1500px at 50% 44%, transparent 50%, rgba(2,3,6,0.9) 100%)',
        }}
      />
    </AbsoluteFill>
  );
};
