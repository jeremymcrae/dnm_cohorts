# functions to extract data from the ensembl REST API

import time
import logging

import requests
from requests.exceptions import HTTPError

# consequence list, as sorted at http://www.ensembl.org/info/genome/variation/predicted_data.html
consequences = ["transcript_ablation", "splice_donor_variant",
    "splice_acceptor_variant", "stop_gained", "frameshift_variant",
    "start_lost", "initiator_codon_variant", "stop_lost",
    "transcript_amplification", "inframe_insertion", "inframe_deletion",
    "missense_variant", "protein_altering_variant", "splice_region_variant",
    "incomplete_terminal_codon_variant", "start_retained_variant", "stop_retained_variant",
    "synonymous_variant", "coding_sequence_variant", "mature_miRNA_variant",
    "5_prime_UTR_variant", "3_prime_UTR_variant",
    "non_coding_transcript_exon_variant", "intron_variant",
    "NMD_transcript_variant", "non_coding_transcript_variant",
    "upstream_gene_variant", "downstream_gene_variant", "TFBS_ablation",
    "TFBS_amplification", "TF_binding_site_variant",
    "regulatory_region_ablation", "regulatory_region_amplification",
    "regulatory_region_variant", "feature_elongation", "feature_truncation",
    "intergenic_variant"]
severity = dict(zip(consequences, range(len(consequences))))

class Ensembl:
    initial = time.time() - 2
    base = 'rest.ensembl.org'
    headers = {'content-type': 'application/json'}
    session = requests.Session()
    
    def __init__(self, build='grch37'):
        build = build.lower()
        assert build in ["grch37", "grch38"]
        if build == "grch37":
            self.base = "grch37." + self.base
        else:
            self.base = self.base
    
    def __call__(self, ext, data=None, attempt=0):
        if attempt > 5:
            raise ValueError('too many attempts accessing')
        self._rate_limit()
        
        url = f'http://{self.base}/{ext}'
        
        if data is None:
            logging.info(url)
            response = self.session.get(url, headers=self.headers)
        else:
            logging.info(f'{url}\t{data}')
            response = self.session.post(url, headers=self.headers, data=data)
            
        if self.check_retry(response):
            return self.__call__(ext, data, attempt + 1)
        
        logging.info(f'{url}\t{response.status_code}')
        response.raise_for_status()
        
        return response.json()
    
    def _rate_limit(self):
        current = time.time()
        delta = 0.1 - (current - self.initial)
        time.sleep(max(0, delta))
        self.initial = current
    
    def check_retry(self, response):
        """ check for http request errors which permit a retry
        """
        if response.status_code == 500 or response.status_code == 503:
            # if the server is down, briefly pause
            time.sleep(30)
            return True
        elif response.status_code == 429:
            # if we exceed the server limits, pause for required time
            time.sleep(float(response.headers['retry-after']))
            return True
        elif response.status_code == 400:
            data = response.json()
            error = data['error']
            # account for some EBI REST server failures
            if 'Cannot allocate memory' in error:
                time.sleep(30)
                return True
            logging.info(f'{response.url}\tERROR 400: {error}')
        
        return False

ensembl = Ensembl('grch37')

def cq_and_symbol(chrom, pos, ref, alt):
    """find the VEP consequence for a variant
    
    Args:
        chrom: chromosome
        pos: nucleotide position
        ref: reference allele
        alt: alternate allele
        build: genome build to find consequences on
    
    Returns:
        a string containing the most severe consequence, as per VEP formats.
    
    Examples:
        get_vep_consequence("1", 1000000, "A", "G")
    """
    
    if alt == "":
        alt = "-"  # correct deletion allele for ensembl API
    
    ext = f"vep/human/region/{chrom}:{pos}:{pos + len(ref) - 1}/"
    
    try:
        data = ensembl(ext + alt)
    except HTTPError:
        data = ensembl(ext + ref)
    
    return find_most_severe_transcript(data[0])

def chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]

def flatten(nested):
    return [ x for sublist in nested for x in sublist ]

def break_large_lists(chroms, positions, refs, alts):
    """ break large lists into separate ensembl requests
    """
    
    grouped = list(zip(chroms, positions, refs, alts))
    
    cqs, symbols = [], []
    for group in chunks(grouped, 100):
        cq, symbol = cq_and_symbols(*zip(*group))
        cqs += cq
        symbols += symbol
    
    return cqs, symbols

def cq_and_symbols(chroms, positions, refs, alts, attempt=0):
    """ get consequence and symbol for multiple variants
    """
    
    if len(chroms) > 100:
        break_large_lists(chroms, positions, refs, alts)
    
    variants = []
    for chrom, pos, ref, alt in zip(chroms, positions, refs, alts):
        variants.append(f'{chrom} {pos} {pos + len(ref) - 1} {ref} {alt} . . .')
    
    data = str({'variants': variants}).replace("'", '"')
    ext = "vep/homo_sapiens/region"
    
    response = ensembl(ext, data)
    
    values = [ find_most_severe_transcript(x) for x in response ]
    return tuple(zip(*values))

def find_most_severe_transcript(data, exclude_bad=True):
    """ find the most severe transcript from Ensembl data
    
    Args:
        data: json data for variant from Ensembl
        exclude_bad: whether to exclude nonsense mediated decay transcripts etc.
            Only used when we haven't found a transcript during normal usage.
    
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
        return find_most_severe_transcript(data, exclude_bad=False)
    
    for tx in transcripts:
        # get consequence for current transcript
        tx['cq'] = min(tx['consequence_terms'], key=lambda x: severity[x])
        tx['not_hgnc'] = tx['gene_symbol_source'] != "HGNC" # sort HGNC first
    
    # return the most severe conequence, prefer transcripts with HGNC symbols
    tx = min(transcripts, key=lambda x: (severity[x['cq']], x['not_hgnc']))
    return tx['cq'], tx['gene_symbol']

def genome_sequence(chrom, start, end, build="grch37"):
    """ find genomic sequence within a region
    
    Args:
        chrom:
        start:
        end:
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
    data = ensembl(ext)
    
    if len(data) > 0:
        return data['seq']
    
    return ""
