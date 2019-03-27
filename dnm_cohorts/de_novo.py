
class DeNovo:
    
    CHROMS = list(map(str, range(1, 23))) + ['X', 'Y', 'MT']
    CHROMS = dict(zip(CHROMS, range(len(CHROMS))))
    
    def __init__(self, person_id, chrom, pos, ref, alt, study, confidence,
            symbol=None, consequence=None):
        self.person_id = str(person_id)
        self.chrom = str(chrom)
        self.pos = int(pos)
        self.ref = ref
        self.alt = alt
        self.study = study
        self.confidence = confidence
        self.symbol = '' if symbol is None else symbol
        self.consequence = '' if consequence is None else consequence
        
        max_len = max(len(self.ref), len(self.alt)) - 1
        self.range = (self.pos - max_len, self.pos + max_len)
    
    def __repr__(self):
        return 'DeNovo("{}", "{}", {}, "{}", "{}", "{}", "{}", "{}", "{}")'.format( \
            *list(self))
    
    def __str__(self):
        return '\t'.join(map(str, list(self)))
    
    def __iter__(self):
        group = [self.person_id, self.chrom, self.pos, self.ref, self.alt,
            self.study, self.confidence, self.symbol, self.consequence]
        for x in group:
            yield x
    
    def __hash__(self):
        return hash(f'{self.person_id}-{self.chrom}-{self.pos}')
    
    def __eq__(self, other):
        """ check if two variants are the same (permit fuzzy distance matches)
        """
        if not self.person_id == other.person_id and self.chrom == other.chrom:
            return False
        
        x1, x2 = self.range
        y1, y2 = other.range
        return x2 >= y1 and y2 >= x1
    
    def __gt__(self, other):
        return [self.person_id, self._int_chrom(), self.pos] > \
            [other.person_id, other._int_chrom(), other.pos]
    
    def _int_chrom(self):
        chrom = self.chrom.strip('chr')
        if chrom not in self.CHROMS:
            self.CHROMS[chrom] = max(self.CHROMS.values()) + 1
        
        return self.CHROMS[chrom]
