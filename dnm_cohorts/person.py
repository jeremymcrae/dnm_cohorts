
class Person(dict):
    
    def __init__(self, person_id, sex, phenotype):
        self.person_id = person_id
        self.sex = sex
        self.phenotype = phenotype
    
    def __repr__(self):
        return 'Person("{}", "{}", "{}")'.format(*list(self))
    
    def __str__(self):
        return '{}\t{}\t{}'.format(*list(self))
    
    def __hash__(self):
        string = '{}-{}-{}'.format(*list(self))
        return hash(string)
    
    def __iter__(self):
        self._idx = 0
        return self
    
    def __next__(self):
        self._idx += 1
        if self._idx > 3:
            raise StopIteration
        
        return [self.person_id, self.sex, self.phenotype][self._idx - 1]
    
    def __eq__(self, other):
        return hash(self) == hash(other)
    
    def __gt__(self, other):
        return self.id > other.id
