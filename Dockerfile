FROM python:3.8.5

LABEL maintainer="Evgeny Perchun <evgeny_perchun@mail.ru>"

WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . .

ENTRYPOINT [ "executable" ]
CMD gunicorn api_yamdb.wsgi:application --bind 0.0.0.0:8000