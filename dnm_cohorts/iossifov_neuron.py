
import pandas
import itertools

from dnm_cohorts.hashdict import Hashdict

supp_s1_url = 'http://www.cell.com/cms/attachment/2024816859/2044465439/mmc2.xlsx'
supp_s2_url = 'http://www.cell.com/cms/attachment/2024816859/2044465438/mmc3.xlsx'
supp_s3_url = 'http://www.cell.com/cms/attachment/2024816859/2044465437/mmc4.xlsx'

def open_iossifov_neuron_cohort():
    s1 = pandas.read_excel(supp_s1_url, sheet_name='SNV.v4.1-normlized')
    s2 = pandas.read_excel(supp_s2_url, sheet_name='suppLGKTable')
    s3 = pandas.read_excel(supp_s3_url, sheet_name='ID.v4.1-normlized')
    
    fam_ids = list(s1.quadId) + list(s2.quadId) + list(s3.quadId)
    members = list(s1.inChild) + list(s2.inChild) + list(s3.inChild)
    
    sex = ['M', 'F']
    affected = ['aut', 'sib']
    possible = list(itertools.product(affected, sex))
    study = 'iossifov_neuron_2012'
    
    persons = set()
    for fam, children in zip(fam_ids, members):
        for affected, sex in possible:
            string = '{}{}'.format(affected,sex)
            if string in children:
                status = 'unaffected' if affected != 'aut' else 'autism'
                member = 's1' if affected != 'aut' else 'p1'
                sex = 'female' if sex == 'F' else 'male'
                person_id = '{}.{}'.format(fam, member)
                
                person = Hashdict({'person_id': person_id, 'sex': sex,
                    'phenotype': status, 'study': study})
                persons.add(person)
    
    return list(persons)
