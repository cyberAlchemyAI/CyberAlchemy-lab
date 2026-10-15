"""Read-only pinned legacy-store adapter for candidate construction."""
from pathlib import Path
from .replay import ReplayPins, full_replay, replay


class VerifiedLegacyReadStore:
    """No provisioning, signing, admission, checkpoint or mutation methods."""
    def __init__(self, path, repository, executable_repo, pins: ReplayPins):
        self.path = Path(path).resolve()
        self.repository = Path(repository).resolve()
        self.executable_repo = Path(executable_repo).resolve()
        self.pins = pins

    def replay(self, *, require_current=False):
        return replay(self.path, self.repository, self.executable_repo, self.pins, require_current=require_current)

    def verify_full(self, *, require_current=False):
        return full_replay(self.path, self.repository, self.executable_repo, self.pins, require_current=require_current)
