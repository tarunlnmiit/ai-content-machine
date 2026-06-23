// POST /api/subscribe { email, slug, company? }
// Classifies + tags the subscriber in Kit, then returns a signed PDF URL.
import { resolve } from "./_lib/manifest.mjs";
import { captureAndTag } from "./_lib/convertkit.mjs";
import { sign } from "./_lib/token.mjs";

const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

async function readBody(req) {
  if (req.body && typeof req.body === "object") return req.body;
  if (typeof req.body === "string" && req.body.length) {
    try {
      return JSON.parse(req.body);
    } catch {
      return Object.fromEntries(new URLSearchParams(req.body));
    }
  }
  // Fallback: read the raw stream.
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
  const slug = String(body.slug ?? "").trim();
  const honeypot = String(body.company ?? "").trim();

  // Bots fill hidden fields — silently succeed without doing work.
  if (honeypot) return sendJson(200, { url: `/get-worksheet?slug=${encodeURIComponent(slug)}` });

  if (!EMAIL_RE.test(email)) return sendJson(400, { error: "Please enter a valid email." });

  const ws = resolve(slug);
  if (!ws) return sendJson(404, { error: "Unknown worksheet." });

  try {
    await captureAndTag(email);
  } catch (err) {
    console.error("[subscribe] Kit error:", err.message);
    return sendJson(502, { error: "Could not reach our email service. Try again shortly." });
  }

  const token = sign(slug);
  const url = `/api/worksheet?slug=${encodeURIComponent(slug)}&t=${encodeURIComponent(token)}`;

  if (wantsJson) return sendJson(200, { url });
  // No-JS fallback: native form post → redirect straight to the PDF.
  res.statusCode = 302;
  res.setHeader("Location", url);
  res.end();
}
