
class Hashdict(dict):
    def __hash__(self):
        return hash((frozenset(self), frozenset(self.values())))
