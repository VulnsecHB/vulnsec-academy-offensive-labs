FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        openssh-server samba samba-common-bin vsftpd sudo tar \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /app /run/sshd /srv/ftp /srv/samba/public /srv/samba/scans /srv/samba/hr-archive

WORKDIR /app
COPY app.py entrypoint.sh setup.sh sshd_config smb.conf vsftpd.conf banner ./
COPY templates ./templates
COPY static ./static
COPY files/ftp/ /srv/ftp/
COPY files/smb/public/ /srv/samba/public/
COPY files/smb/scans/ /srv/samba/scans/
COPY files/smb/hr-archive/ /srv/samba/hr-archive/
RUN chmod +x /app/entrypoint.sh /app/setup.sh \
    && /app/setup.sh \
    && chmod -R a+rX /srv/ftp /srv/samba

EXPOSE 21 22 80 139 445 30000-30009

HEALTHCHECK --interval=2s --timeout=2s --retries=20 --start-period=10s \
  CMD ["python3", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1/healthz', timeout=2).read()"]

CMD ["/app/entrypoint.sh"]
