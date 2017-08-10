import argparse
import fileinput
import re
from utils import *

def main():
    parser = argparse.ArgumentParser(description="Add contraction rules to contraction table")
    parser.add_argument('FILE', default=['-'],
                        help="file with unprocessed contraction rules")
    parser.add_argument('CONTRACTION_TABLE', help="contraction table")
    parser.add_argument('-t', '--table', required=True,
                        help="translation table for converting to dot patterns", dest="TABLE")
    args = parser.parse_args()
    load_table(args.TABLE)
    p = re.compile(r"^#.*|[ \t]*([+-])?(nocross|syllable\*|always|word|begword|endword)[ \t]+([^ \t]+)[ \t]+([^ \t\n]+)([ \t]+(.*))?\n?$")
    rules = []
    for line in fileinput.FileInput(args.CONTRACTION_TABLE, openhook=fileinput.hook_encoded("utf-8")):
        m = p.match(line)
        exit_if_not(m and not m.group(1))
        _, opcode, text, braille, _, comment = m.groups()
        if opcode:
            rule = {"opcode": opcode, "text": text, "braille": braille, "comment": comment}
            rules.append(rule)
    for line in fileinput.FileInput(args.FILE, openhook=fileinput.hook_encoded("utf-8")):
        m = p.match(line)
        if not m:
            printerrln("%s: rule is not valid" % (line,))
            exit(1)
        exit_if_not(m)
        add_or_delete, opcode, text, braille, _, _ = m.groups()
        if opcode:
            comment = braille
            if comment.endswith('\\'):
                comment = comment + " "
            braille = to_dot_pattern(braille)
            rules, rule = partition(lambda rule: rule["opcode"] == opcode and
                                                 rule["text"] == text and
                                                 rule["braille"] == braille,
                                    rules)
            rule = list(rule)
            if add_or_delete == '-':
                if not rule:
                    printerrln("%s %s %s: rule can not be deleted because not in %s" % (opcode,text,braille,args.CONTRACTION_TABLE))
                    exit(1)
            else:
                if rule:
                    printerrln("%s %s %s: rule can not be added because already in %s" % (opcode,text,braille,args.CONTRACTION_TABLE))
                    exit(1)
                rule = {"opcode": opcode, "text": text, "braille": braille, "comment": comment}
                rules.append(rule)
    opcode_order = {"word": 1, "syllable*": 2, "nocross": 3, "always": 4, "begword": 5, "endword": 6}
    for rule in sorted(rules, key=lambda rule: (rule["text"], opcode_order[rule["opcode"]])):
        println(u"{opcode:<10} {text:<10} {braille:<30} {comment}".format(**rule))

if __name__ == "__main__": main()