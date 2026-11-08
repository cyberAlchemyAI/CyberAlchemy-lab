/* Basic WAI-ARIA carousel: native controls, stable layout, no dependencies. */
(() => {
  const root = document.querySelector('[data-idea-carousel]');
  if (!root) return;
  const slides = [...root.querySelectorAll('.hack-idea-slide')];
  const viewport = root.querySelector('.hack-carousel-slides');
  const rotation = root.querySelector('[data-rotation]');
  const count = root.querySelector('[data-count]');
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const interval = 18000;
  let index = 0;
  let requested = !motion.matches;
  let inView = false;
  let hovering = false;
  let timer;
  let pointerIntent = null;
  let touchStart = null;

  function schedule() {
    clearTimeout(timer);
    rotation.textContent = requested ? 'Pause' : 'Play';
    rotation.setAttribute('aria-label', requested ? 'Pause autoplay' : 'Play autoplay');
    const running = requested && inView && !hovering && !document.hidden;
    viewport.setAttribute('aria-live', running ? 'off' : 'polite');
    if (running) timer = setTimeout(() => show(index + 1), interval);
  }

  function show(next) {
    index = (next + slides.length) % slides.length;
    // Warm the next illustration while the current idea is being read.
    slides[index].querySelector('img').loading = 'eager';
    slides[(index + 1) % slides.length].querySelector('img').loading = 'eager';
    slides.forEach((slide, i) => {
      const active = i === index;
      slide.classList.toggle('is-active', active);
      slide.inert = !active;
      slide.setAttribute('aria-hidden', String(!active));
      slide.setAttribute('role', 'group');
      slide.setAttribute('aria-roledescription', 'slide');
      slide.setAttribute('aria-label', `${i + 1} of ${slides.length}: ${slide.querySelector('h3').textContent}`);
      slide.removeAttribute('aria-labelledby');
    });
    count.textContent = `${String(index + 1).padStart(2, '0')} / ${String(slides.length).padStart(2, '0')}`;
    schedule();
  }

  function pause() {
    requested = false;
    schedule();
  }

  root.querySelector('[data-previous]').addEventListener('click', () => { pause(); show(index - 1); });
  root.querySelector('[data-next]').addEventListener('click', () => { pause(); show(index + 1); });
  // Preserve a pointer user's intent when focus itself pauses rotation.
  rotation.addEventListener('pointerdown', () => { pointerIntent = requested; });
  rotation.addEventListener('pointercancel', () => { pointerIntent = null; });
  rotation.addEventListener('click', () => {
    requested = !(pointerIntent ?? requested);
    pointerIntent = null;
    schedule();
  });
  root.addEventListener('focusin', pause);
  root.addEventListener('mouseenter', () => { hovering = true; schedule(); });
  root.addEventListener('mouseleave', () => { hovering = false; schedule(); });
  document.addEventListener('visibilitychange', schedule);
  motion.addEventListener('change', () => { if (motion.matches) pause(); });

  viewport.addEventListener('pointerdown', event => {
    if (event.pointerType !== 'touch') return;
    pause();
    touchStart = { x: event.clientX, y: event.clientY };
  }, { passive: true });
  viewport.addEventListener('pointerup', event => {
    if (!touchStart || event.pointerType !== 'touch') return;
    const dx = event.clientX - touchStart.x;
    const dy = event.clientY - touchStart.y;
    touchStart = null;
    if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy) * 1.5) show(index + (dx < 0 ? 1 : -1));
  }, { passive: true });
  viewport.addEventListener('pointercancel', () => { touchStart = null; });

  root.setAttribute('aria-roledescription', 'carousel');
  show(0);
  root.classList.add('is-ready');
  root.querySelector('.hack-carousel-toolbar').hidden = false;
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(entries => {
      inView = entries[0].intersectionRatio >= 0.15;
      schedule();
    }, { threshold: 0.15 }).observe(root);
  } else {
    inView = true;
    schedule();
  }
})();
