import sys
from rules import parse_rule


class FSys:
    def __init__(self):
        self.alphabet, self.axioms, self.rules, self.depth = self.get_setup()
        print(self.alphabet, self.axioms, self.rules, self.depth)

    """
    Setup: 
    alphabet -> s.x, where x is string containing characters allowed
    axiom -> a.x, where x is an axiom
    rule -> r.x, where x is an inference rule of type Rule 
    depth d.x, where x > 0
    Last always takes precedence, all axioms checked against alphabet at the end
    
    Defaults: 
    alphabet = alphanumeric + underscore
    axiom = the alphabet in sorted lexicographic order
    rule = the identity rule
    depth = 5
    """
    @staticmethod
    def get_setup():
        s, a, r, d = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRTSUVWXYZ0123456789-"), [], [], 5
        for arg in sys.argv[1:]:  # run with python3...
            if len(arg) < 2 or arg[0] not in ['a', 'r', 'd', 's'] or arg[1] != '.':
                print("Usage: [s.x | a.x | r.x | d.x]")
                exit(1)

            info = arg[2:]

            if arg[0] == 's':
                s = sorted(list(set(info)))
            elif arg[0] == 'a':
                a.append(info)
            elif arg[0] == 'r':
                r.append(parse_rule(info))
            else:
                try:
                    d = int("".join(info))
                except TypeError:
                    print("Error: {}: invalid depth".format(info))
                    exit(1)
            # make sure axioms fit alphabet
            for ax in a:
                for char in ax:
                    if char not in s:
                        print("Error: Axiom '{}' consists of characters not in alphabet.".format(ax))
                        a.remove(ax)
                        break
        return s, a, r, d


f = FSys()





