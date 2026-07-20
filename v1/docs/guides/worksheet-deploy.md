---
title: "Worksheet app deploy (Vercel prebuilt — corrected 2026-07-16)"
type: doc
slug: worksheet-deploy
tags: [content/doc]
---
# Worksheet app deploy (Vercel prebuilt — corrected 2026-07-16)

How new worksheet PDFs actually go live on `worksheets-thebreathnetwork.vercel.app`.
Corrects the previously documented `cd v1 && vercel --prod` method, which now fails.

## Why

The Vercel project `worksheets-thebreathnetwork` (`rootDirectory=v1`) has **no git
integration** — `git commit`/`git push` never deploys anything; only the Vercel CLI does.

A plain source deploy (`vercel --prod`, from repo root or from `v1`) now **fails**: it
uploads the whole `v1` tree (~237 MB) and hits Vercel's 100 MB per-file limit on
`v1/remotion/node_modules/.remotion/chrome-headless-shell` (153 MB). `.vercelignore`'s
directory patterns (`remotion/`, `assets/`, `node_modules/`) are **not honored** in this
setup — only `*.ext` globs are — so the heavy binary slips through regardless. Do not
try to fix this by editing `.vercelignore`.

## Correct method: prebuilt deploy

Build locally, upload only the build output (~5.5 MB — PDFs + api functions, no
`node_modules`, no `remotion/`):

```bash
cd "/Users/tarungupta/Making It Big/Claude/content-machine/v1"
vercel pull --yes --environment production   # once, or whenever it errors "project_settings_required"
vercel build --prod --yes                     # runs build-worksheets-manifest.mjs + copy-pdfs-to-public.mjs → .vercel/output
vercel deploy --prebuilt --prod --yes         # uploads only .vercel/output
```

`vercel build` copies every PDF under `output/worksheets/**` into
`public/worksheets/<slug>.pdf` and regenerates `worksheets-manifest.json` — same build
steps as before, just run locally instead of in Vercel's remote sandbox.

## Verify after deploy

Each new slug must return 200 on both routes:

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://worksheets-thebreathnetwork.vercel.app/get-worksheet/<slug>
curl -s -o /dev/null -w "%{http_code}\n" -L https://worksheets-thebreathnetwork.vercel.app/worksheets/<slug>.pdf
```

## Obsolete

The old note "Until Root Directory is set to v1, deploy via `cd v1 && vercel --prod`" no
longer applies: Root Directory *is* `v1` now, and the source deploy fails regardless of
that setting — always use the prebuilt flow above.
