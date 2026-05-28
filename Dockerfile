FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /restaurant_site

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./restaurant_site /restaurant_site

ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=restaurant_site.settings \
    DJANGO_SECRET_KEY=build-time-only-not-for-runtime

RUN python manage.py collectstatic --noinput

# Heroku sets PORT at runtime (default 8000 for local Docker).
CMD gunicorn restaurant_site.wsgi:application --bind "0.0.0.0:${PORT:-8000}"
