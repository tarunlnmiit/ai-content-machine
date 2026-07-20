---
title: "Git Disaster Recovery — 3-Command Cheat Sheet"
type: reel
week: 2026-W24
slug: cheat-sheet
tags: [content/reel, week/2026-W24]
---
# Git Disaster Recovery — 3-Command Cheat Sheet

*Companion to: "I Deleted Three Weeks of Content"*
*DM this when someone comments REFLOG.*

Run these in order. Each one only matters if the previous step didn't recover everything.

---

**1. Reflog — recovers anything still reachable from HEAD's history**

`git reflog` shows every position HEAD has ever been at — resets, rebases, filter-branch, all of it. Entries expire after 90 days, but right after a disaster they're all still there.

```
git reflog
# find the last good commit hash before things broke, then:
git checkout <good-commit-hash> -- <path>
```

**2. Dangling objects — recovers content deleted *before* the disaster**

If a file was deleted in an earlier commit, the reflog checkout above won't bring it back — that commit never had it either. Check the object store instead:

```
git fsck --dangling
git show <dangling-commit-hash>
```

Git never destroys a blob the moment you delete it — it just becomes unreachable from any branch. `fsck --dangling` surfaces those orphaned commits/blobs before garbage collection sweeps them.

**3. Blob extraction — pulls back one exact file by its content hash**

Once you've found the blob hash for the missing file (from `git show` above or `git cat-file -p <tree-hash>`):

```
git cat-file blob <blob-hash> > recovered_file.ext
```

Byte-perfect recovery, no matter how deep in history it was buried.

---

**Prevent the next one:**
- Git LFS for binary assets — they live outside the object store, filter-branch can't touch them.
- A pre-tool-use hook that blocks `git filter-branch`, `git reset --hard`, and `rm -rf` on asset paths.
- `git tag recovery-anchor-YYYY-MM-DD` after any major commit — tags survive filter-branch.
