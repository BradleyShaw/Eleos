import requests


def paste(payload):
    pastebin = 'https://pybin.pw'
    url = '{0}/documents'.format(pastebin)
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        return '{0}/{1}'.format(pastebin, response.json()['key'])
