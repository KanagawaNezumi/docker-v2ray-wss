#!/bin/sh

domain=$1 ; access=$2 ; email=$3 ; uid=$4; url=$5

[[ ! $domain ]] && echo "你必须拥有一个解析至当前主机的域名" && exit 1
[[ ! $access ]] && access=v2ray
[[ ! $url ]] && url=https://github.com/trending
[[ ! $email ]] && email=example@gmail.com

if [[ ! $uid ]]; then
    # 当用户未传入UID变量时, 生成随机uuid并保存
    if [[ ! -e /v2ray-uid ]]; then
        uid=`uuidgen`
        echo $uid > /v2ray-uid
    else
        uid=`cat /v2ray-uid`
    fi
fi

echo "domain: $domain\n path: $access\n email: $email\n id: $uid"

# 设置公钥私钥路径
publickey="/etc/letsencrypt/live/$domain/fullchain.pem"
priviatekey="/etc/letsencrypt/live/$domain/privkey.pem"

is_certed(){
    if [[ -e $publickey && -e $priviatekey ]]; then 
        certed="true"
    else
        certed=""
    fi
}

# 检测证书文件是否存在
is_certed

if [[ $certed ]]; then
    echo 证书文件: $publickey && echo 私钥文件: $priviatekey
else 
    # 无证书, 使用cetbot申请证书
    certbot certonly --standalone --domain $domain --agree-tos -n --email $email
fi

# 再次检测证书
is_certed

if [[ $certed ]]; then
    # 映射证书, 重启容器, 或申请证书, 此时均应持有证书, 若无, 退出

    # 首先检查标志, 确认是否是初次运行容器
    if [[ ! -e /KanagawaNezumi.flag ]]; then
        
        # 初次运行, 执行文件替换
        mv ./nginx.conf /etc/nginx/nginx.conf
        mv ./v2ray-wss-config.json /etc/v2ray/config.json
        mv ./v2ray-wss-cli-config.json /etc/v2ray/v2ray-wss-cli-config.json

        # 使用sed命令将其中的变量替换真正的域名和路径
        sed -i -e "s/\$access/$access/g" -e "s/\$domain/$domain/g" /etc/nginx/nginx.conf

        # 获得伪装页, 并替换为默认首页index.html
        if [[ $url != "none" ]];then
            wget -q $url -O /usr/share/nginx/html/index.html 
        fi

        # 修改v2ray配置, 包括替换服务端配置, 并替换生成客户端推荐配置
        sed -i -e "s/\$uid/$uid/g" -e "s/\$access/$access/g" /etc/v2ray/config.json # 重写 id和path
        sed -i -e "s/\$uid/$uid/g" -e "s/\$access/$access/g" -e "s/\$domain/$domain/g" /etc/v2ray/v2ray-wss-cli-config.json

        echo -e "你的域名: $domain\n你的路径: $access\n你的id: $uid\n推荐安卓客户端: Kitsunebi\n推荐的客户端配置(通用):"
        echo -e "#======================================================================================#"
        cat /etc/v2ray/v2ray-wss-cli-config.json
        echo -e "#======================================================================================#\n"
        # 设置一个标志, 代表配置已重写, 下次重启容器可以直接运行v2ray和nginx
        echo "surfing" > /KanagawaNezumi.flag
    fi

else
    echo " 当前域名$domain 无本地证书, 且证书申请失败" && exit 1
fi

echo "启动v2ray主程序和nginx进程"
nohup /usr/bin/v2ray -config /etc/v2ray/config.json &
nginx -g "daemon off;"
