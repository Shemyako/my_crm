FROM python:3.10-slim

COPY requirements.txt /app/requirements.txt
WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV TZ=Europe/Moscow

COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh


RUN apt update && apt install -y --no-install-recommends git \
    && pip3 install --no-cache-dir -r /app/requirements.txt \
    && apt autoremove -y \
    && apt clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY . /app

ENTRYPOINT [ "/usr/local/bin/entrypoint.sh" ]
