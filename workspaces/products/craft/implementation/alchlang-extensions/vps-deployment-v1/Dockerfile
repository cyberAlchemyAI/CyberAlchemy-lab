FROM ubuntu@sha256:33ceb71981b602c1a7443a53469e4dba065f7503eab3078a2d7a57a2ab987517
ENV DEBIAN_FRONTEND=noninteractive PYTHONDONTWRITEBYTECODE=1
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-jsonschema ansible-core bubblewrap gcc libc6-dev ca-certificates util-linux && rm -rf /var/lib/apt/lists/*
RUN groupadd -g 10001 alch && useradd -u 10001 -g 10001 -m alch && mkdir -p /var/lib/alch/registry && chown -R 10001:10001 /var/lib/alch
COPY rootfs/ /
RUN chmod -R a+rX /home/vrondelli /opt/alch && chmod 1777 /tmp
USER 10001:10001
EXPOSE 8081
ENTRYPOINT ["/usr/bin/python3","/opt/alch/start.py"]
