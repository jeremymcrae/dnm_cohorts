
class Person(dict):
    
    def __init__(self, person_id, sex, phenotype):
        self.person_id = person_id
        self.sex = sex
        self.phenotype = phenotype
    
    def __repr__(self):
        return 'Person("{}", "{}", "{}", "{}")'.format(self.person_id, self.sex,
            self.phenotype)
    
    def __str__(self):
        return '{}\t{}\t{}'.format(self.person_id, self.sex, self.phenotype)
    
    def __hash__(self):
        string = '{}-{}-{}'.format(self.person_id, self.sex, self.phenotype)
        return hash(string)
    
    def __eq__(self, other):
        return hash(self) == hash(other)
