FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    LOG_FILE=""

RUN useradd --create-home --no-log-init appuser

WORKDIR /app

# Dependencies first, so editing code doesn't rebuild the install layer
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser main.py ./
COPY --chown=appuser:appuser modules ./modules

# Default location for the Krillion database. Mount a volume here to keep
# scores across restarts; without one they last as long as the container.
RUN mkdir -p /app/data && chown appuser:appuser /app/data
VOLUME ["/app/data"]

USER appuser

CMD ["python3", "main.py"]
