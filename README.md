# planetai-coordination

> **Superseded, October 2026. Not maintained since May 2026; kept as a record.** Do not open issues or pull requests
> here. Where each part of this site went:
>
> - the programme and its public pages: [planetai.fab.city](https://planetai.fab.city/)
> - decisions, with their reasoning: [`fabcity/planetai-node` docs/decisions/](https://github.com/fabcity/planetai-node/tree/main/docs/decisions)
> - the node, its docs, and how to contribute (with an agent or without): [`fabcity/planetai-node`](https://github.com/fabcity/planetai-node)
> - packs written for one place: [`fabcity/planetai-wild-packs`](https://github.com/fabcity/planetai-wild-packs)
> - data sources and their reviews: [`fabcity/awesome-fabcity-data`](https://github.com/fabcity/awesome-fabcity-data)
>
> The site at coord.planetai.fab.city still serves these pages, each with a notice at the top saying the same.

## What it was

> Coordination layer for the PLANETAI program. The dashboard explains *what we have built*, surfaces the decisions that shaped it, and lists the open work-tracks where partners can plug in.

Lives at **coord.planetai.fab.city**. Deliberately separate from `planetai_publish` so coordination scaffolding doesn't churn underneath the live observatory and paper, and so the coordination layer can keep developing on its own cadence.

## What's here

| Surface | What it is | Source |
| --- | --- | --- |
| `/index.html` | Front door — framing + what changed + what needs you + open tracks | hand-written |
| `/about.html` | Narrative for cold visitors — what is PLANETAI, how we got here | hand-written |
| `/decisions/` | Decision log — every non-trivial PLANETAI decision with reasoning + supersession chain | YAML, generated |
| `/reviews/` | Active review queue + history (sub-agent attribution surfaced) | YAML, generated *(scaffold)* |
| `/waves/` | Evolution timeline — what shipped when and why | YAML, generated *(scaffold)* |
| `/pilots/` | One page per bioregional pilot (Barcelona · Boston · Santiago · Bali) | YAML + markdown, generated *(scaffold)* |
| `/tracks/` | Seven open work-tracks — pilot deep-descriptions, Bali hyperlocal dashboard, fab lab network activation, Hamburg + CBA metrics, FAB26 actions, funding scenarios, other funding | YAML, generated *(scaffold)* |
| `/canonical/` | One-click index of every canonical artifact (paper, observatory, app v18, data manifest) | YAML, generated *(scaffold)* |
| `/people/` | Who is who, roles, time zones, what they review | YAML, generated *(scaffold)* |

## Build

```bash
python3 scripts/build.py
```

Walks every `*.yaml` under `decisions/`, `reviews/`, etc., and writes HTML alongside (e.g. `decisions/2026-05-02_applicant-org-pivot.yaml` → `decisions/2026-05-02_applicant-org-pivot.html`). Also regenerates `decisions/index.html` (and the equivalents for other surfaces).

Dependencies: Python 3.10+ and `PyYAML`. `pip install pyyaml`.

## Contributing

Each piece of state is one YAML file. Schema reference at `scripts/schemas.md` *(to add)*. To add or update an entry, edit the YAML, run the build, commit both YAML and generated HTML.

If you're a partner without GitHub access, email or Slack the change to Tomas / Lucas; they will land it for you.

## Sister repos

- [`planetai_publish`](https://github.com/fabcity/planetai_publish) — the live observatory and core-ideas paper at planetai.fab.city.
- [`awesome-fabcity-data`](https://github.com/fabcity/awesome-fabcity-data) — the network-curated data discovery list.

## Licence

Curation, narrative, and YAML content under [CC-BY-4.0](LICENSE). Build scripts under MIT (`scripts/LICENSE-MIT`).

Maintained by Fab City and the PLANETAI partner network.
