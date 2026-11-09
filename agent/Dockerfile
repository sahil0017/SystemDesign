FROM python:3.12-slim

# Install GitHub CLI and required system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
        | dd of=/etc/apt/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
        > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update && apt-get install -y --no-install-recommends gh \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY agent/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY agent/ .

# Clone the repository at startup (mounted via volume in production)
COPY .. /repo

# Environment variables
ENV REPO_PATH=/repo
ENV PYTHONUNBUFFERED=1
ENV CACHE_DIR=/tmp/agent-cache
ENV RUN_HISTORY_FILE=/tmp/agent-cache/run_history.json
ENV HEALTH_CHECK_PORT=8080

# Create cache directory
RUN mkdir -p /tmp/agent-cache

# Expose health check port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["python", "scheduler.py"]
