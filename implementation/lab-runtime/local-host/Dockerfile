FROM python:3.12.15-slim-bookworm@sha256:57d96f71de145a98e7ceca18ee4ade77bba4103a33a72dfaea026b23625c6bf0

COPY Dockerfile requirements.lock compose.yaml run-local-product.sh /build-inputs/
COPY package-manifest.json /package-manifest.json
COPY workspace/ /workspace/

RUN groupadd --gid 20001 labruntime \
    && useradd --uid 20001 --gid 20001 --no-create-home --home-dir /nonexistent --shell /usr/sbin/nologin labruntime \
    && python -m pip install --no-cache-dir --only-binary=:all: --require-hashes -r /build-inputs/requirements.lock \
    && python -m pip check \
    && chmod 755 /build-inputs/run-local-product.sh

ENV PYTHONDONTWRITEBYTECODE=1 \
    TMPDIR=/tmp

USER 20001:20001
WORKDIR /workspace
CMD ["python", "-B", "implementation/lab-runtime/local-product/run.py"]
