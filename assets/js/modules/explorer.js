/** Accessible interactive social-ecological systems explorer. */
export function initExplorer() {
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
}
