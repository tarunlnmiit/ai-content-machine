import {useMemo} from 'react';
import {useCurrentFrame} from 'remotion';
import {T, FPS, CAPTION_Y} from './theme';
import words from './data/transcript.json';

type W = {text: string; start: number; end: number};

// Group words into short caption chunks (break on ~26 chars or a >0.5s gap).
function buildChunks(ws: W[]) {
  const chunks: {start: number; end: number; words: W[]}[] = [];
  let cur: W[] = [];
  let chars = 0;
  const flush = () => {
    if (cur.length) {
      chunks.push({start: cur[0].start, end: cur[cur.length - 1].end, words: cur});
      cur = [];
      chars = 0;
    }
  };
  for (let i = 0; i < ws.length; i++) {
    const w = ws[i];
    const gap = cur.length ? w.start - cur[cur.length - 1].end : 0;
    if (cur.length && (chars + w.text.length > 26 || gap > 0.5)) flush();
    cur.push(w);
    chars += w.text.length;
  }
  flush();
  return chunks;
}

export const Captions: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const chunks = useMemo(() => buildChunks(words as W[]), []);

  const chunk =
    chunks.find((c) => t >= c.start && t < c.end) ??
    (t < chunks[0]?.start ? undefined : chunks.reduce((a, c) => (c.start <= t ? c : a), chunks[0]));
  if (!chunk || t < chunk.start - 0.05 || t > chunk.end + 0.35) return null;

  return (
    <div
      style={{
        position: 'absolute',
        left: 0,
        right: 0,
        top: CAPTION_Y,
        display: 'flex',
        justifyContent: 'center',
        flexWrap: 'wrap',
        gap: '0 16px',
        padding: '0 70px',
        fontFamily: T.font,
        fontWeight: 800,
        fontSize: 58,
        letterSpacing: '-0.01em',
        textAlign: 'center',
      }}
    >
      {chunk.words.map((w, i) => {
        const active = t >= w.start && t < w.end;
        return (
          <span
            key={i}
            style={{
              color: active ? '#ffd24a' : '#ffffff',
              textShadow:
                '0 3px 12px rgba(0,0,0,0.85), 0 0 3px rgba(0,0,0,0.9)',
              WebkitTextStroke: '2px rgba(0,0,0,0.55)',
              paintOrder: 'stroke fill',
            }}
          >
            {w.text.trim().toUpperCase()}
          </span>
        );
      })}
    </div>
  );
};
