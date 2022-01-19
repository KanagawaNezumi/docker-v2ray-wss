import uuid
import random
import os
import requests
from collections import namedtuple
import string
import re
import urllib.parse
from functools import partial
from build import V2RAY_BINARY_DIR
import json

HOMEPAGE_URL = 'https://github.com/trending'
HOMEPATE_PATH = '/usr/share/nginx/html/index.html'
CERT_PATH = '/etc/letsencrypt/live/%s/fullchain.pem'
PRIVIATE_KEY_PATH = '/etc/letsencrypt/live/%s/privkey.pem'
CHAIN_PATH = '/etc/letsencrypt/live/%s/chain.pem'
CERT_RENEW_LOG_PATH = '/var/log/letsencrypt/%s/renew.log'
V2RAY_CONFIG_PATH = V2RAY_BINARY_DIR + '/config.json' 
V2RAY_USER_CONFIG_PATH = V2RAY_BINARY_DIR + '/user.config.json'
V2RAY_INITIALIZE_LOG_PATH = '/var/log/v2ray/initialize.log'
NGINX_CONFIG_PATH = '/etc/nginx/nginx.conf'
INITIAL_TAG_PATH = '/Kanagawanezumi'

print = partial(print, flush=True)

def _is_initial_run() -> bool:
    return not os.path.exists(INITIAL_TAG_PATH)

def _gen_divider() -> None:
    print('-' * 70)

def _gen_rand_path(length: int = 36) -> str:
    chars = '_-_-_-'.join([
        string.ascii_lowercase,
        string.ascii_uppercase,
        string.digits,
    ])
    gen_index = lambda: random.randint(0, len(chars)-1)
    return ''.join([chars[i] for i in [gen_index() for _ in range(length)]])

def _parse_config() -> namedtuple:
    _is_initial_run() and _gen_divider()
    fields = ('domain', 'uid', 'access', 'homepage', 'email')
    defaults = (None, uuid.uuid1(), _gen_rand_path(), HOMEPAGE_URL, 'fake@gmail.com')
    Config = namedtuple('config', fields, defaults=defaults)
    kwargs = {field: os.getenv(field.upper()) for field in fields}
    config = Config(**{key: value for key, value in kwargs.items() if value})
    if not config.domain:
        raise Exception('Domain is neccessary but not provided!')
    if _is_initial_run():
        print('Using config:')
        print(json.dumps({field: str(getattr(config, field)) for field in fields}, indent=4))
        _gen_divider()
    return config

def _sync_homepage(url: str, filepath: str) -> str:
    if not os.path.exists(filepath):
        html = requests.get(url).text
        attr_tuple = urllib.parse.urlparse(url)
        url_base = f'{attr_tuple.scheme or "https"}://{attr_tuple.netloc}/'
        href_regex = r'href=("|\')/?([^wh].+?)("|\')'
        new_content = re.sub(href_regex, r'href="{}\2"'.format(url_base), html)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w+', encoding='utf-8') as f:
            f.write(new_content)
    return filepath

def _replace_variable(config: namedtuple, text: str) -> str:
    for field in config._fields:
        text = text.replace(f'${field}', str(getattr(config, field)))
    return text

def _rewrite(original: str, target: str, encoding='utf-8', validators = []) -> None:
    with open(original, 'r', encoding=encoding) as fo:
        text = fo.read()
        for validator in validators:
            text = validator(text=text)
        with open(target, 'w+', encoding=encoding) as ft:
            ft.write(text)

def _apply_config(config: namedtuple) -> None:
    replace_variable = partial(_replace_variable, config=config)
    rewrite = partial(_rewrite, validators=(replace_variable, ))
    rewrite('config/nginx.conf', NGINX_CONFIG_PATH)
    rewrite('config/v2ray.server.json', V2RAY_CONFIG_PATH)
    rewrite('config/v2ray.user.json', V2RAY_USER_CONFIG_PATH)

def _ssl_certificate(domain: str, email: str) -> None:
    print('Requesting certificate...')
    cert_paths = [tmpl % domain for tmpl in (CERT_PATH, PRIVIATE_KEY_PATH, CHAIN_PATH)]
    if not all([os.path.exists(path) for path in cert_paths]):
        cert_cmd = 'certbot certonly --standalone --domain {} --agree-tos -n --email {}'
        if os.system(cert_cmd.format(domain, email)):
            raise Exception('certificate failed...')
    _gen_divider()

def _init_bg_tasks(config: namedtuple) -> None:
    renew_log = CERT_RENEW_LOG_PATH % config.domain
    v2ray_path = os.path.join(V2RAY_BINARY_DIR, "v2ray")
    os.makedirs(os.path.dirname(renew_log), exist_ok=True)
    os.makedirs(os.path.dirname(V2RAY_INITIALIZE_LOG_PATH), exist_ok=True)
    os.system('nohup sh -c "while sleep 86400; do nginx -s reload; done" &')
    os.system(f'nohup sh -c "while sleep 86400; do certbot renew; done >> {renew_log}" &')
    os.system(f'nohup sh -c "{v2ray_path} -config {V2RAY_CONFIG_PATH} >> {V2RAY_INITIALIZE_LOG_PATH}" &')

def _gen_v2rayng_config(config: namedtuple) -> dict:
    return {
        'address': config.domain,
        'port': 443,
        'id': str(config.uid),
        'encryption': 'none',
        'network': 'ws',
        'path': config.access,
        'tls': 'tls',
    }

def _print_info(config: namedtuple) -> None:
    print('V2ray client config:')
    os.system(f'cat {V2RAY_USER_CONFIG_PATH}')
    _gen_divider()
    print('V2rayNG config (Type manually[VLESS])')
    v2rayng_config = _gen_v2rayng_config(config)
    print(json.dumps(v2rayng_config, indent=4))
    _gen_divider()
    print('All services started...')
    print(f'Access https://{config.domain}/files to download V2ray binary and V2rayNG APK...')

def _initialize(config: namedtuple) -> None:
    _apply_config(config)
    _sync_homepage(config.homepage, HOMEPATE_PATH)
    _ssl_certificate(config.domain, config.email)
    _print_info(config)
    open(INITIAL_TAG_PATH, 'w+').close()

if __name__ == '__main__':
    config = _parse_config()
    _is_initial_run() and _initialize(config)
    _init_bg_tasks(config)
    os.system('nginx -g "daemon off;"')