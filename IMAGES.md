# Updating images

All site images are managed through **named image keys** in `data/images.json`.
Templates refer to keys such as `portrait` or `story_finance`; they do not need
to know filenames. This makes it possible to replace an image without editing
HTML.

## Replace an existing image

1. Add the optimized file to `static/images/`.
2. Open `data/images.json`.
3. Change the relevant `src`, `alt`, and optional `width`/`height` values.
4. Run `python scripts/build.py`.

Example:

```json
"portrait": {
  "src": "/images/garry-peterson-2026.webp",
  "alt": "Portrait of Garry Peterson outdoors near Stockholm",
  "width": 900,
  "height": 1200
}
```

The build fails with a clear message when a catalog entry points to a missing
file. This prevents broken images from being published.

## Add a new image slot

1. Add the file under `static/images/`.
2. Add a new named record to `data/images.json`.
3. Reference the key from `content/profile.json` using `image_key`, or directly
   in a template with `image('your_key')`.
4. Render it with the shared macro:

```jinja2
{% from "_image.html" import render as render_image %}
{{ render_image(image(item.image_key)) }}
```

Use `decorative=true` only when the image adds no information. Meaningful
images require concise alt text. Photographs and adapted figures should also be
recorded in an image-credit file or caption with creator, source, licence, and
changes.

## Recommended formats

- Photographs: WebP or AVIF, normally 900–1800 px wide.
- Diagrams and illustrations: SVG where practical.
- Most images: below 300 KB; large hero images: preferably below 700 KB.
- Avoid spaces and capitals in filenames.
