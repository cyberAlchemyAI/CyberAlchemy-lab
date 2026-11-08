/* Progressive documentation shell. The full source remains readable without JS.
   Hashes identify chapters or a heading within a chapter; map URLs retain state. */
(() => {
  const article = document.getElementById('lab-article');
  if (!article) return;
  const create = (tag, className, text) => {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (text) el.textContent = text;
    return el;
  };
  const link = (href, label) => { const el = create('a', '', label); el.href = href; return el; };
  const labels = {
    start: ['Getting started', 'Explore CyberAlchemy Lab'],
    foundations: ['Getting started', 'Definitions first'],
    'system-map': ['Getting started', 'Interactive system map'],
    governance: ['Governance', 'Authority and meaning'],
    evidence: ['Governance', 'Provenance and evidence'],
    change: ['Governance', 'Lifecycle and admission'],
    purpose: ['The Lab model', 'Intent, product and project'],
    records: ['The Lab model', 'Definitions and connections'],
    agent: ['The Lab model', 'Agent work and memory'],
    learning: ['The Lab model', 'Operational learning'],
    today: ['The Lab model', 'Current operational scope'],
    'reading-next': ['Reference', 'Reference and sources']
  };
  const order = Object.keys(labels);
  const aliases = {'top': 'start', 'lab-article': 'start', 'learning-map': 'start', 'lens-governance': 'governance', 'lens-system': 'purpose', 'lens-agent': 'agent', 'lens-learning': 'learning', 'lens-operation': 'today', 'lens-reference': 'reading-next'};
  const chapters = new Map();
  const navAside = create('aside', 'docs-local-nav');
  navAside.setAttribute('aria-label', 'On this page');
  const tocDisclosure = create('details', 'docs-toc');
  const compactToc = matchMedia('(max-width:1200px)');
  const compactBrowse = matchMedia('(max-width:900px)');
  tocDisclosure.open = !compactToc.matches;
  compactToc.addEventListener('change', event => {tocDisclosure.open = !event.matches;});
  tocDisclosure.append(create('summary', '', 'On this page'));
  const tocNav = create('nav'); tocNav.setAttribute('aria-label', 'Headings on this page');
  tocDisclosure.append(tocNav); navAside.append(tocDisclosure);
  let tocObserver = null;
  function chapterHeadings(scope) {
    return [...scope.querySelectorAll('h2, h3.article-subheading, .lens-visual-heading > h3')].filter(el => !el.closest('details'));
  }
  function localContents(scope, route) {
    if (tocObserver) tocObserver.disconnect();
    tocNav.replaceChildren();
    const headings = chapterHeadings(scope);
    headings.forEach((heading, index) => {
      if (!heading.id) heading.id = `docs-${route}-heading-${index + 1}`;
      const a = link('#' + heading.id, heading.textContent.trim());
      tocNav.append(a);
    });
    if (!headings.length) tocNav.append(link('#' + route, 'Overview'));
    if ('IntersectionObserver' in window) {
      tocObserver = new IntersectionObserver(entries => {
        const visible = entries.filter(entry => entry.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
        if (!visible) return;
        for (const a of tocNav.querySelectorAll('a')) {
          if (a.hash === '#' + visible.target.id) a.setAttribute('aria-current', 'location');
          else a.removeAttribute('aria-current');
        }
      }, {rootMargin: '-95px 0px -65% 0px'});
      headings.forEach(heading => tocObserver.observe(heading));
    }
  }

  const layout = document.querySelector('.reading-layout');
  const masthead = document.querySelector('.article-masthead');
  const introduction = document.querySelector('.introduction');
  const illustration = document.querySelector('.opening-image');
  const explorer = document.getElementById('map-explorer');
  const resources = document.getElementById('reading-next');
  const overview = create('section', 'docs-overview');
  overview.dataset.docsChapter = 'start';
  overview.append(masthead);
  const paths = masthead.querySelector('.entry-paths');
  paths.id = 'choose-reading-path';
  const pathHeading = create('h2', 'docs-path-heading', 'Choose where to begin');
  paths.before(pathHeading);
  const introductionHeading = create('h2', 'docs-overview-heading', 'A shared foundation for people and agents');
  introductionHeading.id = 'docs-start-foundation';
  overview.append(introductionHeading, create('p', 'docs-overview-description', 'The Lab connects accepted meanings, evidence and decisions with the work that depends on them. Follow one incident to see how those pieces fit together.'), illustration);
  const foundations = create('section', 'docs-foundations');
  foundations.dataset.docsChapter = 'foundations';
  foundations.append(introduction);
  const mapChapter = create('section', 'docs-map-chapter');
  mapChapter.dataset.docsChapter = 'system-map';
  mapChapter.append(explorer);
  // The original article has a transition paragraph before the model section.
  // Keep such introductions with the chapter they introduce.
  let introductions = [];
  for (const child of [...article.children]) {
    if (child.matches('.prose')) introductions.push(child);
    if (child.matches('.article-section') && introductions.length) {
      child.prepend(...introductions);
      introductions = [];
    }
  }
  for (const section of article.querySelectorAll('.article-section')) {
    section.dataset.docsChapter = section.id;
    chapters.set(section.id, section);
  }
  resources.dataset.docsChapter = 'reading-next';
  article.prepend(overview, foundations);
  article.append(mapChapter, resources);
  chapters.set('start', overview); chapters.set('foundations', foundations);
  chapters.set('system-map', mapChapter); chapters.set('reading-next', resources);
  layout.append(navAside);
  const metadata = masthead.querySelector('.article-metadata');
  metadata.querySelector('div:first-child dt').textContent = 'Guide';
  metadata.querySelector('div:first-child dd').textContent = 'Concepts and examples';
  metadata.querySelector('div:last-child').remove();
  const topicHeader = create('header', 'docs-topic-header');
  const breadcrumb = create('p', 'docs-breadcrumb');
  const title = create('h1'); title.tabIndex = -1;
  topicHeader.append(breadcrumb, title); article.prepend(topicHeader);
  const pager = create('nav', 'docs-pager'); pager.setAttribute('aria-label', 'Previous and next topics'); article.append(pager);
  document.body.dataset.docsEnhanced = 'guide';
  // Assign all heading IDs before resolving an initial fragment, so search
  // results can open a subsection directly from another page.
  for (const [route, scope] of chapters) chapterHeadings(scope).forEach((heading, index) => {
    if (!heading.id) heading.id = `docs-${route}-heading-${index + 1}`;
  });
  const disclosure = document.getElementById('article-contents');
  disclosure.open = !matchMedia('(max-width:900px)').matches;
  compactBrowse.addEventListener('change', event => {disclosure.open = !event.matches;});
  let current = null;

  function routeFor(id) {
    if (chapters.has(id)) return id;
    if (aliases[id]) return aliases[id];
    const target = document.getElementById(id);
    const chapter = target && target.closest('[data-docs-chapter]');
    return chapter ? chapter.dataset.docsChapter : 'start';
  }
  function show(scroll = true, focus = false) {
    let id; try {id = decodeURIComponent(location.hash.slice(1));} catch {id = '';}
    const route = routeFor(id);
    const changed = current !== route;
    current = route; document.body.dataset.docsRoute = route;
    for (const [key, chapter] of chapters) chapter.hidden = key !== route;
    topicHeader.hidden = route === 'start';
    breadcrumb.replaceChildren(link('#start', 'CyberAlchemy Lab'), create('span', '', ' / ' + labels[route][0]));
    title.textContent = labels[route][1];
    document.title = labels[route][1] + ' · CyberAlchemy Lab';
    for (const a of document.querySelectorAll('.article-tree [data-section]')) {
      if (a.dataset.section === route) a.setAttribute('aria-current', 'page');
      else a.removeAttribute('aria-current');
    }
    for (const a of document.querySelectorAll('[data-docs-top]')) {
      const active = a.dataset.docsTop === (route === 'start' ? 'start' : route === 'system-map' ? 'map' : 'guide');
      if (active) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current');
    }
    if (changed) {
      localContents(chapters.get(route), route);
      pager.replaceChildren();
      const index = order.indexOf(route);
      for (const [direction, other] of [['Previous', order[index - 1]], ['Next', order[index + 1]]]) {
        if (!other) {pager.append(create('span'));continue;}
        const a = link('#' + other, '');
        a.append(create('span', '', direction), create('strong', '', labels[other][1] + (direction === 'Next' ? ' →' : '')));
        pager.append(a);
      }
    }
    if (route === 'system-map') {
      explorer.open = true;
      requestAnimationFrame(() => window.dispatchEvent(new Event('resize')));
    }
    if (focus && route !== 'start') title.focus({preventScroll: true});
    if (scroll) requestAnimationFrame(() => {
      const target = document.getElementById(id);
      if (target && target.closest('[data-docs-chapter]') && id !== route) target.scrollIntoView({block: 'start', behavior: 'instant'});
      else window.scrollTo({top: 0, behavior: 'instant'});
    });
  }
  document.addEventListener('click', event => {
    const a = event.target.closest('a[href]');
    if (!a || a.hasAttribute('data-map-jump') || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || a.target || a.hasAttribute('download')) return;
    const url = new URL(a.href, location.href);
    if (url.pathname !== location.pathname || !url.hash || url.search !== location.search) return;
    const id = decodeURIComponent(url.hash.slice(1));
    if (!document.getElementById(id) && !chapters.has(id) && !aliases[id]) return;
    event.preventDefault();
    if (url.href !== location.href) history.pushState(null, '', url);
    if (matchMedia('(max-width:900px)').matches) disclosure.open = false;
    show(true, routeFor(id) !== current);

  });
  window.addEventListener('hashchange', () => show());
  window.addEventListener('popstate', () => show());
  document.addEventListener('lab:mapnavigate', () => show(false));
  show(true);
  // Initial fragment positioning runs as the document finishes loading. Apply
  // the chapter scroll after it, so direct links expose the topic heading.
  if (document.readyState !== 'complete') window.addEventListener('load', () => show(true), {once: true});

})();
