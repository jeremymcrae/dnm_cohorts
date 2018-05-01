
class DeNovo:
    
    def __init__(self, person_id, chrom, pos, ref, alt, study, confidence,
            symbol=None, consequence=None):
        self.person_id = person_id
        self.chrom = chrom
        self.pos = pos
        self.ref = ref
        self.alt = alt
        self.study = study
        self.confidence = confidence
        self.symbol = symbol
        self.consequence = consequence
        
        max_len = max(len(self.ref), len(self.alt)) - 1
        self.range = (self.pos - max_len, self.pos + max_len)
    
    def __repr__(self):
        return 'DeNovo("{}", "{}", {}, "{}", "{}", "{}", "{}")'.format( \
            self.person_id, self.chrom, self.pos, self.ref, self.alt,
            self.study, self.confidence)
    
    def __str__(self):
        # cope with missing symbol and consequences
        symbol = '' if self.symbol is None else self.symbol
        cq = '' if self.consequence is None else self.consequence
        
        data = [self.person_id, self.chrom, self.pos, self.ref, self.alt,
            self.study, self.confidence, symbol, cq]
        
        return '\t'.join(map(str, data))
    
    def __hash__(self):
        string = '{}-{}-{}'.format(self.person_id, self.chrom, self.pos)
        return hash(string)
    
    def __eq__(self, other):
        """ check if two variants are the same (permit fuzzy distance matches)
        """
        if not self.person_id == other.person_id and self.chrom == other.chrom:
            return False
        
        x1, x2 = self.range
        y1, y2 = other.range
        return x2 >= y1 and y2 >= x1
