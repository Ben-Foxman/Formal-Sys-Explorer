import sys
import re
from termcolor import colored
from rules import RuleManager


class FSys:
    def __init__(self):
        self.alphabet, self.axioms, self.rules = self.get_setup()
        self.manage_interface()
        self.max_depth = 10
        self.max_amt = 10 ** 12

    def __repr__(self):
        return colored("--Formal System--", "cyan", attrs=['bold']) + colored("\nAlphabet:", attrs=['bold'])\
               + "".join(self.alphabet) + colored("\nAxiom(s):", attrs=['bold']) + ",".join(self.axioms) +\
               colored("\nInference Rule(s):\n", attrs=['bold']) + repr(self.rules) + \
               colored("--End of Formal System--", "cyan", attrs=['bold'])
    @staticmethod
    def error_msg(msg):
        print(colored("FSys:", "red", attrs=['bold']), colored(msg, "white", attrs=['bold']))
    """
    Setup: 
    alphabet -> s.x where x is string containing characters allowed. alphabet must be the first argument
    axiom -> a.x, where x is an axiom
    rule -> r.x, where x is an inference rule of type Rule 
    Last always takes precedence, all axioms checked against alphabet at the end
    
    Defaults: 
    alphabet = alphanumeric + underscore
    axiom = the alphabet in sorted lexicographic order
    rule = the identity rule
    depth = 5
    
    IMPORTANT: behavior is undefined when the alphabet contains any of the following characters: :,;,&,|,<,>,(,),^,$
    As a result, they are banned. 
    """
    def get_setup(self):
        s, a, r = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRTSUVWXYZ0123456789-"), [], RuleManager()
        banned_chars = ":;$|<>()^$"
        count = 0
        with open(sys.argv[1]) as file:
            for arg in file:
                count += 1
                if len(arg) < 2 or arg[0] not in ['a', 'r', 's'] or arg[1] != '.' or \
                        (arg[0] == 's' and count != 1):
                    self.error_msg("Usage: [s.x][a.x | r.x]")
                    exit(1)

                info = arg[2:]
                if arg[0] == 's':
                    for char in info:
                        if char in banned_chars:
                            self.error_msg("{}: contains banned character {}. Stop.".format(info, char))
                            exit(1)
                    if len(info) == 0:
                        self.error_msg("Alphabets must have at least one character.")
                    s = sorted(list(set(info)))
                    r.set_alphabet(s)
                elif arg[0] == 'a':
                    a.append(info)
                # adding a rule
                else:
                    r.add_rule(info)

        # default axiom is string of entire alphabet
        if len(a) == 0:
            a.append("".join(s))

        if len(r.rules) == 0:
            self.error_msg("No inference rules were given.")
        # make sure axioms fit alphabet
        for ax in a:
            for char in ax:
                if char not in s:
                    self.error_msg("Axiom '{}' consists of characters not in alphabet.".format(ax))
                    a.remove(ax)
                    break

        return s, a, r

    def manage_interface(self):
        while True:
            cmd = input(colored("Enter a command. Type \"help\" for a list of commands.\n", attrs=['bold']))
            if cmd == "help":
                with open("help.docs", "r") as file:
                    print("".join(file.readlines()))
            elif cmd == "exit":
                exit(0)
            elif cmd == "print":
                print(self)
            elif cmd[:9] == "maxdepth ":
                if not re.match("\d+", cmd[9:]):
                    self.error_msg("maxdepth: argument must be an integer.")
                else:
                    self.max_depth = min(int(cmd[9:]), (10 ** 3) - 1)
                    print("maxdepth updated: maxdepth={}".format(self.max_depth))
            elif cmd[:7] == "maxamt ":
                if not re.match("\d+", cmd[7:]):
                    self.error_msg("maxamt: argument must be an integer.")
                else:
                    self.max_amt = min(int(cmd[7:]), (10 ** 18) - 1)
                    print("maxamt updated: maxamt={}".format(self.max_amt))
            else:
                self.error_msg("Invalid command: {}".format(cmd))

    # empty strings array -> exhaust requested
    def search_strings(self, strings, longform):
        pass


f = FSys()






