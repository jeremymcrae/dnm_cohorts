
import random

def random_id(size=12):
    """ make a random character string for semi-unique IDs
    
    Args:
        size: length of string to return. 12 characters should mean a 50% chance
        of string collisions only after 20 million random strings.
    
    Returns:
        random character string
    """
    
    def is_number(string):
        try:
            number = float(string)
            return True
        except ValueError:
            return False
    
    # don't allow the random strings to be equivalent to a number. This reduces
    # the randomness, but enforces evaluation as a string.
    string = None
    while string is None or is_number(string) or len(string) != size:
        string = "{:x}".format(random.getrandbits(size*4))
        string = string.strip()
    
    return string
