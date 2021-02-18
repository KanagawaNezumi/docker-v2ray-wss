FROM certbot/certbot
ENV DOMAIN=www.example.com EMAIL=example@gmail.com ACCESS=v2ray UID="" URL=""
RUN cat /etc/issue
WORKDIR /v2ray-wss
COPY . .
RUN apk add nginx wget util-linux \
    && mkdir -p /run/nginx /etc/v2ray /usr/local/share/v2ray /var/log/v2ray \
    && chmod +x ./v2ray.sh \
    && ./v2ray.sh
COPY . .
RUN chmod +x ./v2ray-wss-entrypoint.sh 
ENTRYPOINT ./v2ray-wss-entrypoint.sh $DOMAIN $ACCESS $EMAIL $UID $URL