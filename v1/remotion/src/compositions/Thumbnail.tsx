import { AbsoluteFill } from "remotion";
import {
  COLORS,
  FONTS,
  RADIUS,
  type Niche,
  nicheAccent,
  nicheGlow,
  nicheGrid,
  nicheShowName,
} from "../styles/chronixel";

export interface ThumbnailProps extends Record<string, unknown> {
  titleText: string;
  hookText?: string;
  niche: Niche;
  variant?: "a" | "b" | "c";
  bgType?: "dark" | "gradient" | "split";
}

function ThumbnailVariantA({
  titleText,
  hookText,
  niche,
  bgType = "dark",
}: ThumbnailProps) {
  const accent = nicheAccent(niche);
  const glow = nicheGlow(niche);
  const grid = nicheGrid(niche);
  const showName = nicheShowName(niche);

  const bg =
    bgType === "gradient"
      ? `radial-gradient(ellipse 80% 80% at 20% 50%, ${glow.replace("0.20", "0.30")} 0%, ${COLORS.bg} 70%)`
      : bgType === "split"
      ? `linear-gradient(105deg, #0f0f18 50%, ${COLORS.bg} 50%)`
      : COLORS.bg;

  return (
    <AbsoluteFill style={{ background: bg, overflow: "hidden" }}>
      {/* Grid */}
      <AbsoluteFill
        style={{
          backgroundImage: `linear-gradient(${grid} 1px, transparent 1px), linear-gradient(90deg, ${grid} 1px, transparent 1px)`,
          backgroundSize: "80px 80px",
          pointerEvents: "none",
        }}
      />

      {/* Glow */}
      <div
        style={{
          position: "absolute",
          top: "50%",
          left: "12%",
          transform: "translateY(-50%)",
          width: 480,
          height: 480,
          background: `radial-gradient(circle, ${glow} 0%, transparent 70%)`,
          pointerEvents: "none",
        }}
      />

      {/* Content block */}
      <div
        style={{
          position: "absolute",
          top: "50%",
          left: 80,
          right: 80,
          transform: "translateY(-50%)",
        }}
      >
        {/* Hook pill */}
        {hookText && (
          <div
            style={{
              display: "inline-block",
              background: accent,
              color: "#fff",
              fontSize: 22,
              fontFamily: FONTS.body,
              fontWeight: FONTS.headingWeight,
              letterSpacing: "0.06em",
              textTransform: "uppercase",
              padding: "8px 20px",
              borderRadius: RADIUS.pill,
              marginBottom: 24,
            }}
          >
            {hookText}
          </div>
        )}

        {/* Title */}
        <div
          style={{
            color: COLORS.text,
            fontSize: 88,
            fontFamily: FONTS.heading,
            fontWeight: FONTS.headingWeight,
            lineHeight: 1.1,
            letterSpacing: "-0.02em",
            maxWidth: "75%",
          }}
        >
          {titleText}
        </div>

        {/* Show name */}
        <div
          style={{
            marginTop: 28,
            color: accent,
            fontSize: 20,
            fontFamily: FONTS.body,
            fontWeight: FONTS.semibold,
            letterSpacing: "0.12em",
            textTransform: "uppercase",
          }}
        >
          {showName}
        </div>
      </div>

      {/* Right edge accent bar */}
      <div
        style={{
          position: "absolute",
          right: 0,
          top: "20%",
          bottom: "20%",
          width: 6,
          background: `linear-gradient(to bottom, transparent, ${accent}, transparent)`,
          borderRadius: "4px 0 0 4px",
        }}
      />
    </AbsoluteFill>
  );
}

function ThumbnailVariantB({
  titleText,
  hookText,
  niche,
}: ThumbnailProps) {
  const accent = nicheAccent(niche);
  const glow = nicheGlow(niche);
  const grid = nicheGrid(niche);

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg, overflow: "hidden" }}>
      {/* Grid */}
      <AbsoluteFill
        style={{
          backgroundImage: `linear-gradient(${grid} 1px, transparent 1px), linear-gradient(90deg, ${grid} 1px, transparent 1px)`,
          backgroundSize: "80px 80px",
          pointerEvents: "none",
        }}
      />

      {/* Center glow */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `radial-gradient(ellipse 70% 60% at 50% 50%, ${glow} 0%, transparent 70%)`,
          pointerEvents: "none",
        }}
      />

      {/* Centered glass card */}
      <div
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          width: "82%",
          background: COLORS.surface,
          border: `1px solid ${COLORS.surfaceBorder}`,
          borderRadius: RADIUS.lg,
          padding: "60px 72px",
          textAlign: "center",
        }}
      >
        <div
          style={{
            width: 64,
            height: 4,
            background: `linear-gradient(to right, ${accent}, transparent)`,
            borderRadius: 2,
            margin: "0 auto 32px",
          }}
        />
        {hookText && (
          <div
            style={{
              color: accent,
              fontSize: 22,
              fontFamily: FONTS.body,
              fontWeight: FONTS.semibold,
              letterSpacing: "0.14em",
              textTransform: "uppercase",
              marginBottom: 20,
            }}
          >
            {hookText}
          </div>
        )}
        <div
          style={{
            color: COLORS.text,
            fontSize: 80,
            fontFamily: FONTS.heading,
            fontWeight: FONTS.headingWeight,
            lineHeight: 1.15,
            letterSpacing: "-0.02em",
          }}
        >
          {titleText}
        </div>
      </div>
    </AbsoluteFill>
  );
}

function ThumbnailVariantC({
  titleText,
  hookText,
  niche,
}: ThumbnailProps) {
  const accent = nicheAccent(niche);
  const grid = nicheGrid(niche);

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg, overflow: "hidden" }}>
      {/* Bold diagonal split */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `linear-gradient(118deg, ${accent}22 0%, transparent 55%)`,
          pointerEvents: "none",
        }}
      />
      <AbsoluteFill
        style={{
          backgroundImage: `linear-gradient(${grid} 1px, transparent 1px), linear-gradient(90deg, ${grid} 1px, transparent 1px)`,
          backgroundSize: "80px 80px",
          pointerEvents: "none",
        }}
      />

      {/* Left border accent */}
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 0,
          bottom: 0,
          width: 10,
          backgroundColor: accent,
          boxShadow: `0 0 20px ${accent}`,
        }}
      />

      <div
        style={{
          position: "absolute",
          top: "50%",
          left: 80,
          right: 80,
          transform: "translateY(-50%)",
        }}
      >
        {hookText && (
          <div
            style={{
              color: COLORS.textMuted,
              fontSize: 22,
              fontFamily: FONTS.body,
              fontWeight: FONTS.semibold,
              letterSpacing: "0.16em",
              textTransform: "uppercase",
              marginBottom: 20,
            }}
          >
            {hookText}
          </div>
        )}
        <div
          style={{
            color: COLORS.text,
            fontSize: 96,
            fontFamily: FONTS.heading,
            fontWeight: FONTS.headingWeight,
            lineHeight: 1.05,
            letterSpacing: "-0.025em",
          }}
        >
          {titleText}
        </div>
        <div
          style={{
            marginTop: 32,
            width: 120,
            height: 4,
            backgroundColor: accent,
            borderRadius: 2,
          }}
        />
      </div>
    </AbsoluteFill>
  );
}

export function Thumbnail(props: ThumbnailProps) {
  const { variant = "a" } = props;
  if (variant === "b") return <ThumbnailVariantB {...props} />;
  if (variant === "c") return <ThumbnailVariantC {...props} />;
  return <ThumbnailVariantA {...props} />;
}
