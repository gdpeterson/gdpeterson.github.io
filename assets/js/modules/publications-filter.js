/**
 * Progressive enhancements for the publication catalogue.
 *
 * Responsibilities:
 * - search, sorting, and non-exclusive taxonomy filters
 * - compact/readable display preference
 * - active-filter chips and URL persistence
 * - accessible long-author disclosure
 * - copy-citation actions
 */
export function initPublicationsFilter() {
  const list = document.getElementById('publication-list');
  if (!list) return;

  const search = document.getElementById('pub-search');
  const year = document.getElementById('pub-year');
  const sort = document.getElementById('pub-sort');
  const count = document.getElementById('pub-results');
  const empty = document.getElementById('pub-empty');
  const matchAll = document.getElementById('pub-match-all');
  const openAccess = document.getElementById('pub-open-access');
  const includeSecondary = document.getElementById('pub-include-secondary');
  const reset = document.getElementById('pub-reset');
  const filterPanel = document.getElementById('publication-filter-panel');
  const filterToggle = document.getElementById('pub-filter-toggle');
  const filterCount = document.getElementById('pub-filter-count');
  const activeFilters = document.getElementById('pub-active-filters');
  const themeBoxes = [...document.querySelectorAll('input[name="theme"]')];
  const questionBoxes = [...document.querySelectorAll('input[name="question"]')];
  const typeBoxes = [...document.querySelectorAll('input[name="type"]')];
  const viewButtons = [...document.querySelectorAll('[data-view]')];
  const items = [...list.querySelectorAll('.publication-item')];

  const selected = (boxes) => boxes.filter((box) => box.checked).map((box) => box.value);
  const labelFor = (box) => box.closest('label')?.querySelector('span')?.textContent?.trim() || box.value;

  const setPanel = (open) => {
    filterPanel.hidden = !open;
    filterToggle.setAttribute('aria-expanded', String(open));
  };

  const activeCount = () => [
    search.value.trim(), year.value, ...selected(typeBoxes), ...selected(themeBoxes),
    ...selected(questionBoxes), openAccess.checked ? 'oa' : '',
    includeSecondary.checked ? 'secondary' : '', matchAll.checked ? 'all' : '',
  ].filter(Boolean).length;

  const updateUrl = () => {
    const params = new URLSearchParams();
    if (search.value.trim()) params.set('q', search.value.trim());
    if (year.value) params.set('year', year.value);
    if (sort.value !== 'newest') params.set('sort', sort.value);
    selected(typeBoxes).forEach((value) => params.append('type', value));
    selected(themeBoxes).forEach((value) => params.append('theme', value));
    selected(questionBoxes).forEach((value) => params.append('question', value));
    if (matchAll.checked) params.set('match', 'all');
    if (openAccess.checked) params.set('oa', 'true');
    if (includeSecondary.checked) params.set('secondary', 'true');
    const view = list.dataset.view;
    if (view !== 'readable') params.set('view', view);
    history.replaceState(null, '', `${location.pathname}${params.toString() ? `?${params}` : ''}`);
  };

  const sortItems = () => {
    const comparator = {
      newest: (a, b) => Number(b.dataset.yearSort) - Number(a.dataset.yearSort)
        || a.dataset.titleSort.localeCompare(b.dataset.titleSort),
      oldest: (a, b) => Number(a.dataset.yearSort) - Number(b.dataset.yearSort)
        || a.dataset.titleSort.localeCompare(b.dataset.titleSort),
      title: (a, b) => a.dataset.titleSort.localeCompare(b.dataset.titleSort),
    }[sort.value];
    [...items].sort(comparator).forEach((item) => list.appendChild(item));
  };

  const removeFilter = (kind, value = '') => {
    if (kind === 'search') search.value = '';
    if (kind === 'year') year.value = '';
    if (kind === 'oa') openAccess.checked = false;
    if (kind === 'secondary') includeSecondary.checked = false;
    if (kind === 'match') matchAll.checked = false;
    const groups = { type: typeBoxes, theme: themeBoxes, question: questionBoxes };
    if (groups[kind]) groups[kind].find((box) => box.value === value).checked = false;
    update();
  };

  const renderActiveFilters = () => {
    activeFilters.replaceChildren();
    const chips = [];
    if (search.value.trim()) chips.push(['search', '', `Search: ${search.value.trim()}`]);
    if (year.value) chips.push(['year', '', year.value]);
    for (const box of typeBoxes.filter((item) => item.checked)) chips.push(['type', box.value, labelFor(box)]);
    for (const box of themeBoxes.filter((item) => item.checked)) chips.push(['theme', box.value, labelFor(box)]);
    for (const box of questionBoxes.filter((item) => item.checked)) chips.push(['question', box.value, labelFor(box)]);
    if (openAccess.checked) chips.push(['oa', '', 'Open access']);
    if (includeSecondary.checked) chips.push(['secondary', '', 'Datasets & supplements']);
    if (matchAll.checked) chips.push(['match', '', 'Match all domains']);

    for (const [kind, value, label] of chips) {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'active-filter-chip';
      button.textContent = `${label} ×`;
      button.setAttribute('aria-label', `Remove filter ${label}`);
      button.addEventListener('click', () => removeFilter(kind, value));
      activeFilters.appendChild(button);
    }
    activeFilters.hidden = chips.length === 0;
    filterCount.textContent = String(activeCount());
  };

  const update = () => {
    const query = search.value.trim().toLowerCase();
    const themes = selected(themeBoxes);
    const questions = selected(questionBoxes);
    const types = selected(typeBoxes);
    let visible = 0;

    for (const item of items) {
      const itemThemes = item.dataset.themes.split('|').filter(Boolean);
      const itemQuestions = item.dataset.questions.split('|').filter(Boolean);
      const themeMatch = !themes.length || (
        matchAll.checked
          ? themes.every((value) => itemThemes.includes(value))
          : themes.some((value) => itemThemes.includes(value))
      );
      const matches = (
        (!query || item.dataset.search.includes(query))
        && (!year.value || item.dataset.year === year.value)
        && (!types.length || types.includes(item.dataset.type))
        && (!questions.length || questions.some((value) => itemQuestions.includes(value)))
        && themeMatch
        && (!openAccess.checked || item.dataset.openAccess === 'true')
        && (includeSecondary.checked || item.dataset.secondary !== 'true')
      );
      item.hidden = !matches;
      if (matches) visible += 1;
    }

    sortItems();
    count.textContent = `Showing ${visible} ${visible === 1 ? 'work' : 'works'}`;
    empty.hidden = visible !== 0;
    renderActiveFilters();
    updateUrl();
  };

  const params = new URLSearchParams(location.search);
  search.value = params.get('q') || '';
  year.value = params.get('year') || '';
  sort.value = params.get('sort') || 'newest';
  matchAll.checked = params.get('match') === 'all';
  openAccess.checked = params.get('oa') === 'true';
  includeSecondary.checked = params.get('secondary') === 'true';
  typeBoxes.forEach((box) => { box.checked = params.getAll('type').includes(box.value); });
  themeBoxes.forEach((box) => { box.checked = params.getAll('theme').includes(box.value); });
  questionBoxes.forEach((box) => { box.checked = params.getAll('question').includes(box.value); });

  const savedView = params.get('view') || localStorage.getItem('publication-view') || 'readable';
  list.dataset.view = savedView;
  viewButtons.forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.view === savedView)));

  filterToggle.addEventListener('click', () => setPanel(filterPanel.hidden));
  [search, year, sort, matchAll, openAccess, includeSecondary, ...typeBoxes, ...themeBoxes, ...questionBoxes]
    .forEach((element) => element.addEventListener(element === search ? 'input' : 'change', update));

  reset.addEventListener('click', () => {
    search.value = '';
    year.value = '';
    sort.value = 'newest';
    matchAll.checked = false;
    openAccess.checked = false;
    includeSecondary.checked = false;
    [...typeBoxes, ...themeBoxes, ...questionBoxes].forEach((box) => { box.checked = false; });
    update();
  });

  viewButtons.forEach((button) => button.addEventListener('click', () => {
    list.dataset.view = button.dataset.view;
    localStorage.setItem('publication-view', button.dataset.view);
    viewButtons.forEach((item) => item.setAttribute('aria-pressed', String(item === button)));
    updateUrl();
  }));

  list.addEventListener('click', async (event) => {
    const authorButton = event.target.closest('.author-toggle');
    if (authorButton) {
      const container = authorButton.closest('.publication-authors');
      const short = container.querySelector('.authors-short');
      const full = container.querySelector('.authors-full');
      const expanded = authorButton.getAttribute('aria-expanded') === 'true';
      short.hidden = !expanded;
      full.hidden = expanded;
      authorButton.setAttribute('aria-expanded', String(!expanded));
      authorButton.textContent = expanded ? 'Show all authors' : 'Show fewer authors';
      return;
    }

    const copyButton = event.target.closest('.copy-citation');
    if (copyButton) {
      try {
        await navigator.clipboard.writeText(copyButton.dataset.citation);
        const original = copyButton.textContent;
        copyButton.textContent = 'Copied';
        setTimeout(() => { copyButton.textContent = original; }, 1500);
      } catch {
        copyButton.textContent = 'Copy unavailable';
      }
    }
  });

  setPanel(activeCount() > 0);
  update();
}
