FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        openssh-server sudo bash findutils gawk \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /run/sshd /app

WORKDIR /app
COPY portal.py app.py entrypoint.sh setup-user.sh ./
COPY sshd_config /etc/ssh/sshd_config
COPY banner /etc/ssh/banner
COPY templates ./templates
COPY static ./static
RUN chmod +x /app/entrypoint.sh /app/setup-user.sh \
    && /app/setup-user.sh \
    && rm -f /app/setup-user.sh

EXPOSE 22 80

HEALTHCHECK --interval=2s --timeout=2s --retries=20 --start-period=6s \
  CMD ["python3", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1/healthz', timeout=2).read()"]

CMD ["/app/entrypoint.sh"]
