
import logging
import tempfile
import math
import re
from zipfile import ZipFile

import pandas

from dnm_cohorts.download_file import download_file
from dnm_cohorts.fix_hgvs import fix_coordinates
from dnm_cohorts.de_novo import DeNovo

url = "http://www.nature.com/nature/journal/v515/n7526/extref/nature13908-s2.zip"

def get_sample_ids(fams):
    """ create a ditionary mapping family ID to sample, to subID
    
    Returns:
        e.g {'10000': {'p': 'p1', 's': 's1'}, ...}
    """
    
    sample_ids = {}
    for i, row in fams.iterrows():
        ids = set()
        for col in ['CSHL', 'UW', 'YALE']:
            col = 'SequencedAt' + col
            if type(row[col]) == float:
                continue
            
            ids |= set(row[col].split(','))
        
        # we want to refer to the individuals by 'p' or 's' for proband or
        # sibling, since that is how they are represented in the de novo table
        sample_ids[str(row.familyId)] = dict( (x[0], x) for x in ids )
    
    return sample_ids

def get_person_ids(data, sample_ids):
    
    fam_ids = data['familyId'].astype(str)
    children = data.inChild.str.split('M|F')
    
    person_ids = []
    for fam, samples in zip(fam_ids, children):
        persons = ( sample_ids[fam][x] for x in samples if x != '' )
        persons = [ f'{fam}.{x}' for x in persons ]
        person_ids.append(persons)
    
    return person_ids

def tidy_families(data):
    ''' Tidy de novo data to one line per individual
    '''
    
    cleaned = []
    
    for i, row in data.iterrows():
        ids = row.person_id[:]
        for person_id in ids:
            temp = row.copy()
            temp.person_id = person_id
            cleaned.append(temp)
    
    return pandas.DataFrame.from_records(cleaned)

def iossifov_nature_de_novos():
    """ get de novo variants fromn Iossifov et al., Nature 2014
    
    Nature (2014) 515: 216-221, doi:10.1038/nature13908
    Variants sourced from Supplementary tables S2, with person IDs sourced from
    Table S1.
    """
    logging.info('getting Iossifov et al Nature 2014 de novos')
    temp = tempfile.NamedTemporaryFile()
    download_file(url, temp.name)
    
    handle = ZipFile(temp.name)
    
    # obtain the dataframe of de novo variants
    data = pandas.read_excel(handle.open('nature13908-s2/Supplementary Table 2.xlsx'))
    fams = pandas.read_excel(handle.open('nature13908-s2/Supplementary Table 1.xlsx'))
    
    chrom, pos, ref, alt = fix_coordinates(data['location'], data['vcfVariant'])
    data['chrom'], data['pos'], data['ref'], data['alt'] = chrom, pos, ref, alt
    
    sample_ids = get_sample_ids(fams)
    data['person_id'] = get_person_ids(data, sample_ids)
    data = tidy_families(data)
    
    data['person_id'] += '|asd_cohorts'
    data['study'] = "10.1038/nature13908"
    data['confidence'] = 'high'
    
    vars = set()
    for i, row in data.iterrows():
        var = DeNovo(row.person_id, row.chrom, row.pos, row.ref, row.alt,
            row.study, row.confidence, 'grch37')
        vars.add(var)
    
    return vars
