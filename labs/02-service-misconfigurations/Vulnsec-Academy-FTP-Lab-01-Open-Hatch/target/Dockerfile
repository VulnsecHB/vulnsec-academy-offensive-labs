FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        vsftpd \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /app /srv/ftp /var/run/vsftpd/empty

WORKDIR /app
COPY notice.py app.py entrypoint.sh vsftpd.conf ./
COPY templates ./templates
COPY static ./static
COPY files/README.txt files/inbound-manifest.txt /srv/ftp/
RUN chmod 755 /srv/ftp \
    && chmod 444 /srv/ftp/README.txt /srv/ftp/inbound-manifest.txt \
    && chmod +x /app/entrypoint.sh \
    && cp /app/vsftpd.conf /etc/vsftpd.conf

EXPOSE 21 80 30000-30009

HEALTHCHECK --interval=2s --timeout=2s --retries=20 --start-period=8s \
  CMD ["python3", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1/healthz', timeout=2).read()"]

CMD ["/app/entrypoint.sh"]
