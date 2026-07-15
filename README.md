# Garry Peterson academic website

Source for `https://gdpeterson.github.io/`. The site is a lightweight static
Jinja build with no database or framework runtime. Pushing to `main` triggers a
GitHub Pages deployment.

## Project structure

```text
content/profile.json             Editorial text and structured site content
data/images.json                 Named image catalog used by all templates
data/publications-csl.json       Machine-managed ORCID/CSL bibliography
data/publication-curation.json   Human-reviewed publication interpretation
data/classic-dois.txt            Homepage classic-paper DOI list
data/taxonomy.json               Three questions and five research domains
scripts/build.py                 Build orchestration only
scripts/site_utils.py            Generic JSON, text, URL, and image helpers
scripts/publications.py          Publication normalization and selection
scripts/update_orcid.py          ORCID/Crossref synchronization
assets/css/site.css              Visual design
assets/js/site.js                JavaScript entry point
assets/js/modules/               One module per interactive feature
templates/                       Jinja page templates and shared image macro
static/images/                   Source images copied to the built site
```

## Routine edits

- Text, current work, projects, stories, talks, and external links:
  `content/profile.json`
- Image files and alt text: `static/images/` plus `data/images.json`
- Publication interpretation: `data/publication-curation.json`
- Classic homepage papers: `data/classic-dois.txt`
- Taxonomy labels: `data/taxonomy.json`

Detailed instructions:

- [Updating images](IMAGES.md)
- [Updating publications](PUBLICATIONS.md)

## Local preview

```bash
python -m pip install -r requirements.txt
SITE_BASE="" SITE_URL="https://gdpeterson.github.io" python scripts/build.py
python -m http.server 4173 --directory dist
```

Open `http://localhost:4173/`.

For a reproducible homepage-paper selection during testing:

```bash
HOMEPAGE_RANDOM_SEED=preview python scripts/build.py
```

## Design and code principles

- Content, images, publication data, build logic, templates, and interactions
  are kept in separate modules.
- Templates use named image keys rather than hard-coded filenames.
- The build validates image paths and classic DOI resolution before publishing.
- JavaScript progressively enhances a complete static fallback.
- ORCID synchronization opens a review pull request; it does not overwrite
  curated research categories or publish directly.

## Publish

Commit and push to `main`. The workflow in `.github/workflows/pages.yml` builds
with the root-site path and deploys `dist/`. GitHub Pages must use **GitHub
Actions** as its source.
