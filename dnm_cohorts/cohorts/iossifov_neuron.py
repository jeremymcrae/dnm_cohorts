
import itertools
import logging

import pandas

from dnm_cohorts.person import Person

supp_s1_url = 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3619976/bin/NIHMS374246-supplement-02.xlsx'
supp_s2_url = 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3619976/bin/NIHMS374246-supplement-03.xlsx'
supp_s3_url = 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3619976/bin/NIHMS374246-supplement-04.xlsx'

def open_iossifov_neuron_cohort():
    """ get probands sequenced in Iossifov et al., Neuron 2012
    
    Iossifov et al. (2012) Neuron 74:285-299
    doi: 10.1016/j.neuron.2012.04.009
    Data from supplementary tables S1, S2 and S3.
    """
    logging.info('getting Iossifov et al Neuron 2012 cohort')
    s1 = pandas.read_excel(supp_s1_url, sheet_name='SNV.v4.1-normlized')
    s2 = pandas.read_excel(supp_s2_url, sheet_name='suppLGKTable')
    s3 = pandas.read_excel(supp_s3_url, sheet_name='ID.v4.1-normlized')
    
    fam_ids = list(s1.quadId) + list(s2.quadId) + list(s3.quadId)
    members = list(s1.inChild) + list(s2.inChild) + list(s3.inChild)
    
    sex = ['M', 'F']
    affected = ['aut', 'sib']
    possible = list(itertools.product(affected, sex))
    study = ['10.1016/j.neuron.2012.04.009']
    
    persons = set()
    for fam, children in zip(fam_ids, members):
        for affected, sex in possible:
            string = f'{affected}{sex}'
            if string in children:
                status = ['unaffected'] if affected != 'aut' else ['HP:0000717']
                member = 's1' if affected != 'aut' else 'p1'
                sex = 'female' if sex == 'F' else 'male'
                person_id = f'{fam}.{member}|asd_cohorts'
                
                person = Person(person_id, sex, status, study)
                persons.add(person)
    
    return persons
