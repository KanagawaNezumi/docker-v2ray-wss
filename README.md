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

(新特性: 可在域名的`/files`路径下找到对应版本的`v2ray`可执行文件, 包括windows64版本, macos64版本, 以及linux64版本)

---

可用环境参数(域名必需, 其余均包含默认值):

- DOMAIN: 解析到远程主机的域名.
- UID: 即 uuid 格式的 id, 默认值为随机生成的 uuid.
- ACCESS: 访问域名时, 可以穿透 nginx 到达 v2ray 的路径, 默认 v2ray.
- URL: 将被下载其内容作为首页的url, 设为 none 时不下载, 默认为 github 的 trending 页.
- EMAIL: 使用certbot申请证书时的邮箱, 默认为 example@gmail.com, 该邮箱用以接收来自 letsencrypt 的通知.

---

可能用到的其他信息:

- nginx 的 root 路径为`/usr/share/nginx/html` (容器内路径, 以下均是)
- 证书路径为 `/etc/letsencrypt/live/$domain/fullchain.pem`
- 私钥路径为 `/etc/letsencrypt/live/$domain/privkey.pem`
- 证书链路径为 `/etc/letsencrypt/live/$domain/chain.pem`

可以自行映射伪装页, 但注意此时环境参数URL需要设为none, 即`-e URL=none`, 否则在启动时被重写.

可以自行映射证书(证书, 私钥, 证书链), 检测证书存在后不会重新申请, let's encrypt 对证书的申请有频率限制. 

自行映射证书时, 如果容器内缺乏更新相关文件会导致自动更新证书失败, 请自行维护证书的有效期.

映射`80`端口用以申请和更新 ssl 证书, `443`端口运行 wss 服务, 确保端口可被访问.

任何时候需要再次查看生成的客户端配置, 执行命令: `docker exec -it v2ray-wss cat /etc/v2ray/v2ray-wss-cli-config.json`

---

如果容器内 v2ray 版本过旧, 重新构建镜像即可.

```bash
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

注: v2ray + nginx + websocket + tls 方案, 需要本机与远程主机间有高质量的网络连接, 若有丢包现象, 请使用 [mkcp 方案](https://github.com/KanagawaNezumi/docker-v2ray-mkcp).
