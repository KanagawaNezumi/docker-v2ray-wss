import re
import sys
import urllib.parse

url = sys.argv[1]

file = '/usr/share/nginx/html/index.html'

# print('Index path:', file)

if url.startswith('http'):
    parsed_url = urllib.parse.urlparse(url)
    scheme = parsed_url.scheme
    netloc = parsed_url.netloc
else:
    netloc = url.partition('/')[0] if '/' in url else url
    scheme = 'https'

base_url = f'{scheme}://{netloc}/'

# print('Base url:', base_url)

with open(file, 'r+', encoding='utf-8') as fp:
    data = ''.join(fp.readlines())
    # print('Data length:', len(data))
    new_data = re.sub(r'href=("|\')/?([^wh].+?)("|\')', r'href="{}\2"'.format(base_url), data)
    # print('Data length repaired:', len(new_data))

with open(file, 'w', encoding='utf-8') as fp:
    fp.write(new_data)