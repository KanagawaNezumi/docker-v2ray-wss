#!/bin/sh

domain=$1 ; access=$2 ; email=$3 ; uid=$4; url=$5

[[ ! $domain ]] && echo "你必须拥有一个解析至当前主机的域名" && exit 1
[[ ! $access ]] && access=v2ray
[[ ! $url ]] && url=https://github.com/trending
[[ ! $email ]] && email=example@gmail.com

echo -e "domain: $domain\npath: $access\nemail: $email\nid: $uid"

# 下载伪装页, 并尽量使其链接可访问
if [[ $url != "none" ]];then
    if [[ ! -e /KanagawaNezumi.flag ]]; then
        echo "下载伪装页, 并尝试补全链接..."
    else
        echo "刷新伪装页, 并尝试补全链接..."
    fi
    mkdir -p /usr/share/nginx/html
    wget $url -nv -O /usr/share/nginx/html/index.html && python repair_link.py $url
fi

# 公钥, 私钥, 证书链路径
publickey="/etc/letsencrypt/live/$domain/fullchain.pem"
priviatekey="/etc/letsencrypt/live/$domain/privkey.pem"
chain="/etc/letsencrypt/live/$domain/chain.pem"

if [[ -e $publickey && -e $priviatekey && -e $chain ]]; then
    echo 证书: $publickey && echo 私钥: $priviatekey && echo 证书链: $chain
else 
    certbot certonly --standalone --domain $domain --agree-tos -n --email $email
fi

if [[ -e $publickey && -e $priviatekey && -e $chain ]]; then
    # 映射证书, 重启容器, 或申请证书, 此时均应持有证书
    
    # 首先检查标志, 确认是否是初次运行容器
    if [[ ! -e /KanagawaNezumi.flag ]]; then
        # 生成随机uuid
        [[ ! $uid ]] && uid=`uuidgen`
        # 移动配置
        mv ./nginx.conf /etc/nginx/nginx.conf
        mv ./v2ray-wss-config.json /etc/v2ray/config.json
        mv ./v2ray-wss-cli-config.json /etc/v2ray/v2ray-wss-cli-config.json
        # 进行 nginx 设置
        sed -i -e "s/\$access/$access/g" -e "s/\$domain/$domain/g" /etc/nginx/nginx.conf
        # 进行 v2ray 服务端设置
        sed -i -e "s/\$uid/$uid/g" -e "s/\$access/$access/g" /etc/v2ray/config.json # 重写 id和path
        # 进行 v2ray 客户端设置
        sed -i -e "s/\$uid/$uid/g" -e "s/\$access/$access/g" -e "s/\$domain/$domain/g" /etc/v2ray/v2ray-wss-cli-config.json
        # 打印客户端配置
        echo -e "域名: $domain\n路径: $access\nid: $uid\n推荐安卓客户端: Kitsunebi\n生成的客户端配置(通用, 包含路由):"
        echo -e "#======================================================================================#"
        cat /etc/v2ray/v2ray-wss-cli-config.json
        echo -e "#======================================================================================#"
    fi
else
    echo " 当前域名 $domain 无本地证书, 且证书申请失败" && exit 1
fi

if [[ ! -e /KanagawaNezumi.flag ]]; then
    echo "启动 v2ray 主程序, certbot 更新程序, 以及 Nginx 主程序..."
    echo "访问 https://${domain}/files 下载可执行文件"
    echo "surfing" > /KanagawaNezumi.flag
fi
nohup /usr/bin/v2ray -config /etc/v2ray/config.json > v2ray.log &
nohup sh -c "while sleep 86400; do certbot renew; done > renew.log" &
nohup sh -c "while sleep 86400; do nginx -s reload; done > nginx-reload.log" &
nginx -g "daemon off;"