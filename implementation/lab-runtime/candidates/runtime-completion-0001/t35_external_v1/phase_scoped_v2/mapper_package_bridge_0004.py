"""Fixed builder overlay. Only an explicitly fixture-only fd3 client is installed."""
from .mapper_package_client_0004 import Client, Refusal

_CLIENT=None


def install(client):
    global _CLIENT
    if type(client) is not Client or _CLIENT is not None:
        raise Refusal('ONE_FIXED_CLIENT')
    _CLIENT=client


def selected():
    if type(_CLIENT) is not Client:
        raise Refusal('NO_FIXED_CLIENT')
    return _CLIENT


def package_begin(pin,out):return selected().begin(pin,out)
def package_emit(leaf,raw):return selected().emit(leaf,raw)
def package_seal(raw):return selected().seal(raw)
def package_cold_read(args):return selected().cold(args)
def package_finish(binding):return selected().finish(binding)


def run_native(*args,**kwargs):raise Refusal('NO_NATIVE_EXECUTOR')
def read(*args,**kwargs):raise Refusal('NO_PROTECTED_READER')
def verify_inputs(*args,**kwargs):raise Refusal('NO_PROTECTED_READER')
