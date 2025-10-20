FROM mcr.microsoft.com/playwright/python:v1.55.0-jammy

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    XDG_CACHE_HOME=/tmp/.cache \
    PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x ./entrypoint.sh

CMD ["./entrypoint.sh"]
