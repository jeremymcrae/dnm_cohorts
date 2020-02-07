
import os
import random
import tempfile
import tarfile
from zipfile import ZipFile

import pandas

from dnm_cohorts.download_file import download_file
from dnm_cohorts.person import Person

url = "https://static-content.springer.com/esm/art%3A10.1038%2Fnature24018/MediaObjects/41586_2017_BFnature24018_MOESM2_ESM.zip"

def open_jonsson_nature_cohort():
    """ get cohort for Jonsson et al Nature 2017
    
    Supplementary Table 4 from:
    Jonsson et al. Nature 549: 519-522, doi: 10.1038/nature24018
    """
    random.seed(1)
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
    data['chrom'] = data['Chr'].astype('str')
    
    # remove individuals who were children of other probands
    child_ids = set(data.person_id[data.Phase_source == 'three_generation'])
    data = data[~data.person_id.isin(child_ids)]
    
    # we need to know which individuals are female. From the de novo table:
    #   - 99% of chrX dnms have alt fractions between 0.3-0.75
    #   - we expect 5% of DNMs to occur on chrX, but only have half that at 2%
    #   - only half (818 of 1548) of individuals have a chrX de novo call
    # These imply only females have chrX de novo calls. ChrX is 5% of the genome,
    # so we expect ~3.5 de novo calls on chrX per person. The chance of a person
    # having 0 chrX de novo calls is 3%, so the number of females should be ~3%
    # higher (818 - (818 / (1 - 0.03)) = 25). Of the remaining individuals,
    # each is 3.4% likely to be female (25 / (1548 - 818) = 0.0342)
    females = set(data.person_id[data.chrom == 'chrX'])
    missing_n = len(females) - (len(females) / (1 - 0.0301))
    female_remainder = missing_n / (len(set(data.person_id)) - len(females))
    
    phenotype = ['unaffected']
    study = ['10.1038/nature24018']
    
    persons = set()
    for i, row in data.iterrows():
        # individuals have two chances to be female, 1) if their sample if is in
        # the female group, or 2) 3.4% of the remainder are female.
        sex = 'female' if row.person_id in females or random.random() < female_remainder else 'male'
        person = Person(row.person_id, sex, phenotype, study)
        persons.add(person)
    
    return persons
