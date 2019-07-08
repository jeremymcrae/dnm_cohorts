
import pandas

from dnm_cohorts.person import Person

url = 'https://www.nature.com/nature/journal/v485/n7397/extref/nature10945-s2.xls'

def open_sanders_nature_cohort():
    """ load individuals form Sanders et al Nature 2012 cohort
    
    Sanders et al. (2012) Nature 485:237-241
    doi: 10.1038/nature10945
    Supplementary table S1
    """
    data = pandas.read_excel(url, sheet_name='Sheet1')
    
    persons = set()
    for i, row in data.iterrows():
        if row.Sample.endswith('fa') or row.Sample.endswith('mo'):
            # ignore parental samples
            continue
        
        status = ['HP:0000717']
        if row.Role == 'Unaffected_Sibling':
            status = ['unaffected']
        
        person = Person(row.Sample + '|asd_cohorts', row.Gender.lower(), status)
        persons.add(person)
        
    return persons
