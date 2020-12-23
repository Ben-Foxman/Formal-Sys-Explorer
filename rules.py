"""
A grammar rule = a function which maps input of a certain form to corresponding outputs
Rules are given by NAME[regex-list][rule]

NAME
A string indicating the name of the rule.

[regex-list]
A list of regular expressions, separated by a space, where the regex at index n specifies the allowed input format
of the nth argument. Rules with 0 argument are identical to theorems, and thus [regex-list] must
have length greater than or equal to 1. Use the empty string for no additional regex filtering on an input.

1. Regexes only subset the strings which are possible under any given alphabet.
2. Default = match all. The user specifies the [num-arguments] and is prompted for each regex (if any).

[rule]
Defines a rule to perform on the input. The rule is the last argument. Rules are composed of
the following:

------Replacements------
1. Any character not part of another rule
Adds that character to the output string.
2. ${n}, n >= 0
Replaces $n by the nth argument to the rule, or empty string if n >= #args
3. ${.}
Replaces by all arguments to the rule.

------Captures------
1. (){n}
Replace by n copies.
2. (){a:b}
Replace by the substring from a(inclusive) to b(exclusive), using python substring conventions.

------Escapes------
1. \
Escapes the next character. The escape is removed.
------Rules-in-Rules------
1. [NAME]
Replace by rule NAME, with [regex-list] used as inputs. If NAME requires less inputs than the parent NAME,
only the first n arguments are used. If more are required, or NAME is not defined, the empty string is returned.

Note: The [rule] syntax is relatively minimal to try to stay true to the philosophy of formal systems.

"""
import re
from termcolor import colored


class RuleManager:
    def __init__(self):
        self.rules = []
        self.alphabet = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRTSUVWXYZ0123456789-")

    def set_alphabet(self, alphabet):
        self.alphabet = alphabet

    def add_rule(self, rule):
        form = re.match("[A-Za-z_]\w+\.\d+->.*", rule)
        if not form:
            self.error_msg("RuleManager: NAME.[num-arguments]->[rule]")
            exit(1)
        x = rule.find('.')
        y = rule.find("->")
        regexes = ['.*'] * int(rule[x + 1: y])
        name = rule[:x]

        # check if a rule already exists
        if name in [x[0] for x in self.rules]:
            self.error_msg("RuleManager: Rule \"{}\" already exists.".format(name))
        else:
            for i in range(len(regexes)):
                done = False
                #  prompt for specific regexes
                while not done:
                    spec = input("Specify a regex filter on argument ({}) of rule \"{}\"? (y/n) ".format(i, name))
                    if spec in ['y', 'Y', 'yes', 'Yes', 'YES']:
                        new_regex = input("Enter regex: ")
                        try:
                            re.compile(new_regex)
                        except re.error:
                            self.error_msg("RuleManager: Invalid Regex.")
                        else:
                            regexes[i] = new_regex
                            done = True
                    elif spec in ['n', 'N', 'no', 'No', 'NO']:
                        done = True

            self.rules.append([name, regexes, rule[y + 2:]])

            # run once to trigger syntax errors in the rule - don't have to check regexes (regex fails != syntax errors)
            self.run_rule(name, [self.alphabet[0]] * len(regexes), False)

    # takes in rule and argument list - argument list must match the regex
    def run_rule(self, rule, args, regex_check):
        # check that rule has been defined
        rule_list = [x[0] for x in self.rules]
        if rule not in rule_list:
            self.error_msg("RuleManager: Running an undefined rule: {}".format(rule))
            exit(1)
        index = rule_list.index(rule)
        regexes = self.rules[index][1]
        toRun = self.rules[index][2]

        if len(regexes) != len(args):
            self.error_msg("RuleManager: conflicting argument numbers when running rule \"{}\": {} required, {} given."
                  .format(rule, len(regexes), len(args)))
            exit(1)
        if regex_check:
            for pattern, string in zip(regexes, args):
                check = re.match(pattern, string)
                if not check or check.end() != len(string):
                    self.error_msg("RuleManager: Rule \"{}\": Argument \"{}\" does not satisfy regex \"{}\""
                          .format(rule, string, pattern))
                    exit(1)

        # apply the rule
        ans = ""
        while toRun:
            toRun, app = self.eval_rule(toRun, args)
            ans += app
        return ans

    def eval_rule(self, rule, args):
        ans = ""
        replacement = re.match("\$\{(\d+|.)\}", rule)
        # replacement group
        if replacement:
            if rule[2] == '.':
                ans += "".join(args)
            else:
                arg = int(rule[2:replacement.end() - 1])
                if arg < len(args):
                    ans += args[arg]
            rule = rule[replacement.end():]
        # capturing group
        elif rule[0] == '(':
            inside = ""
            rule = rule[1:]
            capturing = True
            while capturing:
                if not rule:
                    self.error_msg("RuleManager: Capture group not closed.")
                    exit(1)
                elif rule[0] == ')':
                    rule = rule[1:]
                    operator = re.match("\{([0-9]+|[0-9]+:[0-9]+)\}", rule)
                    if not operator:
                        self.error_msg("RuleManager: Capture group not equipped with valid operator.")
                        exit(1)
                    rep = operator.group(0)
                    if ':' in rep:
                        divide = rep.index(":")
                        start = int(rep[1:divide])
                        end = int(rep[divide + 1: len(rep) - 1])
                        ans += inside[start:end]
                    else:
                        ans += inside * int(rep[1: len(rep) - 1])
                    rule = rule[len(rep):]
                    capturing = False
                else:
                    rule, app = self.eval_rule(rule, args)
                    inside += app
        # escaped char - escaped char must be in alphabet
        elif rule[0] == '\\':
            if len(rule) > 1:
                if rule[1] not in self.alphabet:
                    self.error_msg("RuleManager: rule cannot add characters to string not in the alphabet: \'{}\'".format(rule[0]))
                    exit(1)
                ans += rule[1]
            rule = rule[2:]
        # normal char - must be in alphabet
        else:
            if rule[0] in self.alphabet:
                ans += rule[0]
                rule = rule[1:]
            else:
                self.error_msg("RuleManager: rule cannot add characters to string not in the alphabet: \'{}\'".format(rule[0]))
                exit(1)
        return rule, ans

    @staticmethod
    def error_msg(msg):
        print(colored("Error:", "red", attrs=['bold']), colored(msg, "white"))


# print(run("(adhgfghf){3}", ['1','2','3','4']))

r = RuleManager()  # new rule manager
a = "r1.2->((${0}){0:1}(${1}){0:1}){2}(bb){0}("  # create a rule (first letter of both arguments concatenated twice)
r.add_rule(a)  # add it to the list of rules
ans = r.run_rule("r1", ["ab", "cd"], True)  # run it on the input 'x', 'y'
print(ans)