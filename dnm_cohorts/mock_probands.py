
import random

from dnm_cohorts.person import Person
from dnm_cohorts.random_id import random_id

def add_mock_probands(persons, required, prefix, suffix, phenotype):
    """ include mock probands for those without any de novos
    
    Args:
        persons: set of unique persons in the cohort
        required: number of required mock_probands
        prefix: prefix for mock sample IDs
        suffix: suffix for mock sample IDs
        phenotype: phenotype of probands (some studies include affected and
            unaffected).
    """
    # ensure IDs and sexes are repeatable between runs by setting the random
    # seed with the first known person for each cohort.
    random.seed(str(min(persons)))
    
    affected = [ x for x in persons if x.phenotype == phenotype ]
    # use the current individuals to estimate the proportion of males, so we
    # can sample according to that fraction, to avoid changing the ratio.
    male_ratio = sum(x.sex == 'male' for x in affected)/len(affected)
    
    for x in range(required - len(affected)):
        person_id = f'{prefix}_{random_id()}|{suffix}'
        sex = 'male' if random.random() < male_ratio else 'female'
        person = Person(person_id, sex, phenotype)
        persons.add(person)
    
    return persons
