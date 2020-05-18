FROM python:3.7.5-slim-buster
MAINTAINER Rose Jones <beatthemarket@abine.org>

RUN apt-get update && apt-get install -qq -y \
  build-essential libpq-dev --no-install-recommends

ENV INSTALL_PATH /beatthemarket
RUN mkdir -p $INSTALL_PATH
WORKDIR ${INSTALL_PATH}

COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install --editable .

CMD gunicorn --bind 0.0.0.0:$PORT wsgi --config "python:config.gunicorn" "beatthemarket.run_app:app"
