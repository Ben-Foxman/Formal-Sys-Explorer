import sys
from termcolor import colored
from rules import RuleManager


class FSys:
    def __init__(self):
        self.alphabet, self.axioms, self.rules, self.depth = self.get_setup()
        print(self.alphabet, self.axioms, self.depth)
        print(self.rules)


    """
    Setup: 
    alphabet -> s.x where x is string containing characters allowed. alphabet must be the first argument
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
    def get_setup(self):
        s, a, r, d = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRTSUVWXYZ0123456789-"), [], RuleManager(), 5
        for arg in sys.argv[1:]:
            if len(arg) < 2 or arg[0] not in ['a', 'r', 'd', 's'] or arg[1] != '.' or \
                    (arg[0] == 's' and sys.argv.index(arg) != 1):
                print("Usage: [s.x][a.x | r.x | d.x]")
                exit(1)

            info = arg[2:]
            if arg[0] == 's':
                if len(info) == 0:
                    self.error_msg("Alphabets must have at least one character.")
                s = sorted(list(set(info)))
                r.set_alphabet(s)
            elif arg[0] == 'a':
                a.append(info)
            elif arg[0] == 'r':
                r.add_rule(info)
            else:
                try:
                    d = int("".join(info))
                except:
                    self.error_msg("{}: invalid depth".format(info))
                    exit(1)
        if len(a) == 0:
            a.append("".join(s))
        # make sure axioms fit alphabet
        for ax in a:
            for char in ax:
                if char not in s:
                    self.error_msg("Axiom '{}' consists of characters not in alphabet.".format(ax))
                    a.remove(ax)
                    break
        return s, a, r, d

    @staticmethod
    def error_msg(msg):
        print(colored("FSys:", "red", attrs=['bold']), colored(msg, "white", attrs=['bold']))


f = FSys()





