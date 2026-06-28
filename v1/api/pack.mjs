// POST /api/pack { email, name?, company? }
// Captures + tags the subscriber in Kit, then returns the gated download URL.
import { captureWithTag } from "./_lib/convertkit.mjs";

const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
const TAG = "template_pack_claude_remotion";
const DOWNLOAD_URL = "/downloads/claude-remotion-template-pack.zip";

async function readBody(req) {
  if (req.body && typeof req.body === "object") return req.body;
  if (typeof req.body === "string" && req.body.length) {
    try {
      return JSON.parse(req.body);
    } catch {
      return Object.fromEntries(new URLSearchParams(req.body));
    }
  }
  const chunks = [];
  for await (const c of req) chunks.push(c);
  const raw = Buffer.concat(chunks).toString("utf8");
  if (!raw) return {};
  try {
    return JSON.parse(raw);
  } catch {
    return Object.fromEntries(new URLSearchParams(raw));
  }
}

export default async function handler(req, res) {
  if (req.method !== "POST") {
    res.statusCode = 405;
    res.setHeader("Allow", "POST");
    res.end(JSON.stringify({ error: "Method not allowed" }));
    return;
  }

  const wantsJson = (req.headers["content-type"] || "").includes("application/json");
  const sendJson = (code, obj) => {
    res.statusCode = code;
    res.setHeader("Content-Type", "application/json");
    res.end(JSON.stringify(obj));
  };

  let body;
  try {
    body = await readBody(req);
  } catch {
    return sendJson(400, { error: "Could not read request." });
  }

  const email = String(body.email ?? "").trim().toLowerCase();
  const name = String(body.name ?? "").trim().slice(0, 80) || undefined;
  const honeypot = String(body.company ?? "").trim();

  // Bots fill hidden fields — silently succeed without doing work.
  if (honeypot) return sendJson(200, { url: DOWNLOAD_URL });

  if (!EMAIL_RE.test(email)) return sendJson(400, { error: "Please enter a valid email." });

  try {
    await captureWithTag(email, TAG, name);
  } catch (err) {
    console.error("[pack] Kit error:", err.message);
    return sendJson(502, { error: "Could not reach our email service. Try again shortly." });
  }

  if (wantsJson) return sendJson(200, { url: DOWNLOAD_URL });
  // No-JS fallback: native form post → redirect to the download.
  res.statusCode = 302;
  res.setHeader("Location", DOWNLOAD_URL);
  res.end();
}
