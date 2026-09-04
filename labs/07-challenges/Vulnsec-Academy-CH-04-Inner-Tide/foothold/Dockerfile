FROM python:3.13-slim
RUN apt-get update && apt-get install -y --no-install-recommends openssh-server iproute2 \
    && rm -rf /var/lib/apt/lists/* && mkdir -p /app /run/sshd
WORKDIR /app
COPY app.py entrypoint.sh setup.sh sshd_config ./
COPY templates ./templates
COPY static ./static
RUN chmod +x entrypoint.sh setup.sh && ./setup.sh
EXPOSE 22 80
HEALTHCHECK --interval=2s --timeout=2s --retries=20 --start-period=8s \
  CMD ["python3", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1/healthz', timeout=2).read()"]
CMD ["/app/entrypoint.sh"]
