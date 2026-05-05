#!/usr/bin/env python3
"""
Build script for planetai-coordination.

Walks every *.yaml under decisions/, reviews/, waves/, etc. and emits
HTML alongside the YAML. Also regenerates the per-surface index pages.

Dependencies: PyYAML.
    pip install pyyaml

Usage:
    python3 scripts/build.py
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    sys.exit("Missing dependency: pip install pyyaml")


REPO_ROOT = Path(__file__).resolve().parent.parent
NOW = "2026-05-05"  # build stamp; edit when stale
COORD_VERSION = "v0.1"

# GitHub repository this build deploys from. The "Edit on GitHub" links
# point at the source file at this URL. If the repo lives somewhere else,
# update this one constant.
REPO_URL = "https://github.com/fabcity/planetai-coordination"
DEFAULT_BRANCH = "main"


def edit_link(source_path: str, *, label: str = "Edit on GitHub") -> str:
    """Render an 'Edit on GitHub' link for a given source path.

    source_path is repo-relative — e.g. "decisions/foo.yaml" or
    "decisions/" for the directory listing.
    """
    if source_path.endswith("/"):
        href = f"{REPO_URL}/tree/{DEFAULT_BRANCH}/{source_path.rstrip('/')}"
    else:
        href = f"{REPO_URL}/edit/{DEFAULT_BRANCH}/{source_path}"
    return (
        f'<p class="edit-link" style="margin-top:48px;'
        f'font-family:var(--font-mono);font-size:11px;'
        f'letter-spacing:0.05em;color:var(--ink-muted);">'
        f'<a href="{href}" style="color:var(--ink-muted);'
        f'border-bottom:1px dashed var(--rule);">'
        f'{label} &rarr;</a></p>'
    )


CONTRIBUTE_FOOTER = (
    f'<p class="edit-link" style="margin-top:24px;'
    f'font-family:var(--font-mono);font-size:11px;'
    f'letter-spacing:0.05em;color:var(--ink-muted);">'
    f'New here? See <a href="{REPO_URL}/blob/{DEFAULT_BRANCH}/CONTRIBUTING.md" '
    f'style="color:var(--ink-muted);border-bottom:1px dashed var(--rule);">'
    f'how to contribute &rarr;</a></p>'
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def esc(s: Any) -> str:
    """HTML-escape a value, defaulting empty for None."""
    if s is None:
        return ""
    return html.escape(str(s), quote=True)


def paragraphs(text: str | None) -> str:
    """Convert a multi-line string to paragraphs.

    Blank line splits paragraphs. Single newlines preserved as <br>.
    """
    if not text:
        return ""
    text = text.strip()
    paras = re.split(r"\n\s*\n", text)
    out = []
    for p in paras:
        p = esc(p).replace("\n", "<br>")
        out.append(f"<p>{p}</p>")
    return "\n".join(out)


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a mapping")
    return data


# ---------------------------------------------------------------------------
# template
# ---------------------------------------------------------------------------

LAYOUT = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} — PLANETAI Coordination</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Figtree:wght@300;400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500&display=swap">
  <link rel="stylesheet" href="{root}styles.css">
</head>
<body>
<header class="site-header">
  <div class="site-header__inner">
    <a class="lockup" href="{root}index.html" style="border-bottom:none;">
      <span class="lockup__brand">
        <span class="lockup__eyebrow">FAB CITY</span>
        <span class="lockup__title">PLANETAI</span>
      </span>
      <span class="lockup__meta">· Coordination · {version}</span>
    </a>
    <nav class="site-nav" aria-label="primary">
      <a href="{root}index.html" class="{home_active}">Home</a>
      <a href="{root}about.html" class="{about_active}">About</a>
      <a href="{root}decisions/index.html" class="{decisions_active}">Decisions</a>
      <a href="{root}tracks/index.html" class="{tracks_active}">Tracks</a>
      <a href="{root}reviews/index.html" class="{reviews_active}">Reviews</a>
    </nav>
  </div>
</header>
<main>
{body}
</main>
<footer class="site-footer">
  <div class="site-footer__inner">
    <div>
      Coordination layer for PLANETAI · maintained by Fab City and partners
    </div>
    <div>
      <a href="https://planetai.fab.city/">planetai.fab.city</a> ·
      <a href="https://planetai.fab.city/core-ideas-paper.pdf">paper</a> ·
      <a href="https://planetai.fab.city/observatory/">observatory</a>
    </div>
  </div>
</footer>
</body>
</html>
"""


def render_layout(*, title: str, body: str, root: str = "../",
                  active: str = "") -> str:
    return LAYOUT.format(
        title=esc(title),
        body=body,
        root=root,
        version=COORD_VERSION,
        home_active="is-active" if active == "home" else "",
        about_active="is-active" if active == "about" else "",
        decisions_active="is-active" if active == "decisions" else "",
        tracks_active="is-active" if active == "tracks" else "",
        reviews_active="is-active" if active == "reviews" else "",
    )


# ---------------------------------------------------------------------------
# decision-detail rendering
# ---------------------------------------------------------------------------

def render_attribution(items: list[dict]) -> str:
    if not items:
        return ""
    rows = []
    for it in items:
        kind = it.get("kind", "")
        cls = "kind ai" if kind == "ai-subagent" else "kind"
        if kind == "ai-subagent":
            label = f"{esc(it.get('model', 'AI sub-agent'))}"
            sub = []
            if it.get("surface"):
                sub.append(esc(it['surface']))
            if it.get("role"):
                sub.append(esc(it['role']))
            sub_html = " — ".join(sub)
            line = f"<strong>{label}</strong>" + (f" · {sub_html}" if sub_html else "")
        else:
            label = esc(it.get("name", ""))
            sub = esc(it.get("role", ""))
            line = f"<strong>{label}</strong>" + (f" · {sub}" if sub else "")
        rows.append(
            f'<div class="item"><span class="{cls}">{esc(kind) or "—"}</span>'
            f'<span>{line}</span></div>'
        )
    return f'<div class="attribution-block">{"".join(rows)}</div>'


def render_review_block(review: dict | None) -> str:
    if not review:
        return ""
    parts = []
    required = review.get("required_acks") or []
    received = review.get("acks_received") or []
    closes = review.get("closes")
    note = review.get("note")
    if required:
        ratio = f"{len(received)}/{len(required)} acks"
        items = ", ".join(esc(r) for r in required)
        parts.append(f"<p><strong>Required acks ({ratio}):</strong> {items}</p>")
    if closes:
        parts.append(f"<p><strong>Window closes:</strong> {esc(closes)}</p>")
    if note:
        parts.append(paragraphs(note))
    if not parts:
        return ""
    return f'<div class="callout">{"".join(parts)}</div>'


def render_decision_detail(d: dict, slug: str) -> str:
    status = d.get("status", "")
    scope = d.get("scope", "")
    eyebrow = (
        f'DECISION · {esc(d.get("date", ""))}'
        f' · <span class="pill" data-status="{esc(status)}">{esc(status)}</span>'
    )

    body_parts = [
        f'<a href="index.html" class="mono" style="font-size:11px;'
        f'letter-spacing:0.06em;text-transform:uppercase;color:var(--ink-muted);'
        f'border-bottom:none;">&larr; all decisions</a>',
        f'<div class="decision__eyebrow">{eyebrow}</div>',
        f'<h1>{esc(d.get("title", ""))}</h1>',
    ]

    # meta block
    meta_rows = []
    if scope:
        meta_rows.append(
            f'<dt>Scope</dt><dd><span class="scope-tag">{esc(scope)}</span></dd>'
        )
    authors = d.get("authors") or []
    if authors:
        meta_rows.append(
            f'<dt>Authors</dt><dd>{", ".join(esc(a) for a in authors)}</dd>'
        )
    sup_by = d.get("superseded_by")
    if sup_by:
        meta_rows.append(
            f'<dt>Superseded by</dt><dd><a href="{esc(sup_by)}.html">'
            f'{esc(sup_by)}</a></dd>'
        )
    sup = d.get("supersedes") or []
    if sup:
        links = ", ".join(
            f'<a href="{esc(x)}.html">{esc(x)}</a>' for x in sup
        )
        meta_rows.append(f'<dt>Supersedes</dt><dd>{links}</dd>')
    if meta_rows:
        body_parts.append(
            f'<dl class="decision__meta">{"".join(meta_rows)}</dl>'
        )

    # attribution
    attr = d.get("attribution") or []
    if attr:
        body_parts.append('<div class="section"><h2>Attribution</h2>')
        body_parts.append(render_attribution(attr))
        body_parts.append('</div>')

    # narrative sections
    for key, label in [
        ("prior_state", "Prior state"),
        ("change", "Change"),
        ("reasoning", "Reasoning"),
    ]:
        text = d.get(key)
        if text:
            body_parts.append(
                f'<div class="section"><h2>{label}</h2>{paragraphs(text)}</div>'
            )

    # artifacts changed
    artifacts = d.get("artifacts_changed") or []
    if artifacts:
        items = "".join(f"<li>{esc(a)}</li>" for a in artifacts)
        body_parts.append(
            f'<div class="section"><h2>Artifacts changed</h2>'
            f'<ul class="artifacts-list">{items}</ul></div>'
        )

    # gating questions
    gating = d.get("gating_questions") or []
    if gating:
        items = "".join(f"<li>{esc(g)}</li>" for g in gating)
        body_parts.append(
            f'<div class="section"><h2>Gating questions</h2>'
            f'<ul class="artifacts-list">{items}</ul></div>'
        )

    # review
    review_html = render_review_block(d.get("review"))
    if review_html:
        body_parts.append('<div class="section"><h2>Review</h2>')
        body_parts.append(review_html)
        body_parts.append('</div>')

    # related
    related = d.get("related_decisions") or []
    if related:
        items = "".join(
            f'<li><a href="{esc(r)}.html">{esc(r)}</a></li>' for r in related
        )
        body_parts.append(
            f'<div class="section"><h2>Related decisions</h2>'
            f'<ul class="related-list">{items}</ul></div>'
        )

    # edit-on-github
    body_parts.append(edit_link(f"decisions/{slug}.yaml",
                                label="Edit this decision on GitHub"))
    body_parts.append(CONTRIBUTE_FOOTER)

    return render_layout(
        title=d.get("title", slug),
        body="\n".join(body_parts),
        root="../",
        active="decisions",
    )


# ---------------------------------------------------------------------------
# decision-list rendering
# ---------------------------------------------------------------------------

def render_decisions_index(decisions: list[dict]) -> str:
    decisions_sorted = sorted(
        decisions, key=lambda d: d.get("date", ""), reverse=True
    )

    rows = []
    for d in decisions_sorted:
        slug = d["id"]
        date = d.get("date", "")
        status = d.get("status", "")
        scope = d.get("scope", "")
        title = d.get("title", "")
        rows.append(f"""
<li>
  <span class="date">{esc(date)}</span>
  <div>
    <div class="title"><a href="{esc(slug)}.html">{esc(title)}</a></div>
    <div class="scope">{esc(scope)}</div>
  </div>
  <span class="pill" data-status="{esc(status)}">{esc(status)}</span>
</li>""")

    body = f"""
<a href="../index.html" class="mono" style="font-size:11px;
letter-spacing:0.06em;text-transform:uppercase;color:var(--ink-muted);
border-bottom:none;">&larr; home</a>
<h1>Decision log</h1>
<p>Every non-trivial PLANETAI decision is a first-class object: prior state,
change, who pushed for it, reasoning, what it supersedes. A partner reading
this a week later should know not just <em>what</em> is true but <em>why</em>.</p>
<p class="mono" style="color:var(--ink-muted);font-size:0.85rem;">
{len(decisions_sorted)} entries · seeded {NOW}</p>
<ul class="decision-list">{"".join(rows)}</ul>
{edit_link("decisions/", label="Browse decisions on GitHub")}
{CONTRIBUTE_FOOTER}
"""
    return render_layout(
        title="Decisions",
        body=body,
        root="../",
        active="decisions",
    )


# ---------------------------------------------------------------------------
# stub-index rendering for empty surfaces
# ---------------------------------------------------------------------------

def render_stub_index(*, surface: str, blurb: str) -> str:
    body = f"""
<a href="../index.html" class="mono" style="font-size:11px;
letter-spacing:0.06em;text-transform:uppercase;color:var(--ink-muted);
border-bottom:none;">&larr; home</a>
<h1>{esc(surface.title())}</h1>
<p>{esc(blurb)}</p>
<div class="callout"><strong>Scaffold only.</strong> No entries yet.
This surface ships with the dashboard but is intentionally empty at v0.1.
Content lands in coming sessions.</div>
{edit_link(f"{surface}/", label=f"Browse {surface}/ on GitHub")}
{CONTRIBUTE_FOOTER}
"""
    return render_layout(
        title=surface.title(),
        body=body,
        root="../",
        active=surface,
    )


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def build_decisions() -> int:
    decisions_dir = REPO_ROOT / "decisions"
    if not decisions_dir.exists():
        return 0
    decisions = []
    for yaml_path in sorted(decisions_dir.glob("*.yaml")):
        d = load_yaml(yaml_path)
        slug = d.get("id") or yaml_path.stem
        if d.get("id") != yaml_path.stem:
            print(f"  warning: id mismatch in {yaml_path.name}")
        html_out = render_decision_detail(d, slug)
        out_path = decisions_dir / f"{slug}.html"
        out_path.write_text(html_out, encoding="utf-8")
        decisions.append(d)
        print(f"  wrote {out_path.relative_to(REPO_ROOT)}")
    if decisions:
        idx = decisions_dir / "index.html"
        idx.write_text(render_decisions_index(decisions), encoding="utf-8")
        print(f"  wrote {idx.relative_to(REPO_ROOT)}")
    return len(decisions)


STUB_SURFACES = [
    ("reviews", "Active review queue plus history. Each item names the artifact, "
                "required and optional reviewers, the AI sub-agent's review (with "
                "delta-to-human flagged), and the closing window."),
    ("waves", "Evolution timeline. One card per ship event with reasoning — "
              "what changed, why, and how it shaped what came next."),
    ("pilots", "One page per bioregional pilot — Barcelona, Boston, Santiago, "
               "Bali. Distinguishes network-committed from pilot-specific."),
    ("tracks", "The seven open work-tracks: pilot deep-descriptions, Bali "
               "hyperlocal dashboard, fab lab network activation, Hamburg + CBA "
               "metrics alignment, FAB26 actions, funding scenarios with/without "
               "Google, and other funding opportunities."),
    ("canonical", "One-click index of every canonical PLANETAI artifact (paper, "
                  "observatory, application v18, data manifest, schema)."),
    ("people", "Who is who, time zones, what they review, preferred ack format."),
]


def build_stubs() -> None:
    for surface, blurb in STUB_SURFACES:
        d = REPO_ROOT / surface
        d.mkdir(exist_ok=True)
        (d / ".gitkeep").touch()
        (d / "index.html").write_text(
            render_stub_index(surface=surface, blurb=blurb),
            encoding="utf-8",
        )
        print(f"  wrote {(d / 'index.html').relative_to(REPO_ROOT)}")


def main() -> int:
    print("planetai-coordination · build")
    print(f"  repo: {REPO_ROOT}")
    print()
    print("decisions/")
    n = build_decisions()
    print()
    print("stubs/")
    build_stubs()
    print()
    print(f"done · {n} decisions rendered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
