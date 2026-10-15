"""Deterministic event availability; a schedule never establishes form readiness."""
from datetime import datetime


def event_state(config, at=None):
    now = datetime.fromisoformat(at or config['status_as_of'])
    if now.utcoffset() is None:
        raise ValueError('Event status requires a timestamp with a timezone.')
    stamp = lambda key: datetime.fromisoformat(config[key])
    if now < stamp('registration_opens_at'):
        phase, label = 'before', 'Registration has not opened yet.'
    elif now <= stamp('submissions_close_at'):
        phase, label = 'building', 'Registration and building period'
    elif now < stamp('voting_opens_at'):
        phase, label = 'submitted', 'Registration and submissions have closed.'
    elif now < stamp('voting_closes_at'):
        phase, label = 'voting', 'Participant voting period'
    elif now <= stamp('selection_ends_at'):
        phase, label = 'review', 'Voting has closed. Results are under review.'
    else:
        phase, label = 'ended', 'The event schedule has ended.'
    available = {
        'registration': phase == 'building',
        'submission': phase == 'building',
        'gallery': True,
        'voting': phase == 'voting' and config.get('voting_access_verified') is True,
    }
    pending = {'registration': 'Registration details pending', 'submission': 'Submission link pending',
               'gallery': 'Project gallery pending', 'voting': 'Voting access pending'}
    actions = {}
    for key in available:
        url = config.get(key + '_url')
        enabled = available[key] and bool(url)
        if enabled:
            message = {'registration': 'Register', 'submission': 'Submit project',
                       'gallery': 'View projects', 'voting': 'Open ballot'}[key]
        elif key == 'gallery' or available[key] or (key == 'voting' and phase == 'voting'):
            message = pending[key]
        elif phase == 'before' or (key == 'voting' and phase in ('building', 'submitted')):
            message = 'Opens at the scheduled time'
        else:
            message = 'Registration closed' if key == 'registration' else 'Submissions closed' if key == 'submission' else 'Voting closed'
        actions[key] = {'enabled': enabled, 'label': message, 'url': url if enabled else None}
    if phase == 'building':
        label = 'Registration is open.' if actions['registration']['enabled'] else 'Registration details pending.'
    elif phase == 'voting':
        label = 'Participant voting is open.' if actions['voting']['enabled'] else 'Voting access pending.'
    return {'phase': phase, 'label': label, 'actions': actions}
