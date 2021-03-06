
import trio
import logging

import pandas

from dnm_cohorts.ensembl import parallel_sequence
from dnm_cohorts.de_novo import DeNovo

url = "https://static-content.springer.com/esm/art%3A10.1038%2Fnn.4352/MediaObjects/41593_2016_BFnn4352_MOESM21_ESM.xlsx"

async def fix_alleles(limiter, data):
    """ clean up ref and alt alleles in a dataset
    
    Requires dataset to have columns for chrom, pos, ref and alt
    """
    
    # work on a copy, to prevent assignment warnings
    ref = data['ref'].copy()
    alt = data['alt'].copy()
    
    idx = ref.isnull()
    
    seqs = {}
    coords = [(x.chrom, x.pos, x.pos, x.build) for i, x in data[idx].iterrows()]
    async with trio.open_nursery() as nursery:
        for x in coords:
            nursery.start_soon(parallel_sequence, limiter, *x[:3], seqs, x[3])
    
    ref[idx] = [seqs[x] for x in coords]
    
    # add the reference base to insertions
    alt[idx] = ref[idx] + alt[idx]
    
    # make deletion alts VEP-compatible
    idx = alt.isnull()

    seqs = {}
    coords = [(x.chrom, x.pos - 1, x.pos - 1, x.build) for i, x in data[idx].iterrows()]
    async with trio.open_nursery() as nursery:
        for x in coords:
            nursery.start_soon(parallel_sequence, limiter, *x[:3], seqs, x[3])
    
    alt[idx] = [seqs[x] for x in coords]
    ref[idx] =  alt[idx] + ref[idx]
    
    return ref, alt

async def lelieveld_nn_de_novos(result, limiter):
    """ get de novo data for Lelieveld et al. intellectual disability exome study
    
    De novo mutation data sourced from supplementary table 2 from:
    Lelieveld et al. (2016) Nature Neuroscience 19:1194-1196
    doi: 10.1038/nn.4352
    
    Note that the paper says that the data were aligned to hg19, but their
    table of de novo data is definitely for hg18 (GRCh37).
    
    Returns:
        data frame of de novos, including gene symbol, functional consequence
        (VEP format), chromosome, nucleotide position and SNV or INDEL type
    """
    logging.info('getting Lelieveld et al Nature Neuroscience 2016 de novos')
    data = pandas.read_excel(url, sheet_name='Supplementary Table 2')
    
    data['person_id'] = data['Patient key'].astype(str)
    data['chrom'] = data['Chromosome'].str.replace('chr', '')
    data['pos'] = data['Start position']
    data['ref'] = data['Reference Allele']
    data['alt'] = data['Variant Allele']
    data['build'] = 'grch37'
    
    data['ref'], data['alt'] = await fix_alleles(limiter, data)
    
    data['person_id'] += '|lelieveld'
    data['study'] = '10.1038/nn.4352'
    data['confidence'] = 'high'
    
    vars = set()
    for i, row in data.iterrows():
        var = DeNovo(row.person_id, row.chrom, row.pos, row.ref, row.alt,
            row.study, row.confidence, row.build)
        vars.add(var)
    
    result.append(vars)
