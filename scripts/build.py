#!/usr/bin/env python3
"""Build the Garry Peterson static website into ``dist/``.

The build is intentionally small and modular:

* ``site_utils.py`` handles generic JSON, text, URL, and image helpers.
* ``publications.py`` handles ORCID/CSL normalization and publication choices.
* templates contain presentation only.
* editable content lives in ``content/`` and ``data/``.

Run locally with::

    SITE_BASE="" SITE_URL="https://gdpeterson.github.io" python scripts/build.py
"""
from __future__ import annotations

import json
import os
import shutil
from collections import Counter
from pathlib import Path
from urllib.parse import quote

from jinja2 import Environment, FileSystemLoader, select_autoescape

from publications import (
    homepage_publication_payload,
    homepage_publications,
    load_doi_list,
    normalize_publications,
)
from site_utils import (
    load_json,
    resolve_image,
    validate_image_catalog,
    with_site_base,
)

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
SITE_BASE = os.environ.get("SITE_BASE", "").strip().rstrip("/")
SITE_URL = os.environ.get(
    "SITE_URL", "https://gdpeterson.github.io"
).strip().rstrip("/")


def build_environment(images):
    """Create the Jinja environment and register small presentation helpers."""
    environment = Environment(
        loader=FileSystemLoader(ROOT / "templates"),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    environment.filters["urlencode"] = lambda value: quote(str(value))
    environment.globals["image"] = lambda key: resolve_image(images, key)
    return environment


def copy_static_assets():
    """Create a clean output directory and copy versioned static assets."""
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    shutil.copytree(ROOT / "assets", DIST / "assets")
    shutil.copytree(ROOT / "static", DIST, dirs_exist_ok=True)


def render_pages(environment, common, page_specs):
    """Render all configured pages from declarative output/template/context specs."""
    for output, template, context in page_specs:
        destination = DIST / output
        destination.parent.mkdir(parents=True, exist_ok=True)
        rendered = environment.get_template(template).render(**common, **context)
        destination.write_text(
            with_site_base(rendered, SITE_BASE),
            encoding="utf-8",
        )


def write_machine_readable_outputs(publications, taxonomy):
    """Write discovery, indexing, and open-data files."""
    (DIST / ".nojekyll").write_text("", encoding="utf-8")
    (DIST / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n",
        encoding="utf-8",
    )
    routes = ["", "research/", "publications/", "projects/", "talks/", "bio/", "contact/"]
    sitemap_urls = "\n".join(
        f"  <url><loc>{SITE_URL}/{route}</loc></url>" for route in routes
    )
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{sitemap_urls}\n"
        "</urlset>\n",
        encoding="utf-8",
    )
    (DIST / "publications.json").write_text(
        json.dumps(publications, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (DIST / "taxonomy.json").write_text(
        json.dumps(taxonomy, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def build():
    """Load content, validate it, render pages, and write public data exports."""
    profile = load_json(ROOT / "content/profile.json", {})
    images = load_json(ROOT / "data/images.json", {})
    taxonomy = load_json(ROOT / "data/taxonomy.json", {"questions": {}, "themes": {}})
    curation = load_json(ROOT / "data/publication-curation.json", {"records": {}})
    access = load_json(ROOT / "data/publication-access.json", {"records": {}})
    sync = load_json(ROOT / "data/orcid-sync.json", {})
    raw_publications = load_json(ROOT / "data/publications-csl.json", [])
    classic_dois = load_doi_list(ROOT / "data/classic-dois.txt")

    validate_image_catalog(ROOT, images)
    publications = normalize_publications(raw_publications, curation, taxonomy, access)
    homepage_selection = homepage_publications(publications, classic_dois)

    copy_static_assets()
    environment = build_environment(images)

    theme_counts = Counter(
        theme_id for publication in publications for theme_id in publication["theme_ids"]
    )
    question_counts = Counter(
        question_id
        for publication in publications
        for question_id in publication["question_ids"]
    )
    output_type_counts = Counter(publication["type_slug"] for publication in publications)
    output_type_labels = {
        publication["type_slug"]: publication["type"] for publication in publications
    }
    open_access_count = sum(1 for publication in publications if publication["open_access"])
    homepage_candidate_json = json.dumps(
        {
            "recent": [
                homepage_publication_payload(publication)
                for publication in homepage_selection["recent_candidates"]
            ],
            "classic": [
                homepage_publication_payload(publication)
                for publication in homepage_selection["classic_candidates"]
            ],
        },
        ensure_ascii=False,
    ).replace("</", r"<\/")

    common = {
        "profile": profile,
        "images": images,
        "site_base": SITE_BASE,
        "publication_count": len(publications),
        "year_counts": Counter(
            publication["year"] for publication in publications if publication["year"]
        ),
        "years": sorted(
            {publication["year"] for publication in publications if publication["year"]},
            reverse=True,
        ),
        "taxonomy": taxonomy,
        "theme_counts": theme_counts,
        "question_counts": question_counts,
        "sync": sync,
        "output_type_counts": output_type_counts,
        "output_type_labels": output_type_labels,
        "open_access_count": open_access_count,
    }

    featured_index = profile.get("homepage", {}).get("featured_story_index", 0)
    stories = profile.get("research_stories", [{}])
    featured_story = stories[featured_index] if stories else {}

    page_specs = [
        (
            "index.html",
            "home.html",
            {
                "page_title": profile["name"],
                "active": "home",
                "homepage_publications": homepage_selection["cards"],
                "homepage_publication_data_json": homepage_candidate_json,
                "featured_story": featured_story,
            },
        ),
        (
            "research/index.html",
            "research.html",
            {"page_title": "Research", "active": "research", "publications": publications},
        ),
        (
            "publications/index.html",
            "publications.html",
            {
                "page_title": "Publications",
                "active": "publications",
                "publications": publications,
                "featured_publications": homepage_selection["cards"],
            },
        ),
        ("projects/index.html", "projects.html", {"page_title": "Projects & Data", "active": "projects"}),
        ("talks/index.html", "talks.html", {"page_title": "Talks", "active": "talks"}),
        ("bio/index.html", "bio.html", {"page_title": "About", "active": "bio"}),
        ("contact/index.html", "contact.html", {"page_title": "Contact", "active": "contact"}),
        ("404.html", "404.html", {"page_title": "Page not found", "active": ""}),
    ]

    render_pages(environment, common, page_specs)
    write_machine_readable_outputs(publications, taxonomy)

    print(f"Built {len(page_specs)} pages and {len(publications)} publications into {DIST}")
    for item in homepage_selection["cards"]:
        print(f"Homepage {item['slot_label'].lower()}: {item['title']}")


if __name__ == "__main__":
    build()
