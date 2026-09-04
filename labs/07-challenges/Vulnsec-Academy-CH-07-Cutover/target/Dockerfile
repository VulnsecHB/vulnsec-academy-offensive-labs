FROM python:3.13-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
        openssh-server samba samba-common-bin vsftpd libcap2-bin iproute2 \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /app /run/sshd
WORKDIR /app
COPY app.py entrypoint.sh setup.sh sshd_config smb.conf vsftpd.conf ./
COPY templates ./templates
COPY static ./static
COPY ops ./ops
COPY keys ./keys
COPY ftp ./ftp
COPY smb ./smb
RUN chmod +x entrypoint.sh setup.sh && ./setup.sh
EXPOSE 21 22 80 445 30000-30009
HEALTHCHECK --interval=2s --timeout=2s --retries=20 --start-period=12s \
  CMD ["python3", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1/healthz', timeout=2).read()"]
CMD ["/app/entrypoint.sh"]
