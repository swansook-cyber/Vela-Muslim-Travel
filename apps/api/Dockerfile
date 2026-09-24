FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml ./
COPY app ./app
COPY migrations ./migrations

RUN python -m pip install --no-cache-dir .

EXPOSE 8000

CMD ["sh", "-c", "python -m app.migrations && exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers"]
