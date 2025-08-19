FROM python:3.13-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN echo "from django.contrib.auth import get_user_model; \
User = get_user_model(); \
username='h04x4'; \
password='qwerty123'; \
email='admin@example.com'; \
if not User.objects.filter(username=username).exists(): \
    User.objects.create_superuser(username=username, email=email, password=password)" \
> create_admin.py

CMD python manage.py migrate --noinput && \
    python manage.py shell < create_admin.py && \
    gunicorn project.wsgi:application --bind 0.0.0.0:8000
