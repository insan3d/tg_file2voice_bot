ARG ALPINE_VERSION="3.19"
ARG PYTHON_VERSION="3.12"

FROM python:${PYTHON_VERSION}-alpine${ALPINE_VERSION} as tg_file2voice_bot

RUN apk add --no-cache ffmpeg

COPY ./requirements.txt /tmp/requirements.txt

RUN python3 -m venv --without-pip /opt/venv

RUN python3 -m pip install \
        --no-cache-dir --progress-bar=off --root-user-action=ignore \
        --target "$(find /opt/venv -name site-packages)" \
        -r /tmp/requirements.txt \
 \
 && rm -v /tmp/requirements.txt

COPY ./tg_file2voice_bot.py /opt/tg_file2voice_bot.py

CMD [ "/opt/venv/bin/python3", "/opt/tg_file2voice_bot.py"]
