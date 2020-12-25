import sys
import re
import itertools
import time
from termcolor import colored
from rules import RuleManager


class FSys:
    def __init__(self):
        self.alphabet, self.axioms, self.rule_list = self.get_setup()
        self.max_depth = 10
        self.max_len = 100
        # theorems: string, iteration found, path
        self.theorems = [[ax, 0] for ax in self.axioms]
        # searched = #iterations already calculated
        self.searched = 0
        self.manage_interface()

    def __repr__(self):
        return colored("--Formal System--", "cyan", attrs=['bold']) + colored("\nAlphabet:", attrs=['bold'])\
               + "".join(self.alphabet) + colored("\nAxiom(s):", attrs=['bold']) + ",".join(self.axioms) +\
               colored("\nInference Rule(s):\n", attrs=['bold']) + repr(self.rule_list) + \
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
    
    IMPORTANT: behavior is undefined when the alphabet contains any of the following characters: :,;,&,|,<,>,(,),^,$
    As a result, they are banned. 
    """
    def get_setup(self):
        s, a, r = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRTSUVWXYZ0123456789-"), [], RuleManager()
        banned_chars = ":;$|<>()^$"
        count = 0
        with open(sys.argv[1]) as file:
            for arg in file:
                arg = arg.strip()  # remove trailing newlines
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
                    good = True
                    for char in info:
                        if char not in s:
                            self.error_msg(
                                "Axiom '{}' consists of characters not in alphabet. It will be discarded.".format(info))
                            good = False
                            break
                    if good:
                        a.append(info)
                # adding a rule
                else:
                    r.add_rule(info)

        # default axiom is string of entire alphabet
        if len(a) == 0:
            a.append("".join(s))
        else:
            # remove duplicates
            a = list(set(a))

        if len(r.rules) == 0:
            self.error_msg("No inference rules were given.")
        # make sure axioms fit alphabet
        return s, a, r

    def manage_interface(self):
        count = 1
        while True:
            cmd = input(colored("({}) ".format(count), attrs=['bold'])).split()
            if not cmd:
                continue
            if cmd[0] == "help":
                with open("help.docs", "r") as file:
                    print("".join(file.readlines()))
            elif cmd[0] == "exit":
                exit(0)
            elif cmd[0] == "print":
                print(self)
            elif cmd[0] == "maxdepth":
                if len(cmd) == 1:
                    print("maxdepth={}".format(self.max_depth))
                elif not re.match("\d+", cmd[1]):
                    self.error_msg("maxdepth: argument must be an integer.")
                else:
                    self.max_depth = min(int(cmd[1]), (10 ** 3) - 1)
                    print("maxdepth updated: maxdepth={}".format(self.max_depth))
            elif cmd[0] == "maxlen":
                if len(cmd) == 1:
                    print("maxlen={}".format(self.max_len))
                elif not re.match("\d+", cmd[1]):
                    self.error_msg("maxlen: argument must be an integer.")
                else:
                    self.max_len = min(int(cmd[1]), (10 ** 4) - 1)
                    print("maxlen updated: maxlen={}".format(self.max_len))
            elif cmd[0] == "target" or cmd[0] == "exhaust":
                if len(cmd) >= 2 and cmd[1] == "-l":
                    if cmd[0] == "target":
                        self.search_strings(cmd[2:], longform=True)
                    else:
                        self.search_strings([], longform=True)
                else:
                    if cmd[0] == "target":
                        self.search_strings(cmd[1:], longform=False)
                    else:
                        self.search_strings([], longform=False)
            else:
                self.error_msg("Invalid command: {}".format("".join(cmd)))
                count -= 1
            count += 1

    # empty strings array -> exhaust requested
    def search_strings(self, strings, longform):
        targets = []
        # check previously calculated theorems for targets
        for thm in self.theorems:
            # theorem already calculated
            if thm[0] in strings:
                targets.append(thm)
                strings.remove(thm[0])
                if not strings:
                    self.print_info(targets, targets, longform)
                    return

        for i in range(self.searched + 1, self.max_depth + 1):
            old_thms = [x[0] for x in self.theorems]
            new_thms = []
            # for each rule specified
            for rule in self.rule_list.rules:
                # for each group of theorem input
                for inputs in itertools.product(old_thms, repeat=len(rule[1])):
                    good_in = True
                    # for each theorem
                    for j in range(len(inputs)):
                        # if regex fails
                        match = re.match(rule[1][j], inputs[j])
                        if not match or match.end() != len(inputs[j]):
                            good_in = False
                            break
                    # run the input on the rule
                    if good_in:
                        output = self.rule_list.run_rule(rule[0], inputs, False)
                        if len(output) <= self.max_len and output not in old_thms and output not in new_thms:
                            new_thms.append(output)
                            # target?
                            if output in strings:
                                targets.append([output, i])
                                strings.remove(output)
                                if not strings:
                                    self.print_info(targets, targets, longform)
                                    return
            # add depth to new_thms
            new_thms = [[x, i] for x in new_thms]
            self.theorems.extend(new_thms)
            # update searched depth
            self.searched = i
        self.print_info(strings, targets, longform)

    def print_info(self, strings, targets, longform):
        # print everything out
        colors = ['yellow', 'blue', 'magenta']
        if longform:
            print("--Overall Search Information--")
            print("Maximum Search Depth: {}".format(self.max_depth))
            print("Maximum string length: {}".format(self.max_len))
        if strings:
            if not targets:
                print(colored("No targets found.", attrs=['bold']))
            else:
                for t in targets:
                    if t[1] <= self.max_depth and len(t[0]) <= self.max_len:
                        print(colored("{} found at depth={}".format(t[0], t[1]), colors[t[1] % 3], attrs=['bold']))
        else:
            for t in self.theorems:
                if t[1] <= self.max_depth and len(t[0]) <= self.max_len:
                    print(colored("depth={}: {}".format(t[1], t[0]), colors[t[1] % 3], attrs=['bold']))


f = FSys()

