
import io

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

import requests

def download_file(url, path, session=None):
    ''' download a file from a url to disk
    '''
    if not session:
        session = requests.session()
    r = session.get(url, stream=True)
    if r.status_code == 200:
        with open(path, 'wb') as f:
            for chunk in r.iter_content(1600):
                f.write(chunk)
    else:
        raise ValueError(f'{r.status_code} error downloading {url}, headers={r.headers}')

def download_with_cookies(url, path):
    ''' download a file, but set cookies beforehand
    '''
    # start a requests session and get cookies for the hostname
    session = requests.session()
    parsed = urlparse(url)
    _ = session.get(f'{parsed.scheme}://{parsed.hostname}')
    
    # I don't know why this is necessary, but it is. Otherwise we get perpetual
    # redirects with www.nejm.org
    _ = list(session.cookies)
    download_file(url, path, session)
