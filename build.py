import os
import requests
import zipfile
import time
import stat
import functools

V2RAY_VERSION = '4.44.0'
V2RAYGN_VERSION = '1.6.28'

NGINX_FILE_DIR = '/usr/share/nginx/files/'
V2RAY_BINARY_DIR = '/v2ray'

print = functools.partial(print, flush=True)

def _http_downlaod(url: str, filepath: str, session: requests.Session = None) -> str:
    with session or requests.Session() as session:
        with session.get(url, stream=True) as resp:
            with open(filepath, 'wb+') as f:
                size = int(resp.headers.get('Content-Length'))
                for chunk in resp.iter_content(chunk_size=8192):
                    chunk and f.write(chunk)
    return size

def _set_file_index() -> None:
    with open('static/file.html', 'r', encoding='utf-8') as ff:
        with open(os.path.join(NGINX_FILE_DIR, 'index.html'), 'w+') as ft:
            _text = ff.read()
            _text = _text.replace('$v2ray_version', V2RAY_VERSION)
            text = _text.replace('$v2rayng_version', V2RAYGN_VERSION)
            ft.write(text)

def _convert_size(size: int) -> str:
    return f'{round(size/1024/1024, 1)}MB'

def _collect_v2ray_binary(local:str = NGINX_FILE_DIR) -> None:
    v2ray_tmpl = 'https://github.com/v2fly/v2ray-core/releases/download/v{}/v2ray-{}-64.zip'
    with requests.Session() as session:
        for plat in ('windows', 'macos', 'linux'):
            url = v2ray_tmpl.format(V2RAY_VERSION, plat)
            print(f'Downloading {plat} binary...', end='')
            size = _http_downlaod(url, filepath:= local + os.path.basename(url), session)
            print(f'done({_convert_size(size)}).')
            if plat == 'linux':
                with zipfile.ZipFile(filepath, 'r') as zip:
                    zip.extractall(V2RAY_BINARY_DIR)
                    os.chmod(os.path.join(V2RAY_BINARY_DIR, 'v2ray'), stat.S_IXUSR)
        v2rayng_tmpl = 'https://github.com/2dust/v2rayNG/releases/download/{0}/v2rayNG_{0}.apk'
        v2rayng_url = v2rayng_tmpl.format(V2RAYGN_VERSION)
        print('Downloading V2rayNG APK...', end='')
        size = _http_downlaod(v2rayng_url, local + os.path.basename(v2rayng_url), session)
        print(f'.done({_convert_size(size)}).')

def main():
    if os.system('apk add nginx'):
        raise Exception('Failed to install nginx... exit.')
    os.makedirs(NGINX_FILE_DIR, exist_ok=True)
    os.makedirs(V2RAY_BINARY_DIR, exist_ok=True)
    os.makedirs('/run/nginx/', exist_ok=True)
    _collect_v2ray_binary()
    _set_file_index()

if __name__ == '__main__':
    main()