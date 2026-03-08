FROM jenkins/inbound-agent:latest-jdk21

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
      curl \
      git \
      jq \
      make \
      python3 \
      python3-pip \
      python3-venv \
    && rm -rf /var/lib/apt/lists/*

USER jenkins
COPY start-agent.sh /usr/local/bin/start-agent.sh
ENTRYPOINT ["/usr/local/bin/start-agent.sh"]
