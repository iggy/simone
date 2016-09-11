FROM alpine:edge

ENV PYTHONUNBUFFERED 1

# sqlite3 is for dbshell to work in the example
RUN apk update && apk add python3 py3-cffi py3-openssl py3-cryptography ca-certificates sqlite

# Requirements have to be pulled and installed here, otherwise caching won't work
COPY ./requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt

RUN addgroup -S django \
    && adduser -S -G django django

COPY . /app
WORKDIR /app/example
RUN pwd
RUN chown -R django /app \
    && pip3 install -r requirements.txt \
    && python3 manage.py makemigrations \
    && python3 manage.py migrate \
    && python3 manage.py makemigrations simone \
    && python3 manage.py migrate simone

EXPOSE 8000

ENTRYPOINT ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
