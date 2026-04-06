import json
import urllib.request

url = 'https://api.github.com/repos/Nitrodz00/NITRO-TOOLS/releases/latest'

try:
    with urllib.request.urlopen(url, timeout=10) as r:
        data = json.load(r)
        print('status', r.status)
        print('tag_name', data.get('tag_name'))
        print('name', data.get('name'))
        print('draft', data.get('draft'))
        print('prerelease', data.get('prerelease'))
        print('assets', len(data.get('assets', [])))
except Exception as e:
    print('error', e)
