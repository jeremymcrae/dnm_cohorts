
class Person(dict):
    
    def __init__(self, person_id, sex, phenotype, studies):
        self.person_id = str(person_id)
        self.sex = sex
        self.phenotype = phenotype
        self.studies = studies
    
    def __repr__(self):
        return f'Person("{self.person_id}", "{self.sex}", "{self.phenotype}", {self.studies})'
    
    def __str__(self):
        return f'{self.person_id}\t{self.sex}\t{",".join(self.phenotype)}\t{",".join(self.studies)}'
    
    def __hash__(self):
        return hash(f'{self.person_id}')
    
    def __eq__(self, other):
        return hash(self) == hash(other)
    
    def __gt__(self, other):
        return self.person_id > other.person_id
