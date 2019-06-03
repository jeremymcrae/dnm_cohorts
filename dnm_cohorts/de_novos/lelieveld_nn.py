
import logging

import pandas

from dnm_cohorts.ensembl import genome_sequence
from dnm_cohorts.de_novo import DeNovo

url = "http://www.nature.com/neuro/journal/v19/n9/extref/nn.4352-S3.xlsx"

def fix_alleles(data):
    """ clean up ref and alt alleles in a dataset
    
    Requires dataset to have columns for chrom, pos, ref and alt
    """
    
    # work on a copy, to prevent assignment warnings
    ref = data['ref'].copy()
    alt = data['alt'].copy()
    
    idx = ref.isnull()
    ref[idx] = [ genome_sequence(x.chrom, x.pos, x.pos) for i, x in data[idx].iterrows() ]
    
    # add the reference base to insertions
    alt[idx] = ref[idx] + alt[idx]
    
    # make deletion alts VEP-compatible
    alt[alt.isnull()] = '-'
    
    return ref, alt

def lelieveld_nn_de_novos():
    """ get de novo data for Lelieveld et al. intellectual disability exome study
    
    De novo mutation data sourced from supplementary table 1 from:
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
    
    data['ref'], data['alt'] = fix_alleles(data)
    
    data['person_id'] += '|lelieveld'
    data['study'] = '10.1038/nn.4352'
    data['confidence'] = 'high'
    
    vars = set()
    for i, row in data.iterrows():
        var = DeNovo(row.person_id, row.chrom, row.pos, row.ref, row.alt,
            row.study, row.confidence, 'grch37')
        vars.add(var)
    
    return vars
