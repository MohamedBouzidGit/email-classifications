FROM python:3.8.0-slim

WORKDIR /app

ADD . /app

RUN pip install --trusted-host https://pypi.org/ -r requirements.txt

EXPOSE 5000

ENV NAME OpentoAll

CMD ["python","app.py"]
