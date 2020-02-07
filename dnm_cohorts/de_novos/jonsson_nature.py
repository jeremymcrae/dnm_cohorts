
import os
import gzip
import logging
import tempfile
import tarfile
from zipfile import ZipFile

import pandas

from dnm_cohorts.download_file import download_file
from dnm_cohorts.de_novo import DeNovo

url = "https://static-content.springer.com/esm/art%3A10.1038%2Fnature24018/MediaObjects/41586_2017_BFnature24018_MOESM2_ESM.zip"

async def jonsson_nature_de_novos(result):
    """ get de novo variants for Jonsson et al Nature 2017
    
    Supplementary Table 4 from:
    Jonsson et al. Nature 549: 519-522, doi: 10.1038/nature24018
    """
    logging.info('getting Jonsson et al Nature 2017 de novos')
    zipf = tempfile.NamedTemporaryFile()
    download_file(url, zipf.name)
    
    # open the zipfile, then open a tarfile inside the zip, then extract and
    # read from file inside the tar
    path = 'nature24018-s2/Aging_Oocytes_Supplementary_Table_DNMs.tar.gz'
    with ZipFile(zipf.name) as zip, tarfile.open(fileobj=zip.open(path)) as tar:
        member = tar.getmember('decode_DNMs/decode_DNMs.tsv')
        data = pandas.read_table(tar.extractfile(member))
    
    data['person_id'] = data['Proband_nr'].astype(str)
    data['person_id'] += '|jonsson'
    data['chrom'] = data['Chr'].astype(str)
    data['pos'] = data['Pos_hg38']
    data['ref'] = data['Ref']
    data['alt'] = data['Alt']
    data['study'] = '10.1038/nature24018'
    data['confidence'] = 'high'
    data['build'] = 'grch38'
    
    # remove individuals who were children of other probands
    child_ids = set(data.person_id[data.Phase_source == 'three_generation'])
    data = data[~data.person_id.isin(child_ids)]
    
    vars = set()
    for i, row in data.iterrows():
        var = DeNovo(row.person_id, row.chrom, row.pos, row.ref, row.alt,
            row.study, row.confidence, row.build)
        vars.add(var)
    
    result.append(vars)
