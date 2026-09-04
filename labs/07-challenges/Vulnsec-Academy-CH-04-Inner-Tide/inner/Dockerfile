FROM python:3.13-slim
WORKDIR /app
COPY app.py ./
COPY templates ./templates
COPY static ./static
EXPOSE 80
HEALTHCHECK --interval=2s --timeout=2s --retries=20 --start-period=4s \
  CMD ["python3", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1/healthz', timeout=2).read()"]
CMD ["python3", "/app/app.py"]
