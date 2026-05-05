# Next steps to ship the coordination dashboard

This repo is a working local skeleton. Three things to do — all safe, none touch `planetai.fab.city` or the existing `planetai` Worker.

## Step 0 — what's already running, and what we won't touch

The existing site at `planetai.fab.city` is served by a **Cloudflare Worker** named `planetai`, configured in `planetai_publish/wrangler.toml` with Basic Auth and `run_worker_first = true`. Its DNS record lives in the `fab.city` zone.

The new dashboard runs on a **separate Cloudflare product** (Pages), at a separate DNS record (`coord.planetai.fab.city`), in the same zone. They are independent the way two rooms in the same building are independent. None of the steps below modify the existing Worker, its routes, its config, or the `planetai.fab.city` DNS record.

## Step 1 — push the new repo to GitHub

From this directory:

```bash
git init -b main
git add .
git commit -m "scaffold: planetai-coordination v0.1 — repo skeleton + 8 seed decisions"
```

Then create the empty repo on GitHub (proposed: `fabcity/planetai-coordination`):

```bash
# easiest, if you have the gh CLI:
gh repo create fabcity/planetai-coordination --public \
  --description "Coordination layer for PLANETAI — decision log, reviews, tracks, pilots." \
  --source=. --remote=origin --push

# or manually: create the repo at github.com/organizations/fabcity/repositories/new, then:
# git remote add origin git@github.com:fabcity/planetai-coordination.git
# git push -u origin main
```

After this step: the code is on GitHub. Nothing has touched Cloudflare yet.

## Step 2 — connect Cloudflare Pages to the new GitHub repo

In the Cloudflare dashboard: **Workers & Pages** → **Create** → tab **Pages** → **Connect to Git**.

Authorize Cloudflare to read your GitHub (one-time). Select `fabcity/planetai-coordination`.

Build configuration:

| Field | Value |
|---|---|
| Project name | `planetai-coordination` |
| Production branch | `main` |
| Framework preset | None |
| Build command | *(leave empty)* |
| Build output directory | `/` |
| Root directory | *(leave empty)* |

Click **Save and Deploy**. Within ~30 seconds you get a URL like `https://planetai-coordination.pages.dev`. Open it; verify the dashboard renders.

After this step: the dashboard is live on a Cloudflare-owned domain. `planetai.fab.city` is untouched.

## Step 3 — add the custom domain `coord.planetai.fab.city`

In the Pages project just created: **Custom domains** → **Set up a custom domain** → enter `coord.planetai.fab.city` → **Continue**.

Cloudflare detects that `fab.city` is in your account and offers to add the DNS record automatically. Confirm. It creates a CNAME: `coord.planetai` → `planetai-coordination.pages.dev`. SSL provisions automatically (~1 minute).

Open `https://coord.planetai.fab.city` in a fresh browser tab — dashboard loads.

After this step: the dashboard is live at the final URL. The DNS record for `coord.planetai` is brand-new; `planetai.fab.city`'s DNS record is unchanged.

## Step 4 — smoke test

Open these in order:

- `https://planetai.fab.city` — observatory still loads (Basic Auth still works)
- `https://planetai.fab.city/core-ideas-paper.pdf` — paper still loads
- `https://coord.planetai.fab.city` — coordination dashboard loads
- `https://coord.planetai.fab.city/decisions/2026-05-01_hub-architecture-12-to-4.html` — a deep page renders

If any of the first two fail: stop and investigate. They should not.

## Step 5 — your edit loop (no terminal required)

Three ways to land a change. All web-only after Step 1.

**Quickest — GitHub web editor.** Navigate to a YAML file in the GitHub UI (or click the *Edit on GitHub* link on any dashboard page). Edit in browser. Click *Commit changes* (commits to `main` directly if you have write access, or opens a pull request if you don't). The `.github/workflows/build.yml` action runs `python3 scripts/build.py`, commits the regenerated HTML back with `[skip ci]`, and Cloudflare Pages redeploys. Total: one to two minutes.

**Form-based — for partners who shouldn't have to think about YAML.** Two GitHub Issue Forms ship with the repo: *Propose a decision* and *Ack or push back on a review*. Partners fill the form fields, submit, and the result is a labelled GitHub issue. A maintainer (you or Lucas) converts the issue body into a YAML file and commits. Same auto-build path takes over from there.

**Terminal — only if you want to.** The local build still works:

```bash
pip install pyyaml
python3 scripts/build.py
```

But you no longer need it for production. The build runs in CI on every push.

The auto-build action lives at `.github/workflows/build.yml`. If it fails, the Actions tab on GitHub shows the log.

## Why this can't break what's already running

Three independent layers:

| Layer | Existing | New |
|---|---|---|
| Cloudflare resource | Worker named `planetai` | Pages project named `planetai-coordination` |
| DNS record | `planetai.fab.city` (CNAME or A → existing Worker route) | `coord.planetai.fab.city` (CNAME → Pages) |
| Repo | `fabcity/planetai_publish` | `fabcity/planetai-coordination` |

The only zone-level setting that could in principle affect both is **Page Rules** or **Bulk Redirects** on `fab.city`. If you don't already have ones that match `coord.planetai.*`, no impact. Worth a 30-second check at zone settings before Step 3 if you're unsure.

## Notes

- The `CNAME` file at the repo root (`coord.planetai.fab.city`) is a GitHub Pages convention. For Cloudflare Pages it's harmless — Pages reads the custom domain from its own dashboard, not from the file.
- If you ever want a preview deploy, push to a branch other than `main`. Pages builds it at a unique URL and doesn't replace production.

## What to do next, in order of leverage

1. **Open the four pending reviews** (PITO/DIDO cell-weights, hub architecture, hyperlocal dashboard IA Stage 1, Bali three-source reframe) as YAML files under `reviews/` and notify the named reviewers — closes the most consequential coordination loops first.
2. **Backfill waves 7→28+** from the auto-memory wave files. Each one already has a memory file; reading them in and emitting YAML is a one-evening data-entry job.
3. **Fill out the seven tracks** with concrete one-hour / one-day / one-week entry points, then send the first weekly digest to a two-person test list (Lucas Marangoni + Guillem Camprodon recommended).
4. **Open the four pilot pages** as collaborative drafts — one YAML per pilot, partners fill in `network_committed` vs `pilot_specific`, named contacts, MoU state.

Total: roughly 9 working days of focused effort to a first usable, partner-shareable version.
