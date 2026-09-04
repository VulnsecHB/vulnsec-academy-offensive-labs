FROM python:3.13-slim
RUN apt-get update && apt-get install -y --no-install-recommends openssh-server \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /run/sshd
COPY sshd_config /etc/ssh/sshd_config
COPY banner /etc/ssh/banner
COPY setup-user.sh entrypoint.sh /usr/local/sbin/
RUN chmod +x /usr/local/sbin/setup-user.sh /usr/local/sbin/entrypoint.sh \
    && /usr/local/sbin/setup-user.sh \
    && rm -f /usr/local/sbin/setup-user.sh
EXPOSE 22
HEALTHCHECK --interval=2s --timeout=2s --retries=20 --start-period=6s \
  CMD python3 -c "import socket; s=socket.create_connection(('127.0.0.1',22),2); s.close()"
CMD ["/usr/local/sbin/entrypoint.sh"]
