# Next steps to ship the coordination dashboard

This repo is a working local skeleton. To make it real, three things need to happen — none of them code-side.

## 1. Push to GitHub

Create the GitHub repo (proposed name: `fabcity/planetai-coordination`), then from inside this folder:

```bash
git init -b main
git add .
git commit -m "scaffold: planetai-coordination v0.1 — repo skeleton + 8 seed decisions"

# create the GitHub repo via gh CLI (or via web UI then add the remote)
gh repo create fabcity/planetai-coordination --public \
  --description "Coordination layer for PLANETAI — decision log, reviews, tracks, pilots, waves." \
  --source=. --remote=origin --push

# if doing it without gh:
# git remote add origin git@github.com:fabcity/planetai-coordination.git
# git push -u origin main
```

The `fabcity` GitHub org already houses `planetai_publish` and `awesome-fabcity-data`, so this is a natural sibling.

## 2. Stand up the Cloudflare Worker

Mirror the pattern in `planetai_publish/wrangler.toml` but without the basic-auth gate (this dashboard should be openly readable). One option:

```toml
# planetai-coordination/wrangler.toml
name = "planetai-coordination"
main = "src/index.js"          # only needed if you want a Worker shim;
                                # otherwise use Cloudflare Pages directly
compatibility_date = "2025-01-15"

[assets]
directory = "./"
binding = "ASSETS"
not_found_handling = "404-page"
```

If you don't need any auth or rewrite logic at all, **Cloudflare Pages** is even simpler than a Worker — connect the GitHub repo, point it at the repo root, set the build command to `python3 scripts/build.py` (or skip the build and let it serve the committed HTML). For now the build is fast enough to commit the generated HTML and skip the build step in CI.

```bash
# install wrangler if needed
npm install -g wrangler

# inside planetai-coordination/
wrangler login
wrangler deploy
```

## 3. Point DNS at the Worker

In Cloudflare DNS for `fab.city`:

- Add a CNAME record: `coord.planetai` → the Worker / Pages URL
- TLS will be issued automatically by Cloudflare

Once DNS propagates, the dashboard lives at **https://coord.planetai.fab.city**.

The `CNAME` file at the repo root (`coord.planetai.fab.city`) is GitHub Pages convention — harmless if you go Worker/Pages instead, useful as a marker either way.

## After deploy

Run the build script after every YAML edit:

```bash
python3 scripts/build.py
git add decisions/ reviews/ tracks/ pilots/ waves/ canonical/ people/
git commit -m "rebuild: <what changed>"
git push
```

Cloudflare auto-deploys on push.

## What to do next, in order of leverage

1. **Open the four pending reviews** (PITO/DIDO cell-weights, applicant-org pivot, hub architecture, hyperlocal dashboard IA Stage 1) as YAML files under `reviews/` and notify the named reviewers — that closes the most consequential coordination loops first.
2. **Backfill waves 7→28+** from the auto-memory wave files. Each one already has a memory file; reading them in and emitting YAML is a one-evening data-entry job.
3. **Fill out the seven tracks** with concrete one-hour / one-day / one-week entry points, then send the first weekly digest to a two-person test list (Lucas Marangoni + Guillem Camprodon recommended).
4. **Open the four pilot pages** as collaborative drafts — one YAML per pilot, partners fill in `network_committed` vs `pilot_specific`, named contacts, MoU state.

Total: roughly 9 working days of focused effort to a first usable, partner-shareable version.
