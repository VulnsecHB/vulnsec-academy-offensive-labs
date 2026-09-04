FROM python:3.13-alpine

WORKDIR /app
COPY catalog.py app.py ./
COPY templates ./templates
COPY static ./static

EXPOSE 80

HEALTHCHECK --interval=2s --timeout=2s --retries=15 --start-period=2s \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1/healthz', timeout=2).read()"]

CMD ["python", "app.py"]
