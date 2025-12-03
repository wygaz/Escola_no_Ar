web: sh -c "python manage.py collectstatic --noinput && gunicorn escola_no_ar_site.wsgi:application --bind 0.0.0.0:$PORT"
