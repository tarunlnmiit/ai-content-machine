// Short-lived HMAC token gating PDF access. Keeps the PDF path non-guessable
// so the email capture is a real gate, not a speed bump.
import { createHmac, timingSafeEqual } from "node:crypto";

const TTL_MS = 10 * 60 * 1000; // ~10 minutes

function secret() {
  const s = process.env.WORKSHEET_TOKEN_SECRET;
  if (!s) throw new Error("WORKSHEET_TOKEN_SECRET is not set");
  return s;
}

function b64url(buf) {
  return Buffer.from(buf).toString("base64url");
}

function digest(payload) {
  return createHmac("sha256", secret()).update(payload).digest("base64url");
}

// token = base64url(`${slug}|${exp}`) + "." + hmac
export function sign(slug, ttlMs = TTL_MS) {
  const exp = Date.now() + ttlMs;
  const payload = `${slug}|${exp}`;
  return `${b64url(payload)}.${digest(payload)}`;
}

export function verify(token, slug) {
  if (typeof token !== "string" || !token.includes(".")) return false;
  const [payloadB64, sig] = token.split(".");
  let payload;
  try {
    payload = Buffer.from(payloadB64, "base64url").toString("utf8");
  } catch {
    return false;
  }
  const [tokenSlug, expStr] = payload.split("|");
  if (tokenSlug !== slug) return false;

  const exp = Number(expStr);
  if (!Number.isFinite(exp) || Date.now() > exp) return false;

  const expected = digest(payload);
  const a = Buffer.from(sig);
  const b = Buffer.from(expected);
  if (a.length !== b.length) return false;
  return timingSafeEqual(a, b);
}
