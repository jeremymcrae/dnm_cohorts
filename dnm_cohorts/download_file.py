
import io

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

import requests

def download_file(url, path):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(path, 'wb') as f:
            for chunk in r.iter_content(1600):
                f.write(chunk)

def download_with_cookies(url):
    ''' download a file, but set cookies beforehand
    '''
    # start a requests session and get cookies for the hostname
    session = requests.session()
    parsed = urlparse(url)
    _ = session.get('{}://{}'.format(parsed.scheme, parsed.hostname))
    
    # I don't know why this is necessary, but it is. Otherwise we get perpetual
    # redirects with www.nejm.org
    _ = list(session.cookies)
    
    # download document, and load into a in-memory buffer as a quasi-file handle
    r = session.get(url)
    r.raise_for_status()
    
    return io.BytesIO(r.content)
