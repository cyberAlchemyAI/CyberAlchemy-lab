from . import protocol as P, artifact_model as M, handlers as H, guard as G, workspace as W
SOURCE = None
PROFILE = None
def guard():
    G.verify(SOURCE)
    return P.Schemas(PROFILE)
