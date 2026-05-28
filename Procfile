web: cd restaurant_site && gunicorn restaurant_site.wsgi:application --bind 0.0.0.0:$PORT
release: cd restaurant_site && python manage.py migrate --noinput
