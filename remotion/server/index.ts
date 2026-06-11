import express from "express";
import path from "path";
import { bundle } from "@remotion/bundler";
import { renderMedia, renderStill, selectComposition } from "@remotion/renderer";

const app = express();
app.use(express.json());

const PORT = 3001;
const REMOTION_ROOT = path.resolve(__dirname, "..");
const ENTRY_POINT = path.join(REMOTION_ROOT, "src", "index.ts");

// Bundle is cached after first request — subsequent renders skip re-bundling
let bundleLocation: string | null = null;

async function getBundle(): Promise<string> {
  if (bundleLocation) return bundleLocation;
  console.log("Bundling Remotion project (first request only)...");
  bundleLocation = await bundle({
    entryPoint: ENTRY_POINT,
    webpackOverride: (config) => config,
  });
  console.log("Bundle ready:", bundleLocation);
  return bundleLocation;
}

// In-memory job store — sufficient for a local workflow server
interface Job {
  status: "pending" | "rendering" | "done" | "failed";
  progress: number;
  outputFile?: string;
  error?: string;
}
const jobs = new Map<string, Job>();
let jobCounter = 0;

function newJobId(): string {
  return `job-${Date.now()}-${++jobCounter}`;
}

app.get("/health", (_req, res) => {
  res.json({ status: "ok", bundleCached: bundleLocation !== null });
});

/**
 * POST /render
 * Body: { compositionId, inputProps, outputFile, codec? }
 * Returns: { jobId }
 */
app.post("/render", async (req, res) => {
  const { compositionId, inputProps = {}, outputFile, codec = "h264" } = req.body as {
    compositionId: string;
    inputProps?: Record<string, unknown>;
    outputFile: string;
    codec?: string;
  };

  if (!compositionId || !outputFile) {
    return res.status(400).json({ error: "compositionId and outputFile are required" });
  }

  const jobId = newJobId();
  jobs.set(jobId, { status: "pending", progress: 0 });
  res.json({ jobId });

  // Run async, don't await in request handler
  (async () => {
    try {
      jobs.set(jobId, { status: "rendering", progress: 0 });
      const bundlePath = await getBundle();
      const composition = await selectComposition({
        serveUrl: bundlePath,
        id: compositionId,
        inputProps,
      });
      await renderMedia({
        composition,
        serveUrl: bundlePath,
        codec: codec as Parameters<typeof renderMedia>[0]["codec"],
        outputLocation: outputFile,
        inputProps,
        onProgress: ({ progress }) => {
          jobs.set(jobId, { status: "rendering", progress: Math.round(progress * 100) });
        },
      });
      jobs.set(jobId, { status: "done", progress: 100, outputFile });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      console.error(`Job ${jobId} failed:`, msg);
      jobs.set(jobId, { status: "failed", progress: 0, error: msg });
    }
  })();
});

/**
 * POST /still
 * Body: { compositionId, inputProps, outputFile, frame? }
 * Returns: { jobId }
 */
app.post("/still", async (req, res) => {
  const { compositionId, inputProps = {}, outputFile, frame = 0 } = req.body as {
    compositionId: string;
    inputProps?: Record<string, unknown>;
    outputFile: string;
    frame?: number;
  };

  if (!compositionId || !outputFile) {
    return res.status(400).json({ error: "compositionId and outputFile are required" });
  }

  const jobId = newJobId();
  jobs.set(jobId, { status: "pending", progress: 0 });
  res.json({ jobId });

  (async () => {
    try {
      jobs.set(jobId, { status: "rendering", progress: 0 });
      const bundlePath = await getBundle();
      const composition = await selectComposition({
        serveUrl: bundlePath,
        id: compositionId,
        inputProps,
      });
      await renderStill({
        composition,
        serveUrl: bundlePath,
        output: outputFile,
        inputProps,
        frame,
        imageFormat: "png",
      });
      jobs.set(jobId, { status: "done", progress: 100, outputFile });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      console.error(`Job ${jobId} failed:`, msg);
      jobs.set(jobId, { status: "failed", progress: 0, error: msg });
    }
  })();
});

/**
 * GET /status/:jobId
 * Returns: { status, progress, outputFile?, error? }
 */
app.get("/status/:jobId", (req, res) => {
  const job = jobs.get(req.params.jobId);
  if (!job) return res.status(404).json({ error: "Job not found" });
  res.json(job);
});

app.listen(PORT, () => {
  console.log(`Remotion render server listening on http://localhost:${PORT}`);
  console.log(`  POST /render  — render full video`);
  console.log(`  POST /still   — export single PNG frame`);
  console.log(`  GET  /status/:jobId — poll job progress`);
});
