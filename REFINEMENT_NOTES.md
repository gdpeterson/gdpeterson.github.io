# Homepage refinement

This revision reduces the homepage from a compressed whole-site experience to six primary sections:

1. Hero with concise first-person research introduction and three stable metrics.
2. Three overlapping guiding research questions.
3. Current work: FinBio and Transformative Futures.
4. One featured research story.
5. Three open research databases.
6. Three publications: selected recent, selected classic, and automatically most recent.

The full interactive systems explorer now appears on the Research page. Audience pathways and reuse options are condensed to three links below the publication cards.

## Updating the three homepage publications

Edit `data/publication-curation.json`:

```json
"homepage_publications": {
  "selected_recent": "doi:...",
  "selected_classic": "doi:... or local:..."
}
```

The `most recent` card is calculated at build time from `data/publications-csl.json`, which can be refreshed through the ORCID workflow. Obvious supplementary-data records and the two manually selected records are skipped so all three cards remain distinct.
