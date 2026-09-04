FROM python:3.13-slim
RUN apt-get update && apt-get install -y --no-install-recommends openssh-server sudo zip \
    && rm -rf /var/lib/apt/lists/* && mkdir -p /app /run/sshd
WORKDIR /app
COPY sshd_config entrypoint.sh setup.sh ./
COPY keys ./keys
RUN chmod +x entrypoint.sh setup.sh && ./setup.sh
EXPOSE 22
HEALTHCHECK --interval=2s --timeout=2s --retries=20 --start-period=8s \
  CMD ["python3", "-c", "import socket; s=socket.create_connection(('127.0.0.1',22),2); s.close()"]
CMD ["/app/entrypoint.sh"]
