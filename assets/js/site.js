(() => {
  const menuButton = document.querySelector('.menu-button');
  const nav = document.querySelector('.site-nav');
  if (menuButton && nav) {
    menuButton.addEventListener('click', () => {
      const open = menuButton.getAttribute('aria-expanded') === 'true';
      menuButton.setAttribute('aria-expanded', String(!open));
      nav.classList.toggle('open', !open);
    });
  }

  const list = document.getElementById('publication-list');
  if (!list) return;
  const search = document.getElementById('pub-search');
  const year = document.getElementById('pub-year');
  const theme = document.getElementById('pub-theme');
  const count = document.getElementById('pub-results');
  const empty = document.getElementById('pub-empty');
  const items = [...list.querySelectorAll('.publication-item')];
  const update = () => {
    const query = search.value.trim().toLowerCase();
    let visible = 0;
    for (const item of items) {
      const match = (!query || item.dataset.search.includes(query)) &&
        (!year.value || item.dataset.year === year.value) &&
        (!theme.value || item.dataset.theme.split('|').includes(theme.value));
      item.hidden = !match;
      if (match) visible += 1;
    }
    count.textContent = `Showing ${visible} ${visible === 1 ? 'work' : 'works'}`;
    empty.hidden = visible !== 0;
  };
  [search, year, theme].forEach(el => el.addEventListener(el === search ? 'input' : 'change', update));
})();
