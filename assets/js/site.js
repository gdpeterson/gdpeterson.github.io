(() => {
<<<<<<< HEAD
  const initMenu = () => {
    const menuButton = document.querySelector('.menu-button');
    const nav = document.querySelector('.site-nav');
    if (!menuButton || !nav) return;

    const setOpen = (open) => {
      menuButton.setAttribute('aria-expanded', String(open));
      nav.classList.toggle('open', open);
    };

    menuButton.addEventListener('click', () => {
      setOpen(menuButton.getAttribute('aria-expanded') !== 'true');
    });

    nav.addEventListener('click', (event) => {
      if (event.target.closest('a')) setOpen(false);
    });

    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && menuButton.getAttribute('aria-expanded') === 'true') {
        setOpen(false);
        menuButton.focus();
      }
    });

    document.addEventListener('click', (event) => {
      if (menuButton.getAttribute('aria-expanded') === 'true' && !nav.contains(event.target) && !menuButton.contains(event.target)) {
        setOpen(false);
      }
    });
  };

  const initExplorer = () => {
    const root = document.querySelector('[data-system-explorer]');
    const dataElement = document.getElementById('explorer-data');
    if (!root || !dataElement) return;

    let data;
    try {
      data = JSON.parse(dataElement.textContent);
    } catch (error) {
      console.warn('Unable to initialise systems explorer.', error);
      return;
    }

    const lenses = Object.fromEntries(data.lenses.map((lens) => [lens.id, lens]));
    const tabs = [...root.querySelectorAll('.explorer-tab')];
    const nodes = [...root.querySelectorAll('.system-node')];
    const output = {
      label: document.getElementById('explorer-lens-label'),
      title: document.getElementById('explorer-lens-title'),
      summary: document.getElementById('explorer-lens-summary'),
      kicker: document.getElementById('explorer-node-kicker'),
      nodeTitle: document.getElementById('explorer-node-title'),
      body: document.getElementById('explorer-node-body'),
      question: document.getElementById('explorer-question'),
      link: document.getElementById('explorer-link'),
    };

    const render = (lensId, nodeId) => {
      const lens = lenses[lensId] || data.lenses[0];
      const selectedNode = lens.nodes[nodeId] ? nodeId : lens.default_node;
      const detail = lens.nodes[selectedNode];

      root.dataset.lens = lens.id;
      root.dataset.node = selectedNode;

      tabs.forEach((tab) => {
        const selected = tab.dataset.lens === lens.id;
        tab.setAttribute('aria-selected', String(selected));
        tab.tabIndex = selected ? 0 : -1;
      });

      nodes.forEach((node) => {
        const selected = node.dataset.node === selectedNode;
        node.classList.toggle('is-selected', selected);
        node.classList.toggle('is-related', lens.active_nodes.includes(node.dataset.node));
        node.setAttribute('aria-pressed', String(selected));
      });

      output.label.textContent = `${lens.label} lens`;
      output.title.textContent = lens.title;
      output.summary.textContent = lens.summary;
      output.kicker.textContent = detail.kicker;
      output.nodeTitle.textContent = detail.title;
      output.body.textContent = detail.body;
      output.question.textContent = lens.question;
      output.link.firstChild.textContent = `${lens.link_label} `;
      const siteBase = document.body.dataset.siteBase || '';
      output.link.href = lens.link.startsWith('/') ? `${siteBase}${lens.link}` : lens.link;
      if (lens.link.startsWith('http')) {
        output.link.target = '_blank';
        output.link.rel = 'noopener';
        output.link.querySelector('[aria-hidden="true"]').textContent = '↗';
      } else {
        output.link.removeAttribute('target');
        output.link.removeAttribute('rel');
        output.link.querySelector('[aria-hidden="true"]').textContent = '→';
      }
    };

    tabs.forEach((tab, index) => {
      tab.addEventListener('click', () => {
        const lens = lenses[tab.dataset.lens];
        render(lens.id, lens.default_node);
      });

      tab.addEventListener('keydown', (event) => {
        if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
        event.preventDefault();
        let nextIndex = index;
        if (event.key === 'ArrowLeft') nextIndex = (index - 1 + tabs.length) % tabs.length;
        if (event.key === 'ArrowRight') nextIndex = (index + 1) % tabs.length;
        if (event.key === 'Home') nextIndex = 0;
        if (event.key === 'End') nextIndex = tabs.length - 1;
        tabs[nextIndex].focus();
        tabs[nextIndex].click();
      });
    });

    nodes.forEach((node) => {
      node.addEventListener('click', () => render(root.dataset.lens, node.dataset.node));
    });

    render(root.dataset.lens, root.dataset.node);
  };

  const initPublications = () => {
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
      selected(themeBoxes).forEach((v) => params.append('theme', v));
      selected(questionBoxes).forEach((v) => params.append('question', v));
      if (matchAll.checked) params.set('match', 'all');
      history.replaceState(null, '', `${location.pathname}${params.toString() ? `?${params}` : ''}`);
    };
    const update = () => {
      const query = search.value.trim().toLowerCase();
      const themes = selected(themeBoxes); const questions = selected(questionBoxes);
      let visible = 0;
      for (const item of items) {
        const itemThemes = item.dataset.themes.split('|').filter(Boolean);
        const itemQuestions = item.dataset.questions.split('|').filter(Boolean);
        const themeMatch = !themes.length || (matchAll.checked ? themes.every((x) => itemThemes.includes(x)) : themes.some((x) => itemThemes.includes(x)));
        const questionMatch = !questions.length || questions.some((x) => itemQuestions.includes(x));
        const match = (!query || item.dataset.search.includes(query)) && (!year.value || item.dataset.year === year.value) && themeMatch && questionMatch;
        item.hidden = !match; if (match) visible += 1;
      }
      count.textContent = `Showing ${visible} ${visible === 1 ? 'work' : 'works'}`;
      empty.hidden = visible !== 0; updateUrl();
    };
    const params = new URLSearchParams(location.search);
    search.value = params.get('q') || ''; year.value = params.get('year') || ''; matchAll.checked = params.get('match') === 'all';
    themeBoxes.forEach((b) => { b.checked = params.getAll('theme').includes(b.value); });
    questionBoxes.forEach((b) => { b.checked = params.getAll('question').includes(b.value); });
    [search, year, matchAll, ...themeBoxes, ...questionBoxes].forEach((element) => element.addEventListener(element === search ? 'input' : 'change', update));
    reset.addEventListener('click', () => { search.value=''; year.value=''; matchAll.checked=false; [...themeBoxes,...questionBoxes].forEach((b)=>b.checked=false); update(); });
    update();
  };

  initMenu();
  initExplorer();
  initPublications();
=======
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
>>>>>>> origin/main
})();
