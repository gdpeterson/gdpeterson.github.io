/** Rotate recent and classic homepage papers on each visit. */
export function initHomepagePublications() {
  const dataElement = document.getElementById('homepage-publication-data');
  if (!dataElement) return;

  let pools;
  try {
    pools = JSON.parse(dataElement.textContent);
  } catch (error) {
    console.warn('Unable to randomize homepage publications.', error);
    return;
  }

  const randomIndex = (length) => {
    if (length <= 1) return 0;
    if (window.crypto?.getRandomValues) {
      const value = new Uint32Array(1);
      window.crypto.getRandomValues(value);
      return value[0] % length;
    }
    return Math.floor(Math.random() * length);
  };

  const updateCard = (slot, publication) => {
    const card = document.querySelector(`[data-publication-slot="${slot}"]`);
    if (!card || !publication) return;
    const fields = {
      year: card.querySelector('[data-pub-year]'),
      type: card.querySelector('[data-pub-type]'),
      title: card.querySelector('[data-pub-title]'),
      authors: card.querySelector('[data-pub-authors]'),
      summary: card.querySelector('[data-pub-summary]'),
      link: card.querySelector('[data-pub-link]'),
    };

    fields.year.textContent = publication.year || '—';
    fields.type.textContent = publication.type || 'Publication';
    fields.title.textContent = publication.title || 'Untitled publication';
    fields.authors.textContent = publication.authors_display || '';
    fields.summary.textContent = publication.summary || '';
    fields.summary.hidden = !publication.summary;

    for (const element of [fields.title, fields.link]) {
      if (publication.url) {
        element.href = publication.url;
        element.target = '_blank';
        element.rel = 'noopener';
      } else {
        element.href = `${document.body.dataset.siteBase || ''}/publications/`;
        element.removeAttribute('target');
        element.removeAttribute('rel');
      }
    }
    fields.link.setAttribute('aria-label', `Open ${slot} publication: ${publication.title}`);
  };

  for (const slot of ['recent', 'classic']) {
    const pool = Array.isArray(pools[slot]) ? pools[slot] : [];
    if (pool.length) updateCard(slot, pool[randomIndex(pool.length)]);
  }
}
