FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY prompts ./prompts
COPY static ./static
COPY main.py ./
COPY main_datawarehouse.db ./main_datawarehouse.db

RUN useradd --create-home appuser

USER appuser

EXPOSE 8000

CMD ["sh", "-c", "exec python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
