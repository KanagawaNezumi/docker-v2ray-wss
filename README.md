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

运行时会自动打印相关信息及客户端配置, 复制完毕后, 断开命令行即可.

---

当容器启动时, 映射`80`端口用以申请和更新 ssl 证书, `443`端口运行 wss 服务, 确保端口可用且开放.
为了方便起见, 项目运行成功后, 可根据通过浏览器在域名的`/files`路径下找到`v2ray`常用可执行文件下载, 包括`windows64`版本, `macos64`版本, `linux64`版本, 以及 `V2RayNG` 的 `APK`.
如果之后想要查看初始化时生成的客户端配置, 执行 `docker exec -it v2ray-wss cat /v2ray/user.config.json`.

---

可用环境参数(域名必需, 其余均包含默认值):

- `DOMAIN`: 解析到远程主机的域名.
- `UID`: 即 uuid 格式的 id, 默认值为随机生成的 uuid.
- `ACCESS`: 访问域名时, 可以穿透 nginx 到达 v2ray 的路径, 默认为随机生成的路径.
- `HOMEPAGE`: 将被下载其内容作为首页的url, 默认为 github 的 trending 页.
- `EMAIL`: 使用certbot申请证书时的邮箱, 默认为 fake@gmail.com.

---

可能用到的其他信息:

- nginx 的 root 路径为`/usr/share/nginx/html` (容器内路径, 以下均是)
- 证书路径为 `/etc/letsencrypt/live/$domain/fullchain.pem`
- 私钥路径为 `/etc/letsencrypt/live/$domain/privkey.pem`
- 证书链路径为 `/etc/letsencrypt/live/$domain/chain.pem`

可以自行映射证书(证书, 私钥, 证书链), 检测以上均存在后不会重新申请, let's encrypt 对证书的申请有频率限制.

---

dockerhub 中镜像一般随源码更新(README更新除外), 如有必要可以自行构建镜像:

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

注: v2ray + nginx + websocket + tls 方案, 需要本机与远程主机间有高质量的网络连接, 若有丢包现象, 可以考虑 mkcp 方案.
