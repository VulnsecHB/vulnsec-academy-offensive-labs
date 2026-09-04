FROM python:3.13-slim
RUN apt-get update && apt-get install -y --no-install-recommends samba samba-common-bin \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /app /srv/samba/public /srv/samba/print /srv/samba/archive
WORKDIR /app
COPY smb.conf entrypoint.sh ./
COPY files/public/ /srv/samba/public/
COPY files/print/ /srv/samba/print/
COPY files/archive/ /srv/samba/archive/
COPY keys/id_rsa /srv/samba/archive/id_rsa
RUN chmod +x entrypoint.sh && chmod -R a+rX /srv/samba
EXPOSE 139 445
HEALTHCHECK --interval=2s --timeout=2s --retries=20 --start-period=8s \
  CMD ["python3", "-c", "import socket; s=socket.create_connection(('127.0.0.1',445),2); s.close()"]
CMD ["/app/entrypoint.sh"]
