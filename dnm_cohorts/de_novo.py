
import logging
from liftover import get_lifter

CHROMS = list(map(str, range(1, 23))) + ['X', 'Y', 'MT']
CHROMS = dict(zip(CHROMS, range(len(CHROMS))))
BUILDS = {'grch36': 'grch36', 'hg18': 'grch36', 'grch37': 'grch37',
          'hg19': 'grch37', 'grch38': 'grch38', 'hg38': 'grch38'}
LIFTS = {'hg18': 'hg18', 'grch36': 'hg18', 'hg19': 'hg19', 'grch37': 'hg19',
         'hg38': 'hg38', 'grch38': 'hg38'}
TRANSDICT = str.maketrans('ACGTacgt', 'TGCAtgca')

def check_build(build):
    ''' make sure the genome build is one we know about
    '''
    if build not in BUILDS:
        raise ValueError(f'unknown genome, must be in {sorted(BUILDS)}')

def revcomp(seq):
    ''' reverse complement a sequence
    '''
    return seq.translate(TRANSDICT)[::-1]

class DeNovo:
    ''' class for keeping track of a de novo mutation
    '''
    lifters = {}
    
    def __init__(self, person_id, chrom, pos, ref, alt, study, confidence,
                 build='grch37', symbol=None, consequence=None):
        self.person_id = str(person_id)
        self.chrom = str(chrom).strip('chr')
        self.pos = int(pos)
        self.ref = ref
        self.alt = alt
        self.study = study
        self.confidence = confidence
        check_build(build)
        self.build = BUILDS[build]
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
            self.study, self.confidence, self.build, self.symbol, self.consequence]
        for x in group:
            yield x
    
    def __hash__(self):
        ''' get unique hash for variant, but standardized to grch38 genome build
        '''
        chrom, pos = self.chrom, self.pos
        if self.build != 'grch38':
            try:
                tmp = self.to_build('grch38')
                chrom, pos = tmp.chrom, tmp.pos
            except:
                pass
        return hash(f'{self.person_id}-{chrom}-{pos}')
    
    def __eq__(self, other):
        """ check if two variants are the same (permit fuzzy distance matches)
        """
        # account for variants on different genome builds
        if self.person_id != other.person_id:
            return False
        if self.build != other.build:
            other = other.to_build(self.build)
        if other is None:
            return False
        if self.chrom != other.chrom:
            return False
        
        x1, x2 = self.range
        y1, y2 = other.range
        return x2 >= y1 and y2 >= x1
    
    def __gt__(self, other):
        return [self.person_id, self._int_chrom(), self.pos] > \
            [other.person_id, other._int_chrom(), other.pos]
    
    def _int_chrom(self):
        chrom = self.chrom.strip('chr')
        if chrom not in CHROMS:
            CHROMS[chrom] = max(CHROMS.values()) + 1
        return CHROMS[chrom]
    
    def to_build(self, build):
        ''' shift variant to a different genome build
        '''
        check_build(build)
        build = BUILDS[build]
        
        from_build = LIFTS[self.build]
        to_build = LIFTS[build]
        
        # return unmodified variant if already on the build we want to convert to
        if from_build == to_build:
            return self
        
        key = f'{from_build}-{to_build}'
        if key not in self.lifters:
            self.lifters[key] = get_lifter(from_build, to_build)
        
        try:
            coords = self.lifters[key][self.chrom][self.pos - 1]
        except KeyError:
            logging.warning(f'cannot liftover: {self.chrom}:{self.pos} ' \
                            f'{self.ref}->{self.alt}')
            return None
        if not coords:
            logging.warning(f'cannot liftover: {self.chrom}:{self.pos} ' \
                            f'{self.ref}->{self.alt}')
            return None
        
        # NOTE: This doesn't account for left-aligning indels, or where the
        # NOTE: ref is now the alt. I'm also not rechecking the symbol and
        # NOTE: consequence annotations.
        assert len(coords) == 1
        chrom, pos, strand = coords[0]
        pos += 1
        ref, alt = self.ref, self.alt
        if strand == '-':
            ref = revcomp(self.ref)
            alt = revcomp(self.alt)
        
        return DeNovo(self.person_id, chrom, pos, ref, alt, self.study,
                      self.confidence, build, self.symbol, self.consequence)
