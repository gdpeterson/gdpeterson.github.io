"""Publication normalization, curation, and homepage selection.

Machine-managed bibliographic facts come from ``data/publications-csl.json``.
Human-reviewed interpretation lives in ``data/publication-curation.json``.
The two layers are merged here so ORCID updates cannot overwrite editorial tags.
"""
from __future__ import annotations

import hashlib
import os
import random
import re
from typing import Any

from site_utils import clean_text


def normalize_doi(value: Any) -> str:
    """Normalize a DOI or DOI URL to a lowercase bare DOI string."""
    doi = clean_text(value).strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if doi.startswith(prefix):
            doi = doi[len(prefix) :]
    return doi.strip()


def load_doi_list(path) -> list[str]:
    """Read one DOI per line, allowing blank lines and ``#`` comments."""
    if not path.exists():
        return []
    dois: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        value = normalize_doi(line.split("#", 1)[0])
        if value and value not in dois:
            dois.append(value)
    return dois


def year_of(publication: dict[str, Any]) -> int | None:
    try:
        return int(publication.get("issued", {}).get("date-parts", [[None]])[0][0])
    except (TypeError, ValueError, IndexError):
        return None


def author_name(author: dict[str, Any]) -> str:
    literal = clean_text(author.get("literal"))
    return literal or " ".join(
        value
        for value in (
            clean_text(author.get("given")),
            clean_text(author.get("family")),
        )
        if value
    )


def stable_key(publication: dict[str, Any], title: str) -> str:
    doi = normalize_doi(publication.get("DOI"))
    if doi:
        return f"doi:{doi}"
    put_code = clean_text(publication.get("orcid_put_code"))
    if put_code:
        return f"orcid:{put_code}"
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:100]
    return f"local:{slug}"


def suggest_taxonomy(title: str, venue: str = "") -> tuple[list[str], list[str]]:
    """Suggest non-exclusive tags for unreviewed records.

    These rules are deliberately conservative and only create suggestions.
    Curated values in ``publication-curation.json`` always take precedence.
    """
    haystack = f"{title} {venue}".lower()
    theme_rules = {
        "biodiversity-finance": [
            "finance", "financial", "investment", "disclosure", "materiality",
            "accounting", "central bank", "nature-positive economy",
        ],
        "scenarios-futures": [
            "scenario", "future", "foresight", "vision", "anthropocene",
            "anticipat", "pathway", "nature futures",
        ],
        "resilience-regime-shifts": [
            "resilien", "regime shift", "threshold", "alternative stable",
            "adaptive cycle", "panarchy", "tipping", "feedback",
        ],
        "ecosystem-services-biodiversity": [
            "ecosystem service", "nature contribution", "biodiversity",
            "landscape", "pollinat", "biosphere", "natural capital",
            "multifunction",
        ],
        "governance-transformation": [
            "governance", "transform", "stewardship", "institution",
            "collective action", "participat", "policy", "justice",
            "co-production", "learning",
        ],
    }
    themes = [
        theme_id
        for theme_id, needles in theme_rules.items()
        if any(needle in haystack for needle in needles)
    ]
    if not themes:
        themes = [
            "governance-transformation"
            if "social-ecological" in haystack or "sustainab" in haystack
            else "resilience-regime-shifts"
        ]

    questions: list[str] = []
    if any(
        theme in themes
        for theme in (
            "ecosystem-services-biodiversity",
            "biodiversity-finance",
            "governance-transformation",
        )
    ):
        questions.append("people-nature-connections")
    if "resilience-regime-shifts" in themes or any(
        word in haystack for word in ("change", "dynamic", "disturb", "feedback", "threshold")
    ):
        questions.append("social-ecological-change")
    if any(
        theme in themes
        for theme in (
            "scenarios-futures",
            "governance-transformation",
            "biodiversity-finance",
        )
    ):
        questions.append("navigate-shape-futures")
    return themes, list(dict.fromkeys(questions or ["people-nature-connections"]))


def publication_url(publication: dict[str, Any], doi: str = "") -> str:
    resolved = normalize_doi(doi or publication.get("DOI"))
    return f"https://doi.org/{resolved}" if resolved else clean_text(publication.get("URL"))


def normalize_publications(raw, curation, taxonomy):
    """Merge CSL records with the human-curated metadata overlay."""
    normalized: list[dict[str, Any]] = []
    seen: set[Any] = set()
    records = curation.get("records", {})

    for publication in raw:
        title = clean_text(publication.get("title"))
        if not title:
            continue
        year = year_of(publication)
        venue = clean_text(
            publication.get("container-title")
            or publication.get("publisher")
            or publication.get("genre")
        )
        doi = normalize_doi(publication.get("DOI"))
        dedupe_key = doi or (title.lower(), year, venue.lower())
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)

        key = stable_key(publication, title)
        override = records.get(key, {})
        doi = normalize_doi(override.get("doi") or publication.get("DOI"))
        suggested_themes, suggested_questions = suggest_taxonomy(title, venue)
        themes = override.get("themes", suggested_themes)
        questions = override.get("questions", suggested_questions)
        authors = [author_name(author) for author in publication.get("author", [])]

        output_type = clean_text(publication.get("type"))
        type_names = {
            "article-journal": "Journal article",
            "chapter": "Book chapter",
            "book": "Book",
            "report": "Report",
            "paper-conference": "Conference paper",
            "dataset": "Dataset",
        }
        output_type = type_names.get(output_type, output_type.title() or "Other")

        normalized.append(
            {
                "id": key,
                "title": title,
                "year": year,
                "authors": authors,
                "authors_display": ", ".join(authors),
                "venue": venue,
                "volume": clean_text(publication.get("volume")),
                "issue": clean_text(publication.get("issue")),
                "pages": clean_text(publication.get("page")),
                "doi": doi,
                "url": publication_url(publication, doi),
                "type": override.get("output_type", output_type),
                "theme_ids": themes,
                "question_ids": questions,
                "themes": [
                    taxonomy["themes"][theme]["title"]
                    for theme in themes
                    if theme in taxonomy["themes"]
                ],
                "questions": [
                    taxonomy["questions"][question]["short_title"]
                    for question in questions
                    if question in taxonomy["questions"]
                ],
                # Transitional compatibility for older presentation templates.
                "tags": [
                    taxonomy["themes"][theme]["title"]
                    for theme in themes
                    if theme in taxonomy["themes"]
                ],
                "featured": bool(override.get("featured", False)),
                "summary": override.get("summary"),
                "review_status": override.get("review_status", "suggested"),
            }
        )

    return sorted(
        normalized,
        key=lambda publication: (
            publication["year"] or 0,
            publication["title"].lower(),
        ),
        reverse=True,
    )


def eligible_homepage_papers(publications):
    """Exclude datasets, supplementary records, and undated records."""
    excluded_types = {"dataset", "supplementary material"}
    eligible = []
    for publication in publications:
        title = publication["title"].lower()
        output_type = publication["type"].lower()
        if not publication["year"] or output_type in excluded_types:
            continue
        if "supplementary data" in title or "figshare" in publication["url"].lower():
            continue
        eligible.append(publication)
    return eligible


def _random_choice(items, slot):
    """Choose securely, with an optional deterministic seed for tests/previews."""
    if not items:
        return None
    seed = os.environ.get("HOMEPAGE_RANDOM_SEED", "").strip()
    if not seed:
        return random.SystemRandom().choice(items)
    digest = hashlib.sha256(f"{seed}:{slot}".encode("utf-8")).digest()
    return items[int.from_bytes(digest[:8], "big") % len(items)]


def homepage_publications(publications, classic_dois):
    """Build the recent, classic, and latest homepage publication slots."""
    eligible = eligible_homepage_papers(publications)
    latest = eligible[0] if eligible else None
    recent_pool = eligible[1:11]
    recent = _random_choice(recent_pool, "recent")

    by_doi = {
        normalize_doi(publication.get("doi")): publication
        for publication in eligible
        if normalize_doi(publication.get("doi"))
    }
    classic_pool = []
    for doi in classic_dois:
        publication = by_doi.get(normalize_doi(doi))
        if publication and publication not in classic_pool:
            classic_pool.append(publication)
    classic = _random_choice(classic_pool, "classic")

    slots = []
    definitions = [
        (
            "Recent selection",
            "Randomly selected from the ten most recent eligible papers, excluding the latest",
            recent,
        ),
        (
            "Classic selection",
            "Randomly selected from the editable classic DOI list",
            classic,
        ),
        (
            "Most recent",
            "Updated automatically from the ORCID-compatible publication record",
            latest,
        ),
    ]
    for label, note, publication in definitions:
        if publication:
            item = dict(publication)
            item["slot_label"] = label
            item["slot_note"] = note
            slots.append(item)

    if len(classic_dois) != 10:
        print(
            f"Warning: data/classic-dois.txt contains {len(classic_dois)} "
            "unique DOI entries; 10 are recommended."
        )
    unresolved = [doi for doi in classic_dois if normalize_doi(doi) not in by_doi]
    if unresolved:
        print("Warning: classic DOI entries not found: " + ", ".join(unresolved))
    if not classic_pool:
        raise RuntimeError("No classic DOI entries matched publication records.")
    if len(recent_pool) < 10:
        print(f"Warning: only {len(recent_pool)} recent candidates were available.")

    return {
        "cards": slots,
        "recent_candidates": recent_pool,
        "classic_candidates": classic_pool,
    }


def homepage_publication_payload(publication):
    """Return the minimal safe browser-side payload used for random rotation."""
    keys = ("title", "year", "type", "authors_display", "summary", "url")
    return {key: publication.get(key) for key in keys}
