import { useCurrentFrame, useVideoConfig } from "remotion";
import type { TikTokPage } from "@remotion/captions";

const HIGHLIGHT_COLOR = "#FFD700";
const TEXT_COLOR = "#FFFFFF";

interface CaptionPageProps {
  page: TikTokPage;
}

export function CaptionPage({ page }: CaptionPageProps) {
  const frame = useCurrentFrame();
  const { fps, height } = useVideoConfig();
  const currentTimeMs = (frame / fps) * 1000;
  // Keep text within the center 9:16 crop safe zone (height * 9/16 wide)
  const safeZoneWidth = height * (9 / 16);
  const captionMaxWidth = safeZoneWidth * 0.88;
  const absoluteTimeMs = page.startMs + currentTimeMs;

  return (
    <div
      style={{
        position: "absolute",
        bottom: 80,
        left: 0,
        right: 0,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        padding: "0 60px",
      }}
    >
      <div
        style={{
          backgroundColor: "rgba(0,0,0,0.65)",
          borderRadius: 12,
          padding: "14px 24px",
          maxWidth: captionMaxWidth,
          textAlign: "center",
        }}
      >
        <span
          style={{
            fontSize: 48,
            fontWeight: 700,
            fontFamily: "Arial, sans-serif",
            whiteSpace: "pre-wrap",
            lineHeight: 1.3,
          }}
        >
          {page.tokens.map((token) => {
            const isActive =
              token.fromMs <= absoluteTimeMs && token.toMs > absoluteTimeMs;
            return (
              <span
                key={token.fromMs}
                style={{ color: isActive ? HIGHLIGHT_COLOR : TEXT_COLOR }}
              >
                {token.text}
              </span>
            );
          })}
        </span>
      </div>
    </div>
  );
}
