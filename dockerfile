FROM certbot/certbot
WORKDIR /v2ray-wss
COPY . .
RUN python build.py
ENTRYPOINT python run.py