#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import os
import re
import shutil
from collections import Counter
from pathlib import Path
from urllib.parse import quote

from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
SITE_BASE = os.environ.get("SITE_BASE", "").strip().rstrip("/")
SITE_URL = os.environ.get("SITE_URL", "https://gdpeterson.github.io/garrypeterson.github.io").strip().rstrip("/")


def with_site_base(rendered: str) -> str:
    if not SITE_BASE:
        return rendered
    return re.sub(r'(?P<attr>href|src)="/', rf'\g<attr>="{SITE_BASE}/', rendered)


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    text = html.unescape(value)
    replacements = {
        r"\\mathsemicolon": ";",
        "{": "",
        "}": "",
        "\\&": "&",
        "\\_": "_",
        "~": " ",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"\\[a-zA-Z]+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def year_of(pub: dict) -> int | None:
    try:
        return int(pub.get("issued", {}).get("date-parts", [[None]])[0][0])
    except (TypeError, ValueError, IndexError):
        return None


def author_name(author: dict) -> str:
    literal = clean_text(author.get("literal"))
    if literal:
        return literal
    given = clean_text(author.get("given"))
    family = clean_text(author.get("family"))
    return " ".join(x for x in (given, family) if x)


def classify(title: str) -> list[str]:
    t = title.lower()
    tags = []
    rules = [
        ("Biodiversity finance", ["finance", "financial", "corporate biodiversity", "nature-positive"]),
        ("Scenarios & futures", ["scenario", "future", "foresight", "anthropocene", "visioning"]),
        ("Resilience & regime shifts", ["resilien", "regime shift", "threshold", "alternate stable"]),
        ("Ecosystem services", ["ecosystem service", "human well-being", "human wellbeing"]),
        ("Social-ecological systems", ["social-ecological", "sustainability", "transformation", "governance"]),
    ]
    for tag, needles in rules:
        if any(n in t for n in needles):
            tags.append(tag)
    return tags[:3] or ["Social-ecological systems"]


def publication_url(pub: dict) -> str:
    doi = clean_text(pub.get("DOI"))
    if doi:
        return f"https://doi.org/{doi}"
    return clean_text(pub.get("URL"))


def normalize_publications(raw: list[dict]) -> list[dict]:
    normalized = []
    seen = set()
    for pub in raw:
        title = clean_text(pub.get("title"))
        if not title:
            continue
        year = year_of(pub)
        authors = [author_name(a) for a in pub.get("author", [])]
        venue = clean_text(pub.get("container-title") or pub.get("publisher") or pub.get("genre"))
        key = (title.lower(), year, venue.lower())
        if key in seen:
            continue
        seen.add(key)
        normalized.append({
            "id": clean_text(pub.get("id")) or f"pub-{len(normalized)+1}",
            "title": title,
            "year": year,
            "authors": authors,
            "authors_display": ", ".join(authors),
            "venue": venue,
            "volume": clean_text(pub.get("volume")),
            "issue": clean_text(pub.get("issue")),
            "pages": clean_text(pub.get("page")),
            "doi": clean_text(pub.get("DOI")),
            "url": publication_url(pub),
            "type": clean_text(pub.get("type")).replace("article-journal", "Journal article").replace("chapter", "Book chapter").replace("book", "Book").replace("report", "Report").replace("paper-conference", "Conference paper").replace("dataset", "Dataset").title(),
            "tags": classify(title),
        })
    return sorted(normalized, key=lambda p: (p["year"] or 0, p["title"].lower()), reverse=True)


def selected_publications(publications: list[dict]) -> list[dict]:
    desired = [
        "nature finance futures",
        "cascading regime shifts within and across scales",
        "bright spots: seeds of a good anthropocene",
        "regime shifts in the anthropocene",
        "reconnecting to the biosphere",
        "ecosystem service bundles for analyzing tradeoffs",
        "scenario planning: a tool for conservation",
    ]
    found = []
    for needle in desired:
        for pub in publications:
            if needle in pub["title"].lower() and pub not in found:
                found.append(pub)
                break
    return found[:6]


def build() -> None:
    profile = json.loads((ROOT / "content/profile.json").read_text(encoding="utf-8"))
    raw_publications = json.loads((ROOT / "data/publications-csl.json").read_text(encoding="utf-8"))
    publications = normalize_publications(raw_publications)
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    shutil.copytree(ROOT / "assets", DIST / "assets")
    shutil.copytree(ROOT / "static", DIST, dirs_exist_ok=True)

    env = Environment(
        loader=FileSystemLoader(ROOT / "templates"),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["urlencode"] = lambda value: quote(str(value))

    common = {
        "profile": profile,
        "publication_count": len(publications),
        "year_counts": Counter(p["year"] for p in publications if p["year"]),
        "years": sorted({p["year"] for p in publications if p["year"]}, reverse=True),
    }

    pages = [
        ("index.html", "home.html", {"page_title": profile["name"], "active": "home", "selected_publications": selected_publications(publications)}),
        ("research/index.html", "research.html", {"page_title": "Research", "active": "research", "publications": publications}),
        ("publications/index.html", "publications.html", {"page_title": "Publications", "active": "publications", "publications": publications}),
        ("projects/index.html", "projects.html", {"page_title": "Projects & Data", "active": "projects"}),
        ("talks/index.html", "talks.html", {"page_title": "Talks", "active": "talks"}),
        ("bio/index.html", "bio.html", {"page_title": "About", "active": "bio"}),
        ("contact/index.html", "contact.html", {"page_title": "Contact", "active": "contact"}),
        ("404.html", "404.html", {"page_title": "Page not found", "active": ""}),
    ]
    for output, template, ctx in pages:
        dest = DIST / output
        dest.parent.mkdir(parents=True, exist_ok=True)
        rendered = env.get_template(template).render(**common, **ctx)
        dest.write_text(with_site_base(rendered), encoding="utf-8")

    (DIST / ".nojekyll").write_text("", encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
    sitemap_urls = ["", "research/", "publications/", "projects/", "talks/", "bio/", "contact/"]
    sitemap = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n" + "\n".join(
        f"  <url><loc>{SITE_URL}/{path}</loc></url>" for path in sitemap_urls
    ) + "\n</urlset>\n"
    (DIST / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (DIST / "publications.json").write_text(json.dumps(publications, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Built {len(pages)} pages and {len(publications)} publications into {DIST}")


if __name__ == "__main__":
    build()
