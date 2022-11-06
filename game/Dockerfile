FROM python:3.8

ENV WEBAPP_DIR=/game

RUN mkdir $WEBAPP_DIR
WORKDIR $WEBAPP_DIR

ADD requirements.txt $WEBAPP_DIR/
RUN pip install -r requirements.txt