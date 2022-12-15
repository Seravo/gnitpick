FROM debian:11-slim

RUN set -eux \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
      ca-certificates \
      curl \
      git \
      python3-minimal \
    && rm -rf /var/lib/apt/lists/* \
      /var/cache/debconf/* \
    && apt-get clean

COPY gnitpick.py /usr/bin/gnitpick

RUN chmod +x /usr/bin/gnitpick

CMD ["/usr/bin/gnitpick"]
