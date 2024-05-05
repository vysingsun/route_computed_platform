FROM python:3.6.6-stretch
ENV PYTHONUNBUFFERED 1
RUN mkdir /src
WORKDIR /src
RUN apt-get update
RUN curl -sL https://deb.nodesource.com/setup_8.x | bash -
RUN apt-get install -y nodejs
RUN apt-get install -y clamav
ADD config/requirements.txt /src/
RUN apt-get install -y redis-server
RUN pip install -r requirements.txt

