#!/bin/sh

TAG=`wget https://github.com/v2fly/v2ray-core/tags -q -O - | egrep -o "(v[0-9]{1}\.[0-9]{1,2}\.[0-9]{1,2})" | head -n 1`

echo "Downloading binary file: v2ray ${TAG}"

DOWNLOAD_ADDR="https://github.com/v2fly/v2ray-core/releases/download"

mkdir -p /usr/share/nginx/file
wget -nv -O ${PWD}/v2ray.zip ${DOWNLOAD_ADDR}/${TAG}/v2ray-linux-64.zip
wget -nv -O ${PWD}/v2ray.zip.dgst ${DOWNLOAD_ADDR}/${TAG}/v2ray-linux-64.zip.dgst
wget -nv -O /usr/share/nginx/file/v2ray-windows-64-${TAG}.zip ${DOWNLOAD_ADDR}/${TAG}/v2ray-windows-64.zip
wget -nv -O /usr/share/nginx/file/v2ray-macos-64-${TAG}.zip ${DOWNLOAD_ADDR}/${TAG}/v2ray-macos-64.zip
cp v2ray.zip /usr/share/nginx/file/v2ray-linux-64-${TAG}.zip

if [ $? -ne 0 ]; then
    echo "Error: Failed to download binary file: v2ray-${TAG}, try again " && exit 1
fi
echo "Download binary file: v2ray-${TAG} completed"

# Check SHA512
LOCAL=$(openssl dgst -sha512 v2ray.zip | sed 's/([^)]*)//g')
STR=$(cat v2ray.zip.dgst | grep 'SHA512' | head -n1)

if [ "${LOCAL}" = "${STR}" ]; then
    echo " Check passed" && rm -fv v2ray.zip.dgst
else
    echo " Check have not passed yet " && exit 1
fi

echo "Prepare to use"
unzip v2ray.zip && chmod +x v2ray v2ctl
mv v2ray v2ctl /usr/bin/
mv geosite.dat geoip.dat /usr/local/share/v2ray/
mv config.json /etc/v2ray/config.json
sed -i -e "s/version/${TAG}/g" ${PWD}/file.html
mv file.html /usr/share/nginx/file/index.html
echo "Done"