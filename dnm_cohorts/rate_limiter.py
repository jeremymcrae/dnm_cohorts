
import time
import logging
import trio

import asks
asks.init('trio')

from dnm_cohorts.rate_limiter_retries import ensembl_retry as retry

class RateLimiter:
    ''' class to asynchronously perform http get requests

    This respects the rate limits imposed by the server. Error handling and
    retrying are handled by the 'retry' decorator.
    '''
    MAX_TOKENS = 10
    def __init__(self, per_second=10):
        ''' initialize the class object

        Args:
            per_second: number of queries allowed per second
        '''
        self.tokens = self.MAX_TOKENS
        self.RATE = per_second
        self.updated_at = time.monotonic()
        self.count = 0
    async def __aenter__(self):
        self.client = asks.Session(connections=50)
        return self
    async def __aexit__(self, *err):
        await self.client.close()
        self.client = None

    @retry(retries=9)
    async def get(self, url, *args, **kwargs):
        ''' perform asynchronous http get

        Args:
            url: url to get
            headers: http headers to pass in with the get query
        '''
        if 'headers' not in kwargs:
            kwargs['headers'] = {'content-type': 'application/json'}
        if 'params' not in kwargs:
            kwargs['params'] = {}
        await self.wait_for_token()
        try:
            resp = await self.client.get(url, *args, **kwargs)
        except:
            logging.error(f'problem accessing {url}')
            raise
        logging.info(f'{url}\t{resp.status_code}')
        resp.raise_for_status()
        return resp.text
    
    @retry(retries=3)
    async def post(self, url, *args, **kwargs):
        ''' perform asynchronous http post

        Args:
            url: url to get
            headers: http headers to pass in with the get query
        '''
        if 'headers' not in kwargs:
            kwargs['headers'] = {'content-type': 'application/json'}
        if 'data' not in kwargs:
            kwargs['data'] = {}
        await self.wait_for_token()
        resp = await self.client.post(url, *args, **kwargs)
        logging.info(f'{url}\t{resp.status_code}')
        resp.raise_for_status()
        return resp.text

    async def wait_for_token(self):
        ''' pause until tokens are refilled
        '''
        while self.tokens < 1:
            self.add_new_tokens()
            await trio.sleep(1 / self.RATE)
        self.tokens -= 1

    def add_new_tokens(self):
        ''' add new tokens if sufficient time has passed
        '''
        now = time.monotonic()
        time_since_update = now - self.updated_at
        new_tokens = time_since_update * self.RATE
        if self.tokens + new_tokens >= 1:
            self.tokens = min(self.tokens + new_tokens, self.MAX_TOKENS)
            self.updated_at = now
