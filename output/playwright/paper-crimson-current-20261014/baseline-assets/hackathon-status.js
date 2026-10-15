/* The maintained schedule is shared by both entrances. No form is invented. */
(() => {
  const node = document.getElementById('event-config');
  if (!node) return;
  const config = JSON.parse(node.textContent);
  const state = (at = Date.now()) => {
    const stamp = key => Date.parse(config[key]);
    const phase = at < stamp('registration_opens_at') ? 'before'
      : at <= stamp('submissions_close_at') ? 'building'
      : at < stamp('voting_opens_at') ? 'submitted'
      : at < stamp('voting_closes_at') ? 'voting'
      : at <= stamp('selection_ends_at') ? 'review' : 'ended';
    const allowed = {registration: phase === 'building', submission: phase === 'building', gallery: true,
      voting: phase === 'voting' && config.voting_access_verified === true};
    const pending = {registration: 'Registration details pending', submission: 'Submission link pending',
      gallery: 'Project gallery pending', voting: 'Voting access pending'};
    const names = {registration: 'Register', submission: 'Submit project', gallery: 'View projects', voting: 'Open ballot'};
    const actions = {};
    for (const key of Object.keys(allowed)) {
      const value = config[key + '_url'];
      let url;
      try { const parsed = new URL(value); if (parsed.protocol === 'https:' && !parsed.username && !parsed.password) url = parsed.href; } catch {}
      const enabled = allowed[key] && !!url;
      const label = enabled ? names[key]
        : key === 'gallery' || allowed[key] || (key === 'voting' && phase === 'voting') ? pending[key]
        : phase === 'before' || (key === 'voting' && ['building', 'submitted'].includes(phase)) ? 'Opens at the scheduled time'
        : key === 'registration' ? 'Registration closed' : key === 'submission' ? 'Submissions closed' : 'Voting closed';
      actions[key] = {enabled, label, url: enabled ? url : null};
    }
    const label = phase === 'before' ? 'Registration has not opened yet.'
      : phase === 'building' ? (actions.registration.enabled ? 'Registration is open.' : 'Registration details pending.')
      : phase === 'submitted' ? 'Registration and submissions have closed.'
      : phase === 'voting' ? (actions.voting.enabled ? 'Participant voting is open.' : 'Voting access pending.')
      : phase === 'review' ? 'Voting has closed. Results are under review.' : 'The event schedule has ended.';
    return {phase, label, actions};
  };
  function refresh() {
    const current = state();
    for (const el of document.querySelectorAll('[data-event-status]')) el.textContent = current.label;
    for (const el of document.querySelectorAll('[data-event-action]')) {
      const action = current.actions[el.dataset.eventAction];
      const control = document.createElement(action.enabled ? 'a' : 'span');
      control.className = action.enabled ? 'text-link' : 'hack-coming-soon';
      control.textContent = action.label;
      if (action.enabled) control.href = action.url;
      el.replaceChildren(control);
    }
  }
  window.LabEventStatus = {state, refresh};
  refresh();
  // Refresh at an actual schedule boundary rather than polling the page.
  let timer;
  function schedule() {
    clearTimeout(timer);
    const next = ['registration_opens_at', 'submissions_close_at', 'voting_opens_at', 'voting_closes_at', 'selection_ends_at']
      .map(key => Date.parse(config[key]) + 1).filter(time => time > Date.now()).sort((a, b) => a - b)[0];
    if (next) timer = setTimeout(() => { refresh(); schedule(); }, Math.min(next - Date.now(), 2147483647));
  }
  document.addEventListener('visibilitychange', () => { if (!document.hidden) { refresh(); schedule(); } });
  schedule();
})();
