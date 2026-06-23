// GET /api/worksheet?slug=<slug>&t=<token> — verify token, stream the PDF.
import { createReadStream, statSync } from "node:fs";
import { resolve } from "./_lib/manifest.mjs";
import { verify } from "./_lib/token.mjs";

export default function handler(req, res) {
  const slug = String(req.query?.slug ?? "");
  const token = String(req.query?.t ?? "");

  if (!verify(token, slug)) {
    res.statusCode = 403;
    res.setHeader("Content-Type", "text/plain; charset=utf-8");
    res.end("Link expired or invalid. Request the worksheet again.");
    return;
  }

  const ws = resolve(slug);
  if (!ws) {
    res.statusCode = 404;
    res.setHeader("Content-Type", "text/plain; charset=utf-8");
    res.end("Worksheet not found.");
    return;
  }

  let size;
  try {
    size = statSync(ws.pdfPath).size;
  } catch {
    res.statusCode = 404;
    res.setHeader("Content-Type", "text/plain; charset=utf-8");
    res.end("Worksheet file missing.");
    return;
  }

  const filename = `${slug}.pdf`;
  res.statusCode = 200;
  res.setHeader("Content-Type", "application/pdf");
  res.setHeader("Content-Length", size);
  res.setHeader("Content-Disposition", `inline; filename="${filename}"`);
  res.setHeader("Cache-Control", "private, no-store");

  const stream = createReadStream(ws.pdfPath);
  stream.on("error", () => {
    if (!res.headersSent) res.statusCode = 500;
    res.end();
  });
  stream.pipe(res);
}
