/** Mobile navigation behaviour. */
export function initMenu() {
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
    const open = menuButton.getAttribute('aria-expanded') === 'true';
    if (open && !nav.contains(event.target) && !menuButton.contains(event.target)) {
      setOpen(false);
    }
  });
}
