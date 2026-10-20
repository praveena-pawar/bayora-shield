FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN groupadd --system bayora \
    && useradd --system --gid bayora --create-home bayora

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY security/ ./security/
COPY evaluator/ ./evaluator/

RUN mkdir -p /app/data \
    && chown -R bayora:bayora /app

USER bayora

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]