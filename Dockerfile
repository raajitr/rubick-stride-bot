FROM python:2.7
COPY requirements.txt /
RUN pip install -r /requirements.txt
COPY / ./app
WORKDIR /
USER nobody

ENTRYPOINT ["python", "/app/main.py"]
CMD gunicorn --log-file=- --bind 0.0.0.0:$PORT wsgi
