# Garry Peterson academic website

Source for the GitHub Pages project site at `https://gdpeterson.github.io/`.

The site uses a biophilic, systems-oriented visual language to foreground connections among people, nature, resilience, and futures. Its typography and accent palette are informed by the public Stockholm Resilience Centre graphic manual (Lato, Fire, Water, Sky, Olive, and Stockholm University Blue), while the design remains a distinct personal academic identity rather than an official SRC template. Original illustrations draw on themes in Peterson’s research and Resilience Alliance practice: landscape mosaics, feedbacks, thresholds, participatory futures, and cross-scale connections. The homepage includes an accessible interactive systems explorer, audience-specific pathways, evidence-rich research stories, and direct routes for reusing the research. It is a static Jinja-based build; the only browser-time design dependency is the Lato stylesheet served by Google Fonts.

## Edit content

- Profile, biography, audience pathways, systems-explorer content, research stories, reuse pathways, projects, roles, talks, grants, awards, and external profiles: `content/profile.json`
- Publications: `data/publications-csl.json`
- Styling: `assets/css/site.css`
- Page templates: `templates/`

## Local preview

```bash
python -m pip install -r requirements.txt
python scripts/build.py
python -m http.server 4173 --directory dist
```

Then open `http://localhost:4173`.

## Publish

Pushing to `main` triggers `.github/workflows/pages.yml`. The workflow builds with the root-site base path `/` and deploys `dist/`. GitHub Pages must be configured to use **GitHub Actions** as the source.

## Maintainable research taxonomy

The site uses two non-exclusive layers:

- Three guiding questions and five research domains are defined once in `data/taxonomy.json`.
- Bibliographic facts are stored in `data/publications-csl.json` and can be refreshed from ORCID.
- Human-reviewed interpretation is stored separately in `data/publication-curation.json`, keyed by DOI where possible.

The build merges these files into the Publications page, `dist/publications.json`, homepage selections, counts, and shareable filtered URLs.

### Update publications

Run **Actions → Update publications from ORCID → Run workflow**. The monthly workflow also runs automatically and opens a pull request; it never publishes directly. Review new records and add or revise their non-exclusive metadata in `data/publication-curation.json` before merging.

Example:

```json
"doi:10.1000/example": {
  "themes": ["scenarios-futures", "governance-transformation"],
  "questions": ["navigate-shape-futures", "people-nature-connections"],
  "featured": true,
  "summary": "Plain-language account of the paper's contribution.",
  "review_status": "reviewed"
}
```

For a local refresh:

```bash
python scripts/update_orcid.py
pip install -r requirements.txt
python scripts/build.py
```
