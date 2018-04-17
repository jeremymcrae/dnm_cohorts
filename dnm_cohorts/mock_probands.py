
import random

from dnm_cohorts.person import Person
from dnm_cohorts.random_id import random_id

def add_mock_probands(persons, required, prefix, study, phenotype):
    """ include mock probands for those without any de novos
    
    Args:
        persons: set of unique persons in the cohort
        required: number of required mock_probands
        prefix: prefix for mock sample IDs
        study: code to identify the study
        phenotype: phenotype of probands (some studies include affected and
            unaffected).
    """
    
    affected = [ x for x in persons if x['phenotype'] == phenotype ]
    # use the current individuals to estimate the proportion of males, so we
    # can sample according to that fraction, to avoid changing the ratio.
    male_ratio = sum(x['sex'] == 'male' for x in persons)/len(affected)
    
    for x in range(required - len(affected)):
        person_id = '{}_{}'.format(prefix, random_id())
        sex = 'male' if random.random() < male_ratio else 'female'
        person = Person({'person_id': person_id, 'sex': sex,
            'phenotype': phenotype, 'study': study})
        persons.add(person)
    
    return persons
