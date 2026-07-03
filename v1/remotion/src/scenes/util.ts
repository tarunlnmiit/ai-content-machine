import {interpolate, Easing} from 'remotion';

// Smooth ease-out entrance value 0→1 over [d0, d0+dur] frames.
export const rise = (f: number, d0: number, dur = 16) =>
  interpolate(f, [d0, d0 + dur], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });

// Parse "3 · EXCLUDE — no Eiffel, no top-10 list" → {num, label, val}
export function parseItem(text: string) {
  const m = text.match(/^\s*(\d+)\s*[·.\-]\s*(.*)$/);
  let num = '';
  let rest = text;
  if (m) {
    num = m[1];
    rest = m[2];
  }
  let label = rest;
  let val = '';
  const dash = rest.indexOf('—');
  if (dash >= 0) {
    label = rest.slice(0, dash).trim();
    val = rest.slice(dash + 1).trim();
  }
  return {num, label, val};
}
