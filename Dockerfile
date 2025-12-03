# -----------------------------
# Stage 1: Builder
# -----------------------------
FROM python:3.11-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --prefix=/install -r requirements.txt \
    && rm -rf /root/.cache/pip

# -----------------------------
# Stage 2: Runtime
# -----------------------------
FROM python:3.11-slim
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
WORKDIR /app

# runtime tools
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    cron tzdata \
    && rm -rf /var/lib/apt/lists/*

# copy python packages from builder
COPY --from=builder /install /usr/local

# copy application code
COPY . /app

# make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# install cron jobs
RUN if [ -f /app/cron/cronfile ]; then \
      chmod 0644 /app/cron/cronfile; \
      crontab /app/cron/cronfile; \
    fi && \
    if [ -f /app/cron/2fa-cron ]; then \
      chmod 0644 /app/cron/2fa-cron; \
      crontab -l | cat - /app/cron/2fa-cron | crontab -; \
    fi

# install cronfile if present
RUN if [ -f /app/cron/cronfile ]; then \
      chmod 0644 /app/cron/cronfile && crontab /app/cron/cronfile || true; \
    fi

# install 2fa-cron also
RUN if [ -f /app/cron/2fa-cron ]; then \
      chmod 0644 /app/cron/2fa-cron && crontab -l | cat - /app/cron/2fa-cron | crontab - ; \
    fi


# create volume mount points
RUN mkdir -p /data /cron && chmod 755 /data /cron

EXPOSE 8080
ENTRYPOINT ["/app/entrypoint.sh"]

