FROM ubuntu:18.04

MAINTAINER k0lm4ch "sanand.sivadas@gmail.com"

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

COPY ./requirements.txt /requirements.txt

WORKDIR /

RUN pip3 install -r requirements.txt

COPY . /

ENV url=http://localhost/
ENV hitrate=10
ENV duration=1

ENTRYPOINT [ "python3" ]

CMD [ "rate_test_api.py" ]