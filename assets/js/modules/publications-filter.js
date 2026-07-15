/** Search and non-exclusive taxonomy filters for the publications page. */
export function initPublicationsFilter() {
  const list = document.getElementById('publication-list');
  if (!list) return;

  const search = document.getElementById('pub-search');
  const year = document.getElementById('pub-year');
  const count = document.getElementById('pub-results');
  const empty = document.getElementById('pub-empty');
  const matchAll = document.getElementById('pub-match-all');
  const reset = document.getElementById('pub-reset');
  const themeBoxes = [...document.querySelectorAll('input[name="theme"]')];
  const questionBoxes = [...document.querySelectorAll('input[name="question"]')];
  const items = [...list.querySelectorAll('.publication-item')];
  const selected = (boxes) => boxes.filter((box) => box.checked).map((box) => box.value);

  const updateUrl = () => {
    const params = new URLSearchParams();
    if (search.value.trim()) params.set('q', search.value.trim());
    if (year.value) params.set('year', year.value);
    selected(themeBoxes).forEach((value) => params.append('theme', value));
    selected(questionBoxes).forEach((value) => params.append('question', value));
    if (matchAll.checked) params.set('match', 'all');
    history.replaceState(null, '', `${location.pathname}${params.toString() ? `?${params}` : ''}`);
  };

  const update = () => {
    const query = search.value.trim().toLowerCase();
    const themes = selected(themeBoxes);
    const questions = selected(questionBoxes);
    let visible = 0;

    for (const item of items) {
      const itemThemes = item.dataset.themes.split('|').filter(Boolean);
      const itemQuestions = item.dataset.questions.split('|').filter(Boolean);
      const themeMatch = !themes.length || (
        matchAll.checked
          ? themes.every((value) => itemThemes.includes(value))
          : themes.some((value) => itemThemes.includes(value))
      );
      const questionMatch = !questions.length || questions.some((value) => itemQuestions.includes(value));
      const matches = (
        (!query || item.dataset.search.includes(query))
        && (!year.value || item.dataset.year === year.value)
        && themeMatch
        && questionMatch
      );
      item.hidden = !matches;
      if (matches) visible += 1;
    }
    count.textContent = `Showing ${visible} ${visible === 1 ? 'work' : 'works'}`;
    empty.hidden = visible !== 0;
    updateUrl();
  };

  const params = new URLSearchParams(location.search);
  search.value = params.get('q') || '';
  year.value = params.get('year') || '';
  matchAll.checked = params.get('match') === 'all';
  themeBoxes.forEach((box) => { box.checked = params.getAll('theme').includes(box.value); });
  questionBoxes.forEach((box) => { box.checked = params.getAll('question').includes(box.value); });
  [search, year, matchAll, ...themeBoxes, ...questionBoxes].forEach((element) => {
    element.addEventListener(element === search ? 'input' : 'change', update);
  });
  reset.addEventListener('click', () => {
    search.value = '';
    year.value = '';
    matchAll.checked = false;
    [...themeBoxes, ...questionBoxes].forEach((box) => { box.checked = false; });
    update();
  });
  update();
}
