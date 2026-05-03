FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /restaurant_site

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./restaurant_site /restaurant_site

ENV PYTHONUNBUFFERED=1

RUN python manage.py collectstatic --noinput || true

CMD ["gunicorn", "restaurant.wsgi:application", "--bind", "0.0.0.0:8000"]