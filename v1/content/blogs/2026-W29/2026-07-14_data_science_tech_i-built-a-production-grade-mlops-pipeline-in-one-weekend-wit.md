---
title: "Your \"Production\" MLOps Pipeline Has a Silent Failure You Haven't Noticed Yet"
type: blog
niche: data_science_tech
date: 2026-07-14
week: 2026-W29
slug: i-built-a-production-grade-mlops-pipeline-in-one-weekend-wit
tags: [content/blog, niche/data_science_tech, week/2026-W29]
---
# Your "Production" MLOps Pipeline Has a Silent Failure You Haven't Noticed Yet

*Every tool, the exact swap for each paid default, and the one relative-path bug that ate a Saturday.*

You're not serving predictions at Netflix scale. You're serving maybe 200 a day. That single honest number is why I built a local MLOps pipeline over one weekend with only free tools. The models it runs have been on autopilot ever since — no Kubernetes cluster, no $400 monthly bill.

Here's the stack, tool by tool, with the paid default I rejected for each.

![14 hours across a Saturday and Sunday — most of it fighting Docker networking, not modeling](/content/blogs/2026-W29/2026-07-14_data_science_tech_i-built-a-production-grade-mlops-pipeline-in-one-weekend-wit_images/01_hook_developer-workspace-with-laptop-and-terminal-at-ni.jpg)
*14 hours across a Saturday and Sunday — most of it fighting Docker networking, not modeling — Photo by [Daniil Komov](https://www.pexels.com/photo/modern-laptop-on-wooden-desk-with-code-displayed-34803994/) on Pexels*

**Orchestrator — Prefect, not Airflow.** Airflow's scheduler wants its own Postgres and a webserver babysitting it. Prefect ran as a single local process and I had flows registered in under an hour. That hour-versus-afternoon gap is the whole ethos of this build.

**Tracking + registry — MLflow, self-hosted.** SQLite backend, a local `./mlruns` folder. I rejected Weights & Biases — genuinely great product, but the free tier caps private projects and I didn't want my experiment history living on someone else's server.

**Serving — FastAPI + Uvicorn, not a managed SageMaker endpoint.** A 40-line app loads the model straight from the MLflow registry. I'm not paying for an idle GPU instance 24/7 to answer a few hundred requests.

**Monitoring — Evidently → Prometheus + Grafana.** Evidently generates drift reports as static HTML; Prometheus scrapes them for the dashboards. I skipped Arize and Fiddler entirely — they're built for teams with a data-quality budget, and Evidently caught the feature drift I cared about, for free.

**Scheduler — Prefect's cron plus a plain systemd timer as the dumb backstop.** No Kubernetes CronJob. Standing up a cluster to run one nightly retrain is the exact over-engineering that keeps a weekend project from ever shipping.

**What "production-grade" means here**

The most honest example running on autopilot isn't a fraud model — it's the content machine writing this. A scheduler daemon wakes up, checks a SQLite table for rows where status is `pending` and the posting time has passed, publishes, then flips the row to `published`.

I'd be lying if I claimed five-nines uptime on a laptop-hosted daemon. So "production-grade" means something I can defend: it recovers from transient failures (retry with backoff on timeouts and 429s, hard stop on a 401), and it's idempotent — phase markers so a re-run never double-publishes. The real discipline is a guardrail: the dashboard has no publish endpoint at all, so nothing ships without a human approval gate. That constraint is the feature, not a limitation.

**The bug that ate a Saturday wasn't a crash — it was silence**

I had MLflow logging to SQLite with the artifact store set to a relative path, `./mlruns`. Every run showed green in the UI. Metrics logged fine. I moved on.

Then the retrain scheduler started firing from a different working directory — because cron runs from `$HOME`, not your project folder — and MLflow happily wrote a *second* `mlruns` tree there. For a full day my "autopilot" was training models into a directory nothing else read from. No error. No warning. The registry quietly pointed at Friday's stale artifacts.

The tell: predictions never changed even though fresh runs kept appearing in the tracking UI. Once I stopped trusting the green checkmarks and `ls`'d the path the serving container mounted, the two-tree split was obvious. The fix was boring — absolute paths in one `.env` the cron sources, plus a one-line startup assert:

```python
import os
from pathlib import Path

# Both training and serving MUST resolve to the same store.
TRACKING_URI = os.environ["MLFLOW_TRACKING_URI"]      # e.g. sqlite:////home/you/proj/mlflow.db
ARTIFACT_ROOT = Path(os.environ["MLFLOW_ARTIFACT_ROOT"]).resolve()

assert ARTIFACT_ROOT.is_absolute(), f"Artifact root must be absolute, got {ARTIFACT_ROOT}"
assert ARTIFACT_ROOT.exists(), f"Artifact root missing — cron probably ran from the wrong cwd: {ARTIFACT_ROOT}"
```

A config that silently does nothing is worse than one that errors, because you'll spend the weekend debugging a model that was never broken.

**Where everyone wastes their weekend**

Everyone treats MLOps like they're deploying at Netflix scale when they're serving 200 predictions a day. The standard advice — spin up Kubernetes, pay for a managed platform, orchestrate everything — solves a throughput and team-coordination problem most solo practitioners don't have. It costs you a weekend of YAML plus $200/month to *feel* production-grade while a cron job and a SQLite file would've done the same work.

I ran my last two projects on exactly that: a Python script triggered by cron, model versioned as a timestamped file, predictions logged to SQLite, a 10-line drift check that emails me when input distributions shift. Untouched for months. Kubernetes wouldn't have made one prediction more accurate — it would've handed me a second system to babysit. The real skill at small scale isn't scaling up. It's knowing exactly how little machinery your actual traffic needs.

Which is why I cut a corner on purpose. On one home project I skipped drift monitoring entirely — no Evidently, no statistical tests. I log every prediction with its inputs to a Parquet file and eyeball a weekly summary Sunday mornings with coffee. I know it hasn't bitten me because a bad prediction from my home-energy forecaster costs me a squint at a chart, not a churned customer. The day I point this at something where wrong predictions cost money, that dumb Parquet log graduates into a real monitoring service. Until then it saved me a full day for the part that mattered: making retraining reproducible.

**The one gotcha that will cost you the most hours**

If you copy nothing else, copy this. Cron runs with almost none of your shell environment — no `PATH`, no activated venv, no `conda`, working directory `$HOME`. So `python` resolves to the system 3.9 instead of your venv, and every relative path points somewhere else. It runs clean in your terminal, then fails at 2am with a traceback nobody's awake to read.

```bash
# Wrong — resolves to system python, runs from $HOME
0 3 * * * python train.py

# Right — full path to venv python, absolute script, failures ping you
0 3 * * * MAILTO=you@example.com /home/you/proj/.venv/bin/python /home/you/proj/train.py
```

Absolute paths everywhere, the venv's Python by full path, and a `MAILTO` or Slack webhook so a dead run pings you instead of rotting in a logfile. I lost most of a Saturday to exactly this — the job "worked," the dashboard quietly stopped updating.

**The honest numbers, and the ceiling**

Setup was about 14 hours across a weekend, most of it fighting Docker networking, not modeling. Monthly cost is basically my electricity bill against the ~$250–400/month I was quoting for a comparable SageMaker Pipelines + managed MLflow setup at low volume.

The ceiling is real and worth naming. This works because I'm the only user and my models retrain nightly on data that fits in memory. It breaks the day you need concurrent runs, a real feature store, or someone else on the team depending on it at 2am — because "on autopilot" quietly means "on my laptop staying awake," and a cron job on one machine has no on-call, no cross-failure retries, no audit trail anyone else trusts. Fine up to a few models and a single operator. Past that, you're paying the managed platform for the pager, not the compute.

So before you provision anything: go count your predictions per day. That number, not the conference talks, tells you how much machinery you're allowed to skip.

If you want the exact `.env`, the startup asserts, and the drift-check script as a copy-paste starter, I put them in a free companion worksheet — grab it and join the data science list here.

<!-- Medium tags: MLOps, Machine Learning, Data Science, Python, DevOps -->
<!-- Target keyphrase: local MLOps pipeline -->
<!-- SEO title: Local MLOps Pipeline With Free Tools (No Kubernetes) -->
<!-- SEO description: How to build a local MLOps pipeline with free tools — Prefect, MLflow, FastAPI — no Kubernetes, no $400/mo platform. The exact weekend setup and the bug that ate a Saturday. -->