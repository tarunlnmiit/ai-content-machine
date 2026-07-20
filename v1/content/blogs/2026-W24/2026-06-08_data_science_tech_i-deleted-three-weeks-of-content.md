---
title: "I Deleted Three Weeks of Content"
type: blog
niche: data_science_tech
date: 2026-06-08
week: 2026-W24
slug: i-deleted-three-weeks-of-content
tags: [content/blog, niche/data_science_tech, week/2026-W24]
---
# I Deleted Three Weeks of Content

*Claude helped me get it all back.*

The command looked reasonable at the time.

```
git filter-branch --index-filter \
'git rm -rf --cached --ignore-unmatch assets/' \
--prune-empty --tag-name-filter cat -- --all
```

Standard repo hygiene. I'd been accumulating binary files in git history — slides, carousels, PDFs — and it was bloating things. Filter-branch rewrites history and strips those files out. Clean, documented, widely used.

Except I misread the path. Instead of pruning a specific subdirectory of old files, I wiped my entire `assets/` directory from every commit in the repo's history. Then I ran a cleanup commit for good measure. Then I pushed.

`git status` showed nothing wrong. The working directory looked fine.

It took me about 40 seconds to notice something was off. Then I checked `assets/` and found it empty.

**What was actually lost**

I run three YouTube channels — data science, life and self-development, poetry. For the past month I'd been building a full content buffer: slides, carousels, worksheets, social posts, blog images for every piece. Three weeks of production-ready work sitting in that directory.

188MB total: slides 139MB, social posts 23MB, carousels 19MB, worksheets and PDFs 5MB, blog image directories 1.4MB.

Not backed up externally. Not duplicated anywhere. Just in git.

I've been a data scientist for ten years. I know git well enough to have done something like this.

**Step 1 — The reflog**

I opened Claude and told it what happened. I wasn't looking for sympathy. I needed to know if any of this was recoverable.

First thing it said: run `git reflog` and paste the output.

The reflog showed something like this:

```
HEAD@{0}: filter-branch: rewrote refs/heads/main
HEAD@{1}: commit: chore: clean up asset history
...
HEAD@{19}: commit: feat: add week 2 content assets
```

At position `HEAD@{19}`, before filter-branch ran, was the last commit that still had everything intact. Hash: `6d30a69`.

```
git checkout 6d30a69 -- assets/
```

186MB came back.

Most people know `git log` shows commit history. The reflog (`git reflog`) shows something different: every position HEAD has ever been at, for any reason. Filter-branch, resets, rebases — they all leave traces here. Reflog entries expire after 90 days by default, but immediately after a disaster, everything is still there. It should be the first thing you run when git history goes wrong.

**Step 2 — The missing PDFs**

Two files were still missing after the checkout.

Claude explained why without me having to ask: those PDFs had been deleted in a cleanup commit that ran before filter-branch, so even `6d30a69` didn't have them. The reflog wouldn't help here. We needed to go deeper.

```
git fsck --dangling
```

This outputs every "dangling" object in git's store — commits and blobs that are unreachable from any branch but haven't been garbage-collected yet. One dangling commit appeared: `f5d9a38`.

```
git show f5d9a38
```

It was the commit that had those two PDFs before they were deleted.

When you delete a file and commit that deletion, git doesn't immediately destroy the file's content. The blob — git's internal representation of file data — still exists in `.git/objects/`. It's just unreachable from any branch. `git fsck --dangling` surfaces these orphaned objects. This is git's forensics layer. Most developers never touch it. It's there, and it works.

**Step 3 — Blob extraction**

Claude had me extract the specific file contents directly by their blob hash:

```
git cat-file blob f2725aac2e8e9695a1fb58a98d37fd4ab2aa852d > worksheet1.pdf
git cat-file blob 764605c6d02c3ee0dc1b9a46328c449fed6dd3bc > worksheet2.pdf
```

Both files came back. Byte-perfect.

Full recovery. 188MB. Everything.

**What I built after**

Three things, immediately:

Git LFS. Large File Storage now tracks my binary assets. They live on GitHub's LFS servers, not in the repo's object store. Filter-branch can't touch them.

A guard hook. I added a PreToolUse hook in Claude Code that blocks `git filter-branch`, `git reset --hard`, and `rm -rf` patterns on asset paths. It runs before Claude executes any bash command.

Recovery anchor tags. After any major commit, I now create a tag: `git tag recovery-anchor-YYYY-MM-DD`. Tags survive filter-branch. They're permanent pointers into history.

**The part worth sitting with**

I knew the reflog existed. I'd read "git's undo button" a hundred times in tutorials.

Under pressure, with an empty folder in front of me, I would not have reached for it in the right sequence. And `git fsck --dangling` followed by blob extraction — I knew this layer existed in theory. I would never have navigated it alone, in the right order, without knowing in advance what I was looking for.

Claude did. Not because it's smarter. Because it wasn't panicking.

It started with the reflog, worked down through the recovery layers methodically, and pivoted strategy when two files were still missing after step one. That's debugging. Staying systematic in someone else's crisis is a different skill than generating things from scratch.

I'd been underestimating that use case.

<!-- Medium tags: ai, claude, git, data-science, developer-tools -->
<!-- Target keyphrase: git reflog recovery -->
<!-- SEO title: I Deleted Three Weeks of Content. Claude Helped Me Get It All Back -->
<!-- SEO description: A git filter-branch mistake wiped 188MB of content from every commit in the repo's history. Here's how reflog, dangling commits, and blob extraction recovered all of it. -->
