
import os
import logging
import tempfile
from zipfile import ZipFile

import pandas

from dnm_cohorts.download_file import download_file
from dnm_cohorts.de_novo import DeNovo

url = 'http://science.sciencemag.org/highwire/filestream/646355/field_highwire_adjunct_files/1/aac9396_SupportingFile_Other_seq1_v4.zip'

async def homsy_science_de_novos():
    """ get de novo variants for Homsy et al Science 2015
    
    Supplementary Database 1 from:
    Homsy et al. Science 350: 1262-1266, doi: 10.1126/science.aac9396
    """
    logging.info('getting Homsy et al Science 2015 de novos')
    zipf = tempfile.NamedTemporaryFile()
    download_file(url, zipf.name)
    
    with ZipFile(zipf.name) as zipped:
        handle = zipped.open('homsy_database_S02.xlsx')
        data = pandas.read_excel(handle, 'Database S2', skiprows=1)
    
    data['person_id'] = data['Blinded ID'].astype(str)
    data['person_id'] += '|homsy'
    data['chrom'] = data['CHROM'].astype(str)
    data['pos'] = data['POS']
    data['ref'] = data['REF']
    data['alt'] = data['ALT']
    data['study'] = '10.1126/science.aac9396'
    data['confidence'] = 'high'
    
    vars = set()
    for i, row in data.iterrows():
        var = DeNovo(row.person_id, row.chrom, row.pos, row.ref, row.alt,
            row.study, row.confidence, 'grch37')
        vars.add(var)
    
    return vars
