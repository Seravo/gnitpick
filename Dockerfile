FROM ghcr.io/seravo/ubuntu:noble

ARG APT_PROXY

RUN sed -i 's/main$/main universe/g' /etc/apt/sources.list && \
    apt-setup && \
    apt-get --assume-yes install \
      git \
      python3 && \
    apt-cleanup

RUN useradd user && \
    mkdir -p /workdir
WORKDIR /workdir

COPY gnitpick.py /usr/local/bin/

USER user

ENTRYPOINT ["/usr/bin/python3", "/usr/local/bin/gnitpick.py"]
CMD ["--verbose"]
