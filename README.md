# Garry Peterson academic website

Source for the GitHub Pages project site at `https://gdpeterson.github.io/garrypeterson.github.io/`.

The site uses an editorial, biophilic visual system to foreground connections among people, nature, resilience, and futures. It is a static Jinja-based build with no external theme or runtime dependency in the deployed output.

## Edit content

- Profile, biography, projects, roles, talks, grants, awards, and external profiles: `content/profile.json`
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

Pushing to `main` triggers `.github/workflows/pages.yml`. The workflow builds with the project-site base path `/garrypeterson.github.io` and deploys `dist/`. GitHub Pages must be configured to use **GitHub Actions** as the source.
