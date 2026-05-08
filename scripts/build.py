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
from urllib.parse import quote_plus

try:
    import yaml
except ImportError:
    sys.exit("Missing dependency: pip install pyyaml")

try:
    import markdown as md_lib
except ImportError:
    sys.exit("Missing dependency: pip install markdown")


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
      <a href="{root}pilots/index.html" class="{pilots_active}">Pilots</a>
      <a href="{root}previews/index.html" class="{previews_active}">WIP</a>
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
        pilots_active="is-active" if active == "pilots" else "",
        previews_active="is-active" if active == "previews" else "",
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
# pilot pages
# ---------------------------------------------------------------------------

# Section list. Every pilot page is structured around these five H2-bound
# sections. Slug → display label.
PILOT_SECTIONS = [
    ("overview",              "Overview"),
    ("whats-running",         "What's running"),
    ("data-access",           "Data access"),
    ("open-questions",        "Open questions"),
    ("proposed-pilot-scope",  "Proposed pilot scope"),
]
PILOT_SECTION_BY_LABEL = {label: slug for slug, label in PILOT_SECTIONS}


def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def split_markdown_into_sections(md_text: str) -> dict[str, str]:
    """Split a markdown body on H2 boundaries.

    Returns a dict keyed by section slug. Anything before the first H2
    is dropped (treat the page-level H1 as separate metadata).
    """
    parts: dict[str, str] = {}
    current_label: str | None = None
    buf: list[str] = []
    for line in md_text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            if current_label is not None:
                parts[slugify(current_label)] = "\n".join(buf).strip()
            current_label = m.group(1).strip()
            buf = []
        else:
            if current_label is not None:
                buf.append(line)
    if current_label is not None:
        parts[slugify(current_label)] = "\n".join(buf).strip()
    return parts


def render_validators(validated_by: list[dict] | None) -> str:
    if not validated_by:
        return ""
    bits = []
    for v in validated_by:
        name = esc(v.get("name", ""))
        org = v.get("org")
        date = v.get("date")
        scope = v.get("scope")
        s = f"<strong>{name}</strong>"
        if org: s += f" ({esc(org)})"
        if date: s += f" &middot; {esc(date)}"
        if scope: s += f" &middot; <em>{esc(scope)}</em>"
        bits.append(s)
    return "Validated by " + "; ".join(bits)


def section_action_links(*, pilot_slug: str, pilot_display: str,
                         section_slug: str, section_label: str) -> str:
    """Render the three action links per section.

    - Validate this section (opens validate-pilot-section issue form,
      pre-filled with pilot + section)
    - Suggest changes (opens GitHub web editor on the markdown source)
    - Add a comment (opens blank issue with pre-filled title)
    """
    p = quote_plus(pilot_display)
    s = quote_plus(section_label)
    validate_url = (
        f"{REPO_URL}/issues/new?template=validate-pilot-section.yml"
        f"&pilot={p}&section={s}"
    )
    edit_url = f"{REPO_URL}/edit/{DEFAULT_BRANCH}/pilots/{pilot_slug}.md"
    title = quote_plus(f"[{pilot_display} / {section_label}] ")
    comment_url = f"{REPO_URL}/issues/new?title={title}&labels=pilot-comment"
    return (
        f'<div class="pilot-section__actions">'
        f'<a class="primary" href="{validate_url}">Validate this section</a>'
        f'<a href="{edit_url}">Suggest changes</a>'
        f'<a href="{comment_url}">Add a comment</a>'
        f'</div>'
    )


def render_pilot_page(slug: str, md_text: str, sidecar: dict) -> str:
    sections_md = split_markdown_into_sections(md_text)

    display = sidecar.get("display_name") or slug.title()
    status = sidecar.get("status", "")
    host_state = sidecar.get("host_state", "")
    tz = sidecar.get("time_zone", "")

    body_parts: list[str] = []
    body_parts.append(
        f'<a href="index.html" class="mono" style="font-size:11px;'
        f'letter-spacing:0.06em;text-transform:uppercase;color:var(--ink-muted);'
        f'border-bottom:none;">&larr; all pilots</a>'
    )

    eyebrow = f'PILOT &middot; {esc(status)}' if status else 'PILOT'
    body_parts.append(
        f'<div class="decision__eyebrow">{eyebrow}</div>'
    )
    body_parts.append(f'<h1>{esc(display)}</h1>')

    # meta
    meta_rows = []
    if host_state:
        meta_rows.append(f"<dt>Host state</dt><dd>{esc(host_state)}</dd>")
    if tz:
        meta_rows.append(f"<dt>Time zone</dt><dd>{esc(tz)}</dd>")
    contacts = sidecar.get("contacts") or {}
    contact_lines = []
    for role, payload in contacts.items():
        if not payload: continue
        if isinstance(payload, dict):
            name = payload.get("name")
            if not name:
                # fall back to status, humanised
                name = (payload.get("status") or "").replace("_", " ")
            note = payload.get("role")
            line = f"<strong>{esc(role.replace('_', ' ').title())}</strong>: {esc(name)}"
            if note: line += f" &middot; <em>{esc(note)}</em>"
            contact_lines.append(line)
    if contact_lines:
        meta_rows.append(
            f"<dt>Contacts</dt><dd>{'<br>'.join(contact_lines)}</dd>"
        )
    if meta_rows:
        body_parts.append(
            f'<dl class="pilot-meta">{"".join(meta_rows)}</dl>'
        )

    # validation summary
    validation = sidecar.get("validation") or {}
    section_states = validation.get("sections") or {}
    last_full = validation.get("last_full_review")

    rows = []
    counts = {"validated": 0, "pending": 0, "contested": 0, "open": 0}
    for sec_slug, sec_label in PILOT_SECTIONS:
        st = (section_states.get(sec_slug) or {}).get("status", "pending")
        counts[st] = counts.get(st, 0) + 1
        n_validators = len((section_states.get(sec_slug) or {}).get("validated_by") or [])
        rows.append(
            f"<tr><td>{esc(sec_label)}</td>"
            f'<td><span class="section-status" data-status="{esc(st)}">{esc(st)}</span></td>'
            f"<td>{n_validators}</td></tr>"
        )
    summary_lead = (
        f"{counts.get('validated', 0)} of {len(PILOT_SECTIONS)} sections validated"
    )
    if last_full:
        summary_lead += f" &middot; last full review {esc(last_full)}"
    body_parts.append(f"""
<div class="validation-summary">
  <p style="margin-top:0"><strong>{summary_lead}.</strong>
     This page is a partner-validation surface — every section can be
     validated, contributed to, reviewed, or revised. See the action
     links beside each section.</p>
  <table>
    <tr><th>Section</th><th>Status</th><th>Validators</th></tr>
    {"".join(rows)}
  </table>
</div>
""")

    # network vs pilot-specific (if present)
    nvp = sidecar.get("network_vs_pilot") or {}
    if nvp:
        nc = nvp.get("network_committed") or []
        ps = nvp.get("pilot_specific") or []
        if nc or ps:
            cols = []
            if nc:
                items = "".join(f"<li>{esc(x)}</li>" for x in nc)
                cols.append(
                    f'<div><h3 style="font-family:var(--font-mono);'
                    f'font-size:11px;letter-spacing:0.05em;'
                    f'text-transform:uppercase;color:var(--fc-blue);">'
                    f'Network-committed</h3><ul style="padding-left:18px;">'
                    f'{items}</ul></div>'
                )
            if ps:
                items = "".join(f"<li>{esc(x)}</li>" for x in ps)
                cols.append(
                    f'<div><h3 style="font-family:var(--font-mono);'
                    f'font-size:11px;letter-spacing:0.05em;'
                    f'text-transform:uppercase;color:var(--fc-blue);">'
                    f'Pilot-specific</h3><ul style="padding-left:18px;">'
                    f'{items}</ul></div>'
                )
            body_parts.append(
                f'<div style="display:grid;grid-template-columns:'
                f'repeat(auto-fit,minmax(280px,1fr));gap:24px;'
                f'margin:24px 0 32px;">{"".join(cols)}</div>'
            )

    # body sections from markdown
    md_renderer = md_lib.Markdown(extensions=["extra", "sane_lists"])
    for sec_slug, sec_label in PILOT_SECTIONS:
        body_md = sections_md.get(sec_slug, "")
        sec_state = section_states.get(sec_slug) or {}
        st = sec_state.get("status", "pending")
        validators_html = render_validators(sec_state.get("validated_by"))
        rendered_body = md_renderer.convert(body_md) if body_md else (
            '<p style="color:var(--ink-muted);"><em>No content yet for this '
            'section. Use <strong>Suggest changes</strong> to add the first '
            'draft.</em></p>'
        )
        md_renderer.reset()
        body_parts.append(f"""
<section class="pilot-section" id="{esc(sec_slug)}">
  <div class="pilot-section__head">
    <h2>{esc(sec_label)}</h2>
    <span class="section-status" data-status="{esc(st)}">{esc(st)}</span>
  </div>
  <div class="pilot-section__body">{rendered_body}</div>
  {f'<div class="pilot-section__validators">{validators_html}</div>' if validators_html else ''}
  {section_action_links(pilot_slug=slug, pilot_display=display,
                         section_slug=sec_slug, section_label=sec_label)}
</section>
""")

    # open asks (if present)
    open_asks = sidecar.get("open_asks") or []
    if open_asks:
        items = []
        for a in open_asks:
            if isinstance(a, dict):
                summary = esc(a.get("id") or "")
                rest = []
                if a.get("asks_of"): rest.append(f"asks: {esc(a['asks_of'])}")
                if a.get("by"): rest.append(f"by {esc(a['by'])}")
                if a.get("status"): rest.append(esc(a['status']))
                line = f"<strong>{summary}</strong>"
                if rest: line += " &middot; " + " &middot; ".join(rest)
            else:
                line = esc(a)
            items.append(f"<li>{line}</li>")
        body_parts.append(
            f'<h2>Open asks</h2><ul class="artifacts-list">{"".join(items)}</ul>'
        )

    # edit-on-github
    body_parts.append(edit_link(f"pilots/{slug}.md",
                                label="Edit pilot description on GitHub"))
    body_parts.append(CONTRIBUTE_FOOTER)

    return render_layout(
        title=display,
        body="\n".join(body_parts),
        root="../",
        active="pilots",
    )


def render_pilots_index(pilots: list[tuple[str, dict]]) -> str:
    cards = []
    for slug, sidecar in pilots:
        display = sidecar.get("display_name") or slug.title()
        status = sidecar.get("status", "")
        host_state = sidecar.get("host_state", "")
        validation = sidecar.get("validation") or {}
        section_states = validation.get("sections") or {}
        validated = sum(
            1 for s in PILOT_SECTIONS
            if (section_states.get(s[0]) or {}).get("status") == "validated"
        )
        cards.append(f"""
<div class="pilot-card">
  <div class="name"><a href="{esc(slug)}.html">{esc(display)}</a></div>
  <div class="meta">{esc(status)} &middot; {esc(host_state)}</div>
  <div class="progress">
    <span class="section-status" data-status="{'validated' if validated == len(PILOT_SECTIONS) else 'pending'}">
      {validated} / {len(PILOT_SECTIONS)} sections validated
    </span>
  </div>
</div>""")
    body = f"""
<a href="../index.html" class="mono" style="font-size:11px;
letter-spacing:0.06em;text-transform:uppercase;color:var(--ink-muted);
border-bottom:none;">&larr; home</a>
<h1>Pilots</h1>
<p>Four bioregional pilots — Barcelona, Boston, Santiago de Chile, Bali.
Each pilot page is a <strong>partner-validation surface</strong>: every
section can be validated, contributed to, reviewed, or revised by anyone
with knowledge to share. The four actions map to four ways partners
already work together.</p>

<p class="mono" style="color:var(--ink-muted);font-size:0.85rem;">
{len(pilots)} of 4 pilot pages drafted &middot; the rest follow once the pattern is validated.</p>

<div class="pilots-index">{"".join(cards)}</div>

{edit_link("pilots/", label="Browse pilots/ on GitHub")}
{CONTRIBUTE_FOOTER}
"""
    return render_layout(
        title="Pilots",
        body=body,
        root="../",
        active="pilots",
    )


def build_pilots() -> int:
    pilots_dir = REPO_ROOT / "pilots"
    if not pilots_dir.exists():
        return 0
    drafted = []
    for md_path in sorted(pilots_dir.glob("*.md")):
        slug = md_path.stem
        yaml_path = pilots_dir / f"{slug}.yaml"
        if not yaml_path.exists():
            print(f"  warning: {md_path.name} has no sidecar yaml; skipping")
            continue
        sidecar = load_yaml(yaml_path)
        md_text = md_path.read_text(encoding="utf-8")
        out = render_pilot_page(slug, md_text, sidecar)
        out_path = pilots_dir / f"{slug}.html"
        out_path.write_text(out, encoding="utf-8")
        drafted.append((slug, sidecar))
        print(f"  wrote {out_path.relative_to(REPO_ROOT)}")
    if drafted:
        idx = pilots_dir / "index.html"
        idx.write_text(render_pilots_index(drafted), encoding="utf-8")
        print(f"  wrote {idx.relative_to(REPO_ROOT)}")
    return len(drafted)


# ---------------------------------------------------------------------------
# previews — work-in-progress prototypes partners can view + give feedback on
# ---------------------------------------------------------------------------

PREVIEW_STATUS_LABELS = {
    "early-sketch":          "early sketch",
    "stage-1-ia":            "stage-1 IA",
    "stage-2-mockup":        "stage-2 mockup",
    "functional-prototype":  "functional prototype",
    "near-ready":            "near-ready",
    "shipped":               "shipped",
}


def render_preview_detail(slug: str, p: dict) -> str:
    display = p.get("display_name") or slug.title()
    status = p.get("status", "")
    status_label = PREVIEW_STATUS_LABELS.get(status, status)
    short = p.get("short_desc", "")
    notes = p.get("notes", "")
    live_url = p.get("live_url")
    source_path = p.get("source_path")
    source_repo = p.get("source_repo", "")
    related_track = p.get("related_track")
    related_decisions = p.get("related_decisions") or []

    body_parts: list[str] = []
    body_parts.append(
        '<a href="index.html" class="mono" style="font-size:11px;'
        'letter-spacing:0.06em;text-transform:uppercase;color:var(--ink-muted);'
        'border-bottom:none;">&larr; all WIP</a>'
    )
    body_parts.append(
        f'<div class="decision__eyebrow">WORK IN PROGRESS &middot; '
        f'<span class="section-status" data-status="open">{esc(status_label)}</span></div>'
    )
    body_parts.append(f'<h1>{esc(display)}</h1>')

    if short:
        body_parts.append(f'<p class="framing__lead">{paragraphs(short)[3:-4]}</p>')

    # Live + source CTAs
    cta_links = []
    if live_url:
        cta_links.append(
            f'<a class="primary" href="{esc(live_url)}" target="_blank" rel="noopener">Open in new tab &rarr;</a>'
        )
    if source_path and source_repo:
        src_url = f"https://github.com/fabcity/{source_repo}/blob/main/{source_path}"
        cta_links.append(f'<a href="{esc(src_url)}" target="_blank" rel="noopener">Source on GitHub</a>')
    if cta_links:
        body_parts.append(
            f'<div class="pilot-section__actions" style="margin:16px 0 24px;">'
            f'{"".join(cta_links)}</div>'
        )

    # Inline live embed (iframe) — partners see the actual mockup,
    # not just a description. Falls back to a "preview not yet
    # deployed" notice if the URL 404s.
    if live_url:
        body_parts.append(
            f'<div class="preview-embed">'
            f'<div class="preview-embed__bar mono">'
            f'<span>LIVE EMBED</span>'
            f'<span class="preview-embed__url">{esc(live_url)}</span>'
            f'</div>'
            f'<iframe class="preview-embed__frame" src="{esc(live_url)}" '
            f'title="{esc(display)} — live preview" '
            f'loading="lazy" '
            f'sandbox="allow-scripts allow-same-origin allow-popups allow-forms" '
            f'referrerpolicy="no-referrer-when-downgrade">'
            f'</iframe>'
            f'<p class="preview-embed__fallback mono">'
            f'If the embed is blank, the preview has not yet been '
            f'deployed to <a href="{esc(live_url)}" target="_blank" rel="noopener">{esc(live_url)}</a>. '
            f'<a href="https://github.com/fabcity/planetai-coordination/issues/new?title=%5BWIP+%2F+{quote_plus(display)}%5D+preview+not+deploying&amp;labels=wip-feedback">Flag it &rarr;</a>'
            f'</p>'
            f'</div>'
        )

    # Meta
    meta_rows = []
    opened = p.get("opened")
    last_updated = p.get("last_updated")
    if opened:
        meta_rows.append(f"<dt>Opened</dt><dd>{esc(opened)}</dd>")
    if last_updated:
        meta_rows.append(f"<dt>Last updated</dt><dd>{esc(last_updated)}</dd>")
    owners = p.get("owners") or {}
    if owners.get("lead"):
        meta_rows.append(f"<dt>Lead</dt><dd>{esc(owners['lead'])}</dd>")
    if owners.get("pilot_anchor"):
        meta_rows.append(f"<dt>Pilot anchor</dt><dd>{esc(owners['pilot_anchor'])}</dd>")
    partners = owners.get("partners_named") or []
    if partners:
        meta_rows.append(
            f"<dt>Partners</dt><dd>{'<br>'.join(esc(x) for x in partners)}</dd>"
        )
    if related_track:
        meta_rows.append(
            f'<dt>Related track</dt><dd><span class="scope-tag">{esc(related_track)}</span></dd>'
        )
    if meta_rows:
        body_parts.append(
            f'<dl class="pilot-meta">{"".join(meta_rows)}</dl>'
        )

    # Asks-of-reviewers
    asks = p.get("asks") or {}
    looking = asks.get("looking_for_feedback_on") or []
    not_ready = asks.get("not_ready_for") or []
    if looking or not_ready:
        cols = []
        if looking:
            items = "".join(f"<li>{esc(x)}</li>" for x in looking)
            cols.append(
                f'<div><h3 style="font-family:var(--font-mono);'
                f'font-size:11px;letter-spacing:0.05em;'
                f'text-transform:uppercase;color:var(--fc-blue);">'
                f'Looking for feedback on</h3><ul style="padding-left:18px;">'
                f'{items}</ul></div>'
            )
        if not_ready:
            items = "".join(f"<li>{esc(x)}</li>" for x in not_ready)
            cols.append(
                f'<div><h3 style="font-family:var(--font-mono);'
                f'font-size:11px;letter-spacing:0.05em;'
                f'text-transform:uppercase;color:var(--status-proposed);">'
                f'Not ready for</h3><ul style="padding-left:18px;">'
                f'{items}</ul></div>'
            )
        body_parts.append(
            f'<div style="display:grid;grid-template-columns:'
            f'repeat(auto-fit,minmax(280px,1fr));gap:24px;'
            f'margin:24px 0 32px;">{"".join(cols)}</div>'
        )

    if notes:
        body_parts.append(
            f'<div class="callout">{paragraphs(notes)}</div>'
        )

    # Feedback action buttons
    title_q = quote_plus(f"[WIP / {display}] ")
    feedback_url = f"{REPO_URL}/issues/new?title={title_q}&labels=wip-feedback"
    body_parts.append(
        f'<div class="pilot-section__actions" style="margin-top:32px;">'
        f'<a class="primary" href="{esc(feedback_url)}">File feedback on this preview</a>'
        + (f'<a href="{esc(live_url)}" target="_blank" rel="noopener">Open preview in new tab &rarr;</a>' if live_url else '')
        + '</div>'
    )

    # Related
    if related_decisions:
        items = "".join(
            f'<li><a href="../decisions/{esc(r)}.html">{esc(r)}</a></li>'
            for r in related_decisions
        )
        body_parts.append(
            f'<div class="section"><h2>Related decisions</h2>'
            f'<ul class="related-list">{items}</ul></div>'
        )

    body_parts.append(edit_link(f"previews/{slug}.yaml",
                                label="Edit this preview entry on GitHub"))
    body_parts.append(CONTRIBUTE_FOOTER)

    return render_layout(
        title=f"WIP — {display}",
        body="\n".join(body_parts),
        root="../",
        active="previews",
    )


def render_previews_index(previews: list[tuple[str, dict]]) -> str:
    cards = []
    # sort: most recently updated first
    previews_sorted = sorted(
        previews,
        key=lambda x: x[1].get("last_updated") or x[1].get("opened") or "",
        reverse=True,
    )
    for slug, p in previews_sorted:
        display = p.get("display_name") or slug.title()
        status = p.get("status", "")
        status_label = PREVIEW_STATUS_LABELS.get(status, status)
        short = p.get("short_desc", "").strip()
        # use only the first paragraph as the card teaser
        teaser = re.split(r"\n\s*\n", short, maxsplit=1)[0] if short else ""
        last_updated = p.get("last_updated") or p.get("opened") or ""
        track = p.get("related_track", "")
        cards.append(f"""
<div class="pilot-card">
  <div class="name"><a href="{esc(slug)}.html">{esc(display)}</a></div>
  <div class="meta">
    <span class="section-status" data-status="open">{esc(status_label)}</span>
    {f' &middot; updated {esc(last_updated)}' if last_updated else ''}
    {f' &middot; track: {esc(track)}' if track else ''}
  </div>
  <div class="progress">{esc(teaser)}</div>
</div>""")

    body = f"""
<a href="../index.html" class="mono" style="font-size:11px;
letter-spacing:0.06em;text-transform:uppercase;color:var(--ink-muted);
border-bottom:none;">&larr; home</a>
<h1>Work in progress</h1>
<p>What's currently being built across the PLANETAI program — prototypes,
mockups, drafts that are not yet shipped but are visible to partners for
review and feedback. Each preview links to the live build, names a status,
and lists what kind of feedback is most useful right now.</p>
<p class="mono" style="color:var(--ink-muted);font-size:0.85rem;">
{len(previews)} active preview{'s' if len(previews) != 1 else ''}.</p>

<div class="pilots-index">{"".join(cards)}</div>

{edit_link("previews/", label="Browse previews/ on GitHub")}
{CONTRIBUTE_FOOTER}
"""
    return render_layout(
        title="Work in progress",
        body=body,
        root="../",
        active="previews",
    )


def build_previews() -> int:
    previews_dir = REPO_ROOT / "previews"
    if not previews_dir.exists():
        return 0
    drafted: list[tuple[str, dict]] = []
    for yaml_path in sorted(previews_dir.glob("*.yaml")):
        slug = yaml_path.stem
        p = load_yaml(yaml_path)
        out = render_preview_detail(slug, p)
        out_path = previews_dir / f"{slug}.html"
        out_path.write_text(out, encoding="utf-8")
        drafted.append((slug, p))
        print(f"  wrote {out_path.relative_to(REPO_ROOT)}")
    if drafted:
        idx = previews_dir / "index.html"
        idx.write_text(render_previews_index(drafted), encoding="utf-8")
        print(f"  wrote {idx.relative_to(REPO_ROOT)}")
    return len(drafted)


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
    ("tracks", "The seven open work-tracks: pilot deep-descriptions, Bali "
               "hyperlocal dashboard, fab lab network activation, Hamburg + CBA "
               "metrics alignment, FAB26 actions, funding scenarios with/without "
               "Google, and other funding opportunities."),
    ("canonical", "One-click index of every canonical PLANETAI artifact (paper, "
                  "observatory, data manifest, schema, methodology notes)."),
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
    n_decisions = build_decisions()
    print()
    print("pilots/")
    n_pilots = build_pilots()
    print()
    print("previews/")
    n_previews = build_previews()
    print()
    print("stubs/")
    build_stubs()
    print()
    print(f"done · {n_decisions} decisions, {n_pilots} pilots, "
          f"{n_previews} previews rendered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
