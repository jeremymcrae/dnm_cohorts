# functions to extract data from the ensembl REST API

import time
import logging
import asyncio
import random
import json
import functools

import aiohttp

REQS_PER_SECOND = 15

# consequence list, as sorted at
# http://www.ensembl.org/info/genome/variation/predicted_data.html
consequences = ["transcript_ablation", "splice_donor_variant",
    "splice_acceptor_variant", "stop_gained", "frameshift_variant",
    "start_lost", "initiator_codon_variant", "stop_lost",
    "transcript_amplification", "inframe_insertion", "inframe_deletion",
    "missense_variant", "protein_altering_variant", "splice_region_variant",
    "incomplete_terminal_codon_variant", "start_retained_variant",
    "stop_retained_variant", "synonymous_variant", "coding_sequence_variant",
    "mature_miRNA_variant", "5_prime_UTR_variant", "3_prime_UTR_variant",
    "non_coding_transcript_exon_variant", "intron_variant",
    "NMD_transcript_variant", "non_coding_transcript_variant",
    "upstream_gene_variant", "downstream_gene_variant", "TFBS_ablation",
    "TFBS_amplification", "TF_binding_site_variant",
    "regulatory_region_ablation", "regulatory_region_amplification",
    "regulatory_region_variant", "feature_elongation", "feature_truncation",
    "intergenic_variant"]
severity = dict(zip(consequences, range(len(consequences))))

def retry(retries=5):
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
                except (aiohttp.ServerDisconnectedError, aiohttp.ClientOSError,
                        asyncio.TimeoutError) as err:
                    last_exception = err
                except aiohttp.ClientResponseError as err:
                    last_exception = err
                    # 500, 503, 504 are server down issues. 429 exceeds rate
                    # limits. 400 is server memory issue. Raises other errors.
                    if err.status not in [500, 503, 504, 429, 400]:
                        raise err
                    delay = random.uniform(0, 2 ** (i + 2))
                    if err.status == 429:
                        delay = float(dict(err.headers)['Retry-After'])
                await asyncio.sleep(delay)
            if last_exception is not None:
                raise type(last_exception) from last_exception
            return result
        return wrapper
    return decorator

class RateLimiter:
    MAX_TOKENS = 10
    def __init__(self, per_second=10):
        self.tokens = self.MAX_TOKENS
        self.RATE = per_second
        self.updated_at = time.monotonic()
    async def __aenter__(self):
        self.client = aiohttp.ClientSession()
        return self
    async def __aexit__(self, *err):
        await self.client.close()
        self.client = None
    
    @retry(retries=9)
    async def get(self, url, headers=None):
        ''' perform asynchronous http get
        '''
        if not headers:
            headers = {'content-type': 'application/json'}
        await self.wait_for_token()
        async with self.client.get(url, headers=headers) as resp:
            logging.info(f'{url}\t{resp.status}')
            resp.raise_for_status()
            return await resp.read()
    
    async def wait_for_token(self):
        ''' pause until tokens are refilled
        '''
        while self.tokens < 1:
            self.add_new_tokens()
            await asyncio.sleep(1 / self.RATE)
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

def get_base_url(build):
    assert build in ["grch37", "grch38"], f'unknown build: {build}'
    ver = build + '.' if build == "grch37" else ''
    return f'http://{ver}rest.ensembl.org'

async def cq_and_symbol(ensembl, var):
    """find the VEP consequence for a variant
    
    annotates the consequence and symbol attributes of the variant passed in.
    
    Args:
        ensembl: object for asynchronously calling ensembl REST API
        var: object with chrom, pos, ref and alt attributes. Optionally define
            genome build with 'build' attribute.
    
    Examples:
        from collections import namedtuple
        from dnm_cohorts.ensembl import Ensembl, get_consequences
        Var = namedtuple('Var', ['chrom', 'pos', 'ref', 'alt'])
        ens = Ensembl()
        var = Var('1', 1000000, "A", "G")
        get_vep_consequence(ens, var)
    """
    
    # correct deletion allele for ensembl API
    alt = '-' if var.alt == "" else var.alt
    
    ext = f"vep/human/region/{var.chrom}:{var.pos}:{var.pos + len(var.ref) - 1}/{alt}"
    url = f'{get_base_url(var.build)}/{ext}'
    resp = await ensembl.get(url)
    data = json.loads(resp)
    var.consequence, var.symbol = most_severe(data[0])

def most_severe(data, exclude_bad=True):
    """ find the most severe conseuence and gene symbol from Ensembl data
    
    Args:
        data: json data for variant from Ensembl
        exclude_bad: whether to exclude nonsense mediated decay transcripts etc.
            Only used when we haven't found a transcript via normal usage.
    
     Returns:
        tuple of VEP consequence, and hgnc symbol
    """
    
    # if the variant is intergenic, it won't be in any transcripts. just check
    # against the most severe consequences list and include a blank gene symbol
    if "transcript_consequences" not in data:
        return data['most_severe_consequence'], ""
    
    noncoding = ["lincRNA", "nonsense_mediated_decay", "pseudogene",
        "transcribed_unprocessed_pseudogene"]
    
    transcripts = data['transcript_consequences']
    if exclude_bad:
        transcripts = [ x for x in transcripts if x['biotype'] not in noncoding ]
    
    if len(transcripts) == 0:
        return most_severe(data, exclude_bad=False)
    
    for tx in transcripts:
        # get consequence for current transcript
        tx['cq'] = min(tx['consequence_terms'], key=lambda x: severity[x])
        tx['not_hgnc'] = tx['gene_symbol_source'] != "HGNC" # sort HGNC first
    
    # return the most severe consequence, prefer transcripts with HGNC symbols
    tx = min(transcripts, key=lambda x: (severity[x['cq']], x['not_hgnc']))
    return tx['cq'], tx['gene_symbol']

async def async_get_consequences(variants):
    ''' asychronously get variant consequences and symbols from ensembl
    '''
    async with RateLimiter(REQS_PER_SECOND) as ensembl:
        tasks = []
        semaphore = asyncio.BoundedSemaphore(50)
        for x in variants:
            await semaphore.acquire()
            task = asyncio.create_task(cq_and_symbol(ensembl, x))
            task.add_done_callback(lambda task: tasks.remove(task))
            task.add_done_callback(lambda task: semaphore.release())
            tasks.append(task)
        for f in asyncio.as_completed(set(tasks)):
            _ = await f

def get_consequences(variants):
    ''' asynchronously annotate consequence and gene symbol for many variants
    '''
    asyncio.run(async_get_consequences(variants))
    return variants

async def async_genome_sequence(ensembl, chrom, start, end, build="grch37"):
    """ find genomic sequence within a region
    
    Args:
        ensembl: object for asynchronously calling ensembl REST API
        chrom: chromosome
        start: start position
        end: end position
        build: genome build to find consequences on
        verbose: flag indicating whether to print variants as they are checked
    
    Returns:
        DNA sequence for genome region as str
    
    Examples:
        get_sequence_in_region("1", 1000000, 1000050)
    """
    
    if end < start:
        end = start
    
    ext = f"sequence/region/human/{chrom}:{start}:{end}:1"
    url = f'{get_base_url(build)}/{ext}'
    resp = await ensembl.get(url)
    data = json.loads(resp)
    
    if len(data) > 0:
        return data['seq']
    
    return ""

async def waiter(chrom, start, end, build):
    async with RateLimiter(REQS_PER_SECOND) as ensembl:
        return await async_genome_sequence(ensembl, chrom, start, end, build)

def genome_sequence(chrom, start, end, build='grch37'):
    ''' grab genome sequence for a single genome region
    
    This has been awkwardly shoehorned to the asynchronous ensembl class, but
    needs to be cleaned up, since it doesn't benefit from the asynchronocity.
    '''
    return asyncio.run(waiter(chrom, start, end, build))
