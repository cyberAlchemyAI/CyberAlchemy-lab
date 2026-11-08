# Repeated local Docker setup check

`verify.py` runs the pinned disposable local product twice, capturing each
terminal log and a before/after Docker and temporary-build-context inventory.
It requires both Source→Reader→Mapper→Context and Work journeys to finish, all
preexisting containers/volumes/scoped images and build contexts to survive, and
no new container/volume/scoped image/build context to remain. Its result is
`RESULT.json`; this does not activate protected Source8 or a live Lab service.
`cold_verify.py` separately rehashes both retained logs, requires each exact
journey marker once, checks cleanup/replay messages and the full before/after
object inventory, and rehashes the selected launcher.
