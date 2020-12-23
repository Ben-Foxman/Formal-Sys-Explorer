import sys
from termcolor import colored
from rules import RuleManager


class FSys:
    def __init__(self):
        self.alphabet, self.axioms, self.rules = self.get_setup()
        self.manage_interface()

    def __repr__(self):
        return colored("--System Description--\n", "cyan", attrs=['bold']) + "Alphabet: {}\nAxioms: {}\nInference Rules: \n{}"\
            .format("".join(self.alphabet), ",".join(self.axioms), self.rules) +\
               colored("--End of Description--", "cyan", attrs=['bold'])

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
    """
    def get_setup(self):
        s, a, r = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRTSUVWXYZ0123456789-"), [], RuleManager()
        for arg in sys.argv[1:]:
            if len(arg) < 2 or arg[0] not in ['a', 'r', 's'] or arg[1] != '.' or \
                    (arg[0] == 's' and sys.argv.index(arg) != 1):
                print("Usage: [s.x][a.x | r.x]")
                exit(1)

            info = arg[2:]
            if arg[0] == 's':
                if len(info) == 0:
                    self.error_msg("Alphabets must have at least one character.")
                s = sorted(list(set(info)))
                r.set_alphabet(s)
            elif arg[0] == 'a':
                a.append(info)
            else:
                r.add_rule(info)
        if len(a) == 0:
            a.append("".join(s))
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
            else:
                self.error_msg("Invalid command: {}".format(cmd))





f = FSys()





