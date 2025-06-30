FROM python:3.13

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY docs/requirements.txt .
RUN pip install -r requirements.txt

COPY . .