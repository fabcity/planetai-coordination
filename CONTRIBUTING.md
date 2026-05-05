# Contributing to planetai-coordination

This is the coordination layer for the PLANETAI program. Most contributions are short, structured, and asynchronous: a proposed decision, an ack or pushback on an open review, a corrected fact, an updated track status. The goal is to make the project legible to its own contributors and the wider Fab City network.

## Three paths in

Pick the one that fits how you'd rather work.

### 1. Form-based (no YAML, no terminal)

If you'd rather fill a form than touch the underlying file:

- **[Propose a decision](https://github.com/fabcity/planetai-coordination/issues/new?template=propose-decision.yml)** — opens a structured GitHub Issue Form. Fill the fields (title, scope, prior state, change, reasoning, required reviewers). Tomas or Lucas converts your proposal into a YAML file in `decisions/` when triaging. You'll be tagged on the resulting commit.
- **[Ack or push back on a review](https://github.com/fabcity/planetai-coordination/issues/new?template=ack-or-pushback.yml)** — same shape, scoped to open review windows.

A free GitHub account is required (sixty seconds at [github.com/signup](https://github.com/signup)).

### 2. Direct edit (web only)

If you can read YAML and want to land a small change yourself:

- On any decision page, click **"Edit this decision on GitHub"** at the bottom. GitHub's in-browser editor opens. Make your change. Click **"Propose changes"**. GitHub creates a pull request. A maintainer reviews and merges. Auto-build regenerates HTML and Cloudflare Pages redeploys, all without anyone running a terminal.
- Same flow for tracks, pilot pages, the people page — every generated page has the link.

If you have the `fabcity/planetai-coordination` write bit, you can commit directly to `main` instead of opening a PR. The auto-build action will still rebuild HTML.

### 3. Email or Slack a maintainer

If GitHub itself is the wrong fit (a customary authority signing off on a Tri Hita Karana mapping is not going to file a GitHub issue), email **tomas@fab.city** or DM Tomas / Lucas in the FCF Slack. They log the YAML on your behalf and CC you on the resulting PR. This is an honest fallback, not a second-class path — partner-trust work runs at customary cadence, not git cadence.

## What kinds of contributions belong here

This repo is for **coordination state** — decisions, reviews, waves, tracks, pilots, canonical artifact pointers, people. It is *not* for:

- Observatory code or content — that lives in [`planetai_publish`](https://github.com/fabcity/planetai_publish).
- Data sources — those live in [`awesome-fabcity-data`](https://github.com/fabcity/awesome-fabcity-data).
- Internal grant-application bureaucracy — applicant-org changes, submission versions, deadline-day fix-packs. Those are real but they don't belong on a project-coordination dashboard.

If your contribution doesn't fit, consider whether it belongs in one of the sister repos above.

## Decision-log entries — schema

Every decision is a single YAML file at `decisions/{date}_{slug}.yaml`. Required fields: `id`, `title`, `date`, `status`, `scope`, `authors`, `attribution`, `prior_state`, `change`, `reasoning`. See any existing file for the full shape.

`status` is one of `proposed`, `under-review`, `locked`, `superseded`. `scope` is one of `network`, `program`, `pilot:barcelona`, `pilot:boston`, `pilot:santiago`, `pilot:bali`.

Two requirements that aren't optional:

- **Reasoning is load-bearing.** A partner reading your decision a week later should know not just *what* changed but *why*. "Because we needed to" is not a reason. Cite the constraint, the prior incident, the principle, the partner ask — whatever made the change inevitable.
- **Sub-agent attribution is honest.** If an AI sub-agent (Claude, GPT, anything) drafted the entry or surfaced the issue, the `attribution` block must say so, naming the model and its role. See `decisions/2026-05-04_bali-org-correction.yaml` for an example of how to flag a sub-agent retraction.

## Reviews — how acks and pushbacks are recorded

A review YAML lives at `reviews/{id}.yaml` with required reviewers, optional reviewers, the artifact under review, and a closing date. When you ack or push back via the form, the resulting issue is converted into a comment block on the review's YAML by the maintainer. The review's `status` field reflects current state: `pending`, `acked`, `pushed-back`, `closed`.

Default review window is 14 days. No-response is *not* tacit ACK for required reviewers — it escalates to Tomas. For optional reviewers, no-response is recorded and the review proceeds.

## Auto-build

Every push to `main` triggers a GitHub Actions workflow (`.github/workflows/build.yml`) that runs `python3 scripts/build.py` and commits the regenerated HTML back. Cloudflare Pages auto-deploys. You only ever edit YAML; the rest is automatic.

If you want to preview a change locally before opening a PR:

```bash
pip install pyyaml
python3 scripts/build.py
open index.html  # or your file:// equivalent
```

But this is optional — the GitHub web flow does not require it.

## Code of conduct

Be honest, be useful, be brief. The Fab City network operates under [Fab Charter](https://fabfoundation.org/about/) principles and [Contributor Covenant 2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). Issues go to community@fab.city.

## Questions

If anything in this document is unclear, that's a contribution opportunity in itself — open an issue or email tomas@fab.city. Iteration on this guide is welcome.
