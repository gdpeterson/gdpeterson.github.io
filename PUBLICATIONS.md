# Updating publications

The publication workflow separates machine-managed facts from reviewed
interpretation.

## Files

- `data/publications-csl.json` — bibliographic records imported from ORCID and
  DOI metadata. Do not hand-edit this for routine corrections.
- `data/publication-curation.json` — reviewed themes, questions, summaries,
  output types, featured status, and DOI corrections.
- `data/classic-dois.txt` — ten classic-paper DOIs, one per line. Blank lines
  and comments beginning with `#` are allowed.
- `data/taxonomy.json` — labels and descriptions for the three guiding
  questions and five non-exclusive research domains.

## Normal update from ORCID

1. Update the public ORCID record.
2. In GitHub, run **Actions → Update publications → Run workflow**.
3. Review the generated pull request.
4. Add or correct editorial metadata in `data/publication-curation.json`.
5. Merge only after checking duplicates, output type, DOI, and categories.

ORCID supplies what works exist. The curation file supplies what those works
mean within Peterson's research programme.

## Homepage papers

- **Most recent** is the newest eligible record.
- **Recent selection** is randomly chosen in the browser from the ten newest
  eligible records after excluding the most recent.
- **Classic selection** is randomly chosen from DOI records listed in
  `data/classic-dois.txt`.

The build also creates a no-JavaScript fallback. Set a deterministic seed for a
reproducible preview:

```bash
HOMEPAGE_RANDOM_SEED=preview python scripts/build.py
```

## Add or replace a classic DOI

Edit `data/classic-dois.txt`, keeping exactly ten unique DOI values. Then build.
The build reports unresolved DOI values and stops if no listed classic can be
matched.

## Correct one publication

Use the publication's stable key in `data/publication-curation.json`, normally
`doi:<lowercase-doi>`. Example:

```json
"doi:10.0000/example": {
  "themes": ["scenarios-futures", "governance-transformation"],
  "questions": ["navigate-shape-futures"],
  "output_type": "Journal article",
  "summary": "Plain-language description for the website.",
  "review_status": "reviewed"
}
```

## Open-access status

Open-access corrections are maintained separately in:

```text
data/publication-access.json
```

Use the publication's stable ID, normally its DOI prefixed with `doi:`:

```json
{
  "records": {
    "doi:10.5751/es-12345-260101": {
      "open_access": true,
      "url": "https://www.ecologyandsociety.org/vol26/iss1/art1/",
      "license": "CC BY 4.0"
    }
  }
}
```

Set `open_access` to `false` only when the status has been checked. If a record is
absent, the build makes conservative inferences for Ecology and Society and a
small list of established open repositories. Unknown papers are not labelled.

## Publication-page presentation

The catalogue is generated from the normalized records; do not edit publication
HTML by hand. The page provides:

- search, year, output-type, domain, question, and open-access filters;
- readable and compact views;
- collapsed long author lists with Garry Peterson highlighted;
- output-type labels and separate domain/question treatments;
- DOI, open-access, and copy-citation actions.

Datasets and supplementary records are hidden by default but remain available
through the filters.
