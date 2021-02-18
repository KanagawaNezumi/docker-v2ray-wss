使用方法:

1. 将域名解析到远程主机, 下文以`www.example.com`为例.
2. 执行如下命令

```bash
docker run \
    --restart=always \
    --name v2ray-wss \
    -p 80:80 \
    -p 443:443 \
    -e DOMAIN=www.example.com \
    kanagawanezumi/v2ray-wss
```


运行时会自动打印客户端配置, 复制完毕后, 断开命令行即可.

---

可用环境参数(域名必需, 其余均包含默认值):

- DOMAIN: 解析到远程主机的域名
- UID: 即 uuid 格式的 id, 默认值为随机生成的 uuid.
- ACCESS: 访问域名时, 可以穿透 nginx 到达 v2ray 的路径, 默认 v2ray.
- URL: 作为伪装首页的url, 设为 none 时无伪装页, 默认为 github 的趋势页
- EMAIL: 使用certbot申请证书时的邮箱, 默认 example@gmail.com.


---

可能用到的其他信息:

- nginx 的 root 路径为容器内的 `/usr/share/nginx/html`.
- 证书路径为 `/etc/letsencrypt/live/$domain/fullchain.pem`
- 私钥路径为 `/etc/letsencrypt/live/$domain/privkey.pem`

可以自行映射伪装页, 但注意此时环境参数URL必须设为none, 否则在启动时被重写.

可以映射证书, 检测证书存在后不会重新申请, let's encrypt 对证书的申请有频率限制.

---

如果容器内 v2ray 版本过旧, 重新构建镜像即可.

```
git clone https://github.com/KanagawaNezumi/docker-v2ray-wss.git
cd docker-v2ray-wss
docker build -t kanagawanezumi/v2ray-wss .
```

---

附: 开启谷歌 BBR 加速的命令:

```bash
wget --no-check-certificate https://github.com/teddysun/across/raw/master/bbr.sh && chmod +x bbr.sh && ./bbr.sh
```

---

注: v2ray + nginx + websocket + tls 方案, 需要与远程主机间有高质量的网络连接, 若有丢包现象, 请使用 mkcp 方案.


