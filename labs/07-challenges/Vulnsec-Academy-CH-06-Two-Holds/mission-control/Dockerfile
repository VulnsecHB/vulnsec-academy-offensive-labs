FROM python:3.13-alpine
RUN addgroup -S atlas && adduser -S -D -H -G atlas atlas
WORKDIR /app
COPY --chown=atlas:atlas app.py index.html ./
COPY --chown=atlas:atlas static ./static
USER atlas
EXPOSE 8888
CMD ["python", "app.py"]
