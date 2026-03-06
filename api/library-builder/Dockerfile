FROM python:3.11-slim

WORKDIR /workspace

# install node (for get-graphql-schema)
RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*

# graphql schema downloader
RUN npm install -g get-graphql-schema

FROM python:3.11-slim

# Install curl
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir ariadne-codegen

COPY generate-client.sh /generate-client.sh
RUN chmod +x /generate-client.sh

#ENTRYPOINT ["/generate-client.sh"]
CMD ["bash"]
