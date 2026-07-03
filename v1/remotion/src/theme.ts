// Premium dark-keynote DS palette (matches the polished reel look).
export const T = {
  bg: '#06070b',
  ink: '#eef2f9',
  muted: '#7f8798',
  accent: '#4da3ff', // dominant electric blue
  accent2: '#37e0d8', // cyan — hairlines / cursor
  glass: 'rgba(18,22,31,0.72)',
  hair: 'rgba(255,255,255,0.10)',
  font: "Inter, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif",
  mono: "ui-monospace, 'SF Mono', 'JetBrains Mono', Menlo, monospace",
};

export const FPS = 30;
export const W = 1080;
export const H = 1920;
// Voice track is 46.08s → 1382 frames @30fps. Composition matches the audio.
export const DURATION_IN_FRAMES = 1382;

// Caption band sits mid-lower (thumb-safe). Scenes stay clear of this zone.
export const CAPTION_Y = 1360;
