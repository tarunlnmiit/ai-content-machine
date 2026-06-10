import { useCurrentFrame, useVideoConfig } from "remotion";
import type { TikTokPage } from "@remotion/captions";
import { FONTS } from "../styles/chronixel";

const HIGHLIGHT_COLOR = "#FFD700";
const TEXT_COLOR = "#FFFFFF";

interface CaptionPageProps {
  page: TikTokPage;
  fontSize?: number;
}

export function CaptionPage({ page, fontSize = 48 }: CaptionPageProps) {
  const frame = useCurrentFrame();
  const { fps, height } = useVideoConfig();
  const currentTimeMs = (frame / fps) * 1000;
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
            fontSize,
            fontWeight: 700,
            fontFamily: FONTS.heading,
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
                style={{
                  color: isActive ? HIGHLIGHT_COLOR : TEXT_COLOR,
                  display: "inline-block",
                  transform: isActive ? "scale(1.08)" : "scale(1)",
                  filter: isActive ? "brightness(1.2)" : "brightness(1)",
                  transition: "transform 80ms ease-out, filter 80ms ease-out",
                }}
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
