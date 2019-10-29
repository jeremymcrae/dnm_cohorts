# functions to extract data from the ensembl REST API

import json
import asyncio

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

def get_base_url(build):
    assert build in ["grch37", "grch38"], f'unknown build: {build}'
    ver = build + '.' if build == "grch37" else ''
    return f'http://{ver}rest.ensembl.org'

async def cq_and_symbol(limiter, var):
    """find the VEP consequence for a variant
    
    annotates the consequence and symbol attributes of the variant passed in.
    
    Args:
        limiter: object for asynchronously calling ensembl REST API
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
    resp = await limiter.get(url)
    data = json.loads(resp)
    var.consequence, var.symbol = most_severe(data[0])
    return var

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

class TaskPool(object):
    def __init__(self, workers):
        self._semaphore = asyncio.BoundedSemaphore(workers)
        self._tasks = set()
    async def put(self, coro):
        await self._semaphore.acquire()
        task = asyncio.create_task(coro)
        self._tasks.add(task)
        task.add_done_callback(self._on_task_done)
        return task
    def _on_task_done(self, task):
        self._tasks.remove(task)
        self._semaphore.release()
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        return

async def get_consequences(limiter, variants):
    ''' asychronously get variant consequences and symbols from ensembl
    '''
    # use a taskpool to lower memory requirements, and prevent creating hundreds
    # of thousands of tasks upfront. This loses some of the asynchronous
    # simultaneous advantagaes, but still works quickly.
    async with TaskPool(100) as pool:
        tasks = []
        for x in variants:
            x = await pool.put(cq_and_symbol(limiter, x))
            tasks.append(x)
        return await asyncio.gather(*tasks)

async def genome_sequence(ensembl, chrom, start, end, build='grch37'):
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
