FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        samba samba-common-bin \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /app /srv/samba/records

WORKDIR /app
COPY notice.py app.py entrypoint.sh smb.conf ./
COPY templates ./templates
COPY static ./static
COPY files/README.txt files/yard-ledger.txt /srv/samba/records/
RUN chmod 755 /srv/samba /srv/samba/records \
    && chmod 444 /srv/samba/records/README.txt /srv/samba/records/yard-ledger.txt \
    && chmod +x /app/entrypoint.sh \
    && cp /app/smb.conf /etc/samba/smb.conf

EXPOSE 80 139 445

HEALTHCHECK --interval=2s --timeout=2s --retries=20 --start-period=8s \
  CMD ["python3", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1/healthz', timeout=2).read()"]

CMD ["/app/entrypoint.sh"]
