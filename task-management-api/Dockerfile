FROM python:3.12-slim
WORKDIR /app
COPY requirements-runtime-lock.txt .
RUN pip install --no-cache-dir -r requirements-runtime-lock.txt && useradd --uid 10001 --create-home appuser && mkdir /data && chown appuser /data
COPY app.py .
ENV DATABASE_PATH=/data/tasks.db
USER 10001
EXPOSE 8080
HEALTHCHECK --interval=15s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/ready', timeout=2)"
CMD ["waitress-serve", "--host=0.0.0.0", "--port=8080", "--call", "app:create_app"]
