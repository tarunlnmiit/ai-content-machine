---
title: "Deploy: Template Pack landing page"
type: reel
niche: data_science_tech
week: 2026-W26
slug: deploy
tags: [content/reel, niche/data_science_tech, week/2026-W26]
---
# Deploy: Template Pack landing page

Built into your existing Vercel project **worksheets-thebreathnetwork** (same `api/` + `public/`).
After deploy the page lives at:

```
https://<your-vercel-domain>/template-pack
```

## What was added
- `public/template-pack/index.html` — the landing page (email form → gated download)
- `api/pack.mjs` — POST endpoint: validates email, subscribes via ConvertKit, returns the zip URL
- `api/_lib/convertkit.mjs` — added `captureWithTag()` + optional first name (existing code untouched)
- `public/downloads/claude-remotion-template-pack.zip` — the gated file
- `vercel.json` — added a `Content-Disposition: attachment` header for `/downloads/*`

Subscribers are tagged **`template_pack_claude_remotion`** in Kit so you can see who came from this reel.

## One env var to confirm
The endpoint reuses `CONVERTKIT_API_KEY`. It's in your local `.env`; make sure it's also set in
Vercel: **Project → Settings → Environment Variables** (Production). If the worksheet form already
works in prod, this is already set and you're done.

## Deploy (from your machine — needs your Vercel login)

If the project auto-deploys from Git:
```
git add api/pack.mjs api/_lib/convertkit.mjs public/template-pack public/downloads vercel.json
git commit -m "feat: template-pack landing page + ConvertKit capture"
git push
```

Or deploy directly with the CLI:
```
npm i -g vercel        # if not installed
vercel link            # pick worksheets-thebreathnetwork (already linked via .vercel)
vercel --prod
```

## Test after deploy
1. Open `/template-pack`, submit a test email → you should see the success state + download.
2. Confirm the address appears in Kit with the `template_pack_claude_remotion` tag.
3. Click the download → `claude-remotion-template-pack.zip` should download.

## Wire it into the funnel
- Put the `/template-pack` URL (UTM-tagged via `scripts/lib/utm.py`) in the **auto-DM** after the
  free guide, and in the **pinned comment**. Never in the IG post body.
- Updating the pack later: replace the files in
  `content/reels/2026-W26/2026-06-28_ds_claude-video-editor/template-pack/`, re-zip into
  `public/downloads/claude-remotion-template-pack.zip`, redeploy.
