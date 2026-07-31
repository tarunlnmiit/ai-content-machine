# Pandas Isn't a Beginner Library — It's a Bad Pipeline Library, and Those Are Different Things

*Four libraries, ten years, and the observable symptom that tells you to switch — before production tells you at 2 a.m.*

An 800 MB Parquet file killed a 16 GB machine, and I spent two days blaming my own code. That job is why I stopped arguing about pandas vs Polars vs DuckDB as a taste question and started treating it as a physics question: where does the data live, what shape is it, and which library's memory model fits.

Here's what happened. I loaded the file with `pd.read_parquet()` expecting 2 GB in memory. It sat at 11 GB and then the kernel died. The file had two high-cardinality string columns — session IDs and URLs — stored as `object` dtype after load, roughly 60 million rows, and every one of those strings became a separate Python object with its own pointer overhead. The data size wasn't the problem. The *shape* was: width in string columns, not length in rows.

![The two days I spent optimizing my code, when the memory was already gone before my code ran](/content/blogs/2026-W31/2026-07-29_data_science_tech_the-four-python-libraries-data-engineers-reach-for-before-an_images/01_hook_laptop-screen-showing-terminal-with-memory-usage-o.jpg)
*The two days I spent optimizing my code, when the memory was already gone before my code ran — Photo by [Viralyft](https://www.pexels.com/photo/qr-code-on-screen-of-laptop-17659372/) on Pexels*

The two days is the part that still stings. I chunked the read. I added `del` and `gc.collect()`. I rewrote the groupby to be lazier. I blamed a merge I was sure was fanning out. None of it moved the needle, because the memory was gone before my transformation logic ever executed. What broke it open was dumping per-column memory instead of eyeballing `df.info()`:

```python
import pandas as pd

df = pd.read_parquet("clickstream.parquet")

usage = df.memory_usage(deep=True).sort_values(ascending=False) / 1e9
print(usage.head(10))          # GB per column, not the lie df.info() tells you

# two columns were 9 of the 11 GB
for col in ["session_id", "url"]:
    df[col] = df[col].astype("category")
```

Two columns accounted for 9 of the 11 GB. Casting them to `category` and then pushing the aggregation into DuckDB over the Parquet file directly took the job from OOM to about 40 seconds. `deep=True` in the first ten minutes would have saved me both days.

## Pandas is oversold — as a pipeline library, specifically

I want to be precise about the complaint, because "pandas bad" is a lazy take and I don't hold it. Pandas is a fantastic exploration tool. I still open a notebook and `read_csv` something every week. But the moment it becomes the load-bearing layer of a nightly job, you've signed up for a class of bug that doesn't show up in tests.

I had a job that ran clean for four months and then quietly started writing wrong numbers. An upstream team added a column of mostly-nulls. Pandas inferred it as `object`. A downstream `merge` on a column that was `int64` on one side and `float64` on the other silently dropped about 8% of the rows. Nothing errored. The dashboard got a little bit wrong, and nobody noticed for eleven days.

A database would have refused that join or told me the types didn't match. DuckDB, Postgres, even the `sqlite3` sitting right there in the standard library that everyone skips past. Schema enforcement is the entire job of a database, and an inference heuristic is not a substitute for one.

## The same job, fixed twice, by two different libraries

A daily 40 GB clickstream aggregation ran 52 minutes in pandas with chunked reads and constant memory babysitting. We were on a 64 GB box and it still OOM'd about once a week when a partition skewed. I rewrote the aggregation in Polars using the lazy API — same eight-ish groupbys — and it came down to 4 minutes 10 seconds, peak memory 11 GB instead of 58 GB. The file shrank from roughly 340 lines to 90, because all the manual chunking and reduce logic disappeared.

Six months later we needed to join that output against a 2 TB warehouse table, and Polars was the wrong tool again. Not because it's slow — because we were now pulling 2 TB across the network into a machine to do work the warehouse could do in place. That job went back to plain SQL through DuckDB reading Parquet on S3, and runtime stopped being the metric that mattered: we went from about $180/day in egress and compute to about $12/day.

The library choice is downstream of where the data physically lives. I keep relearning that one.

![The fastest local engine still loses to the query that never moved the data](/content/blogs/2026-W31/2026-07-29_data_science_tech_the-four-python-libraries-data-engineers-reach-for-before-an_images/02_section3_server-racks-in-a-data-center-with-blue-lights.jpg)
*The fastest local engine still loses to the query that never moved the data — Photo by [panumas nikhomkhai](https://www.pexels.com/photo/data-center-server-racks-with-active-equipment-37730212/) on Pexels*

## The switching signals, one per library

These get loud once each library has burned you once.

**Pandas.** The signal isn't the crash. It's watching `df.memory_usage(deep=True)` against machine RAM and noticing a single dataframe crossing roughly a fifth of available memory — you're already in trouble, because the next groupby will triple it. The other tell: a groupby that took 8 seconds on last quarter's data takes 4 minutes on this quarter's. Pandas didn't get slower. You crossed the point where it's spilling and thrashing.

**Polars.** More subtle, because you stop having speed problems and start hitting the ceiling of a single machine. When `scan_parquet` with lazy evaluation still can't finish because the working set genuinely doesn't fit one box, or when your input is 200 files across S3 partitions and you're writing your own concat loop — you wanted a distributed engine, not a faster local one. The other tell: if you're calling `.to_pandas()` three times inside one pipeline to reach some library that doesn't speak Arrow, you're paying a full memory copy each time and you've spent the entire reason you switched.

**DuckDB.** I love it right up until concurrency shows up. Two processes wanting to write the same file, or a scheduled job colliding with an ad-hoc analyst query, gives you lock contention — and that's your signal you needed a real server-backed warehouse. It's a single-writer analytical engine and it never pretended otherwise.

**PySpark.** This signal runs the other direction and nobody says it out loud. If your job's actual compute is 40 seconds and your JVM startup plus shuffle overhead is 3 minutes, you've over-provisioned the problem. Check the Spark UI: stages spending more time in scheduling than execution mean come back down the ladder.

For years I told people pandas was the beginner library and real engineers graduate to Spark. I said it in code reviews. In 2019 I spent three weeks rewriting a pandas job into PySpark because it "wouldn't scale," and the final dataset was 4.2 GB. It ran in 90 seconds on a laptop before I touched it, and 6 minutes on the cluster after, once you counted JVM spin-up. I'd been choosing tools by the size of the problem I imagined instead of the one on disk.

So here's the only monitoring I insist on: a rough runtime log for every recurring job. Nothing fancy — runtime and input row count, one line per run. The switch is due when that curve stops being a straight line. Production will tell you the same thing eventually, at 2 a.m., with a stakeholder watching.

<!-- worksheet-cta -->

---

### Want to put this into practice?

[Download Find Your Own 11GB Moment Before Production Does →](https://worksheets-thebreathnetwork.vercel.app/get-worksheet/the-four-python-libraries-data-engineers-reach-for-before-an)

_Free PDF. Enter your email and it opens right away._

<!-- Medium tags: Data Science, Python, Data Engineering, Pandas, Polars -->
<!-- Target keyphrase: pandas vs polars vs duckdb -->
<!-- SEO title: Pandas vs Polars vs DuckDB: When to Switch -->
<!-- SEO description: Pandas vs Polars vs DuckDB (and PySpark): real benchmarks, memory limits, and the exact switching signals that tell you when to move off each one. -->