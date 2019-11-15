
import trio
import random
import functools

from asks.errors import (RequestTimeout, ServerClosedConnectionError, BadStatus,
    BadHttpResponse)

def ensembl_retry(retries=5):
    ''' perform all the error handling for the request
    
    retries up to N times under certain error conditions, and increases waiting
    time between requests, unless we've hit rate limits, when it uses the stated
    retry time.
    '''
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            result = None
            last_exception = None
            for i in range(retries):
                try:
                    return await func(*args, **kwargs)
                # except (ServerDisconnectedError, ClientOSError, RequestTimeout) as err:
                except (ServerClosedConnectionError, RequestTimeout) as err:
                    last_exception = err
                    delay = 0
                except BadHttpResponse as err:
                    last_exception = err
                    delay = 1
                except BadStatus as err:
                    last_exception = err
                    # 500, 503, 504 are server down issues. 429 exceeds rate
                    # limits. 400 is server memory issue. Raises other errors.
                    if err.status_code not in [500, 503, 504, 429, 400]:
                        raise err
                    delay = random.uniform(0, 2 ** (i + 2))
                    if err.status_code == 429:
                        delay = float(dict(err.response.headers)['retry-after'])
                await trio.sleep(delay)
            if last_exception is not None:
                raise type(last_exception) from last_exception
            return result
        return wrapper
    return decorator
