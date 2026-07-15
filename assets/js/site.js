/** Entry point for optional, progressively enhanced site interactions. */
import { initMenu } from './modules/menu.js';
import { initExplorer } from './modules/explorer.js';
import { initHomepagePublications } from './modules/homepage-publications.js';
import { initPublicationsFilter } from './modules/publications-filter.js';

initMenu();
initExplorer();
initHomepagePublications();
initPublicationsFilter();
