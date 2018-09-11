#!/usr/bin/env python

"""
A morphological analysis program that accept (1) a dictionary file and (2) a rules file and
output the word definition (Part-of-Speech, Root, Source) for each word in (3) a test file
in the following format:
<word> <pos> ROOT=<root> SOURCE=<source>
"""

__author__ = 'Yulong Liang'
__email__ = "yulong.liang@utah.edu"

import sys


class Morphology:
    def __init__(self):
        """
        Constructor - Description of the instance variables:
        self.args   ::  arguments parsed from command-line, format should be like
                        'morphology.py <dictionary file> <rules file> <test file>'
        self.dict   ::  a python dictionary consisting of words paired with their possible parts-of-speech (POS)
        self.rules  ::  a python list consisting of morphology rules, one per line. Each rule will have 5 parts:
                        1. PREFIX or SUFFIX keyword
                        2. beginning or ending characters (relative to the prefix/suffix keyword)
                        3. replacement characters, or a hyphen if no characters should be replaced
                        4. the part-of-speech tag required for the originating word from which the new word is derived
                        5. the part-of-speech tag that will be assigned to the new (derived) word
        self.test   ::  a python list containing words to be analyzed, one per line
        """
        self.args = sys.argv
        self.dict = {}
        self.rules = []
        self.test = []

    def read_dict(self, filepath=None):
        """
        Method for reading dictionary file
        :param filepath: the path of the file, if none then take the second command-line argument
        """
        if filepath is None:
            filepath = self.args[1]
        with open(filepath, 'r') as f:
            for i, line in enumerate(f):
                record = line.split()
                dictionary = {'pos': record[1],
                              'root': record[3] if (len(record) > 2 and record[2] == 'ROOT') else record[0]}
                if record[0] in self.dict:
                    self.dict[record[0]].append(dictionary)
                else:
                    self.dict[record[0]] = [dictionary]

    def read_rules(self, filepath=None):
        """
        Method for reading rules file
        :param filepath: the path of the file, if none then take the third command-line argument
        """
        if filepath is None:
            filepath = self.args[2]
        with open(filepath, 'r') as f:
            for i, line in enumerate(f):
                record = line.split()
                record.pop(4)
                record.pop(-1)
                dictionary = {'loc': record[0],
                              'add': record[1],
                              'delete': '' if (record[2] == '-') else record[2],
                              'frompos': record[3],
                              'topos': record[4]}
                self.rules.append(dictionary)

    def read_test(self, filepath=None):
        """
        Method for reading test file
        :param filepath: the path of the file, if none then take the fourth command-line argument
        """
        if filepath is None:
            filepath = self.args[3]
        with open(filepath, 'r') as f:
            for i, line in enumerate(f):
                record = line.split()
                self.test.append(record[0])

    def match(self, word):
        """
        Method to recursively search for matching of the given word based on the rules and dictionary
        :param word: the word to be analyzed
        :return: a python list of all the possible matching
        """
        result = set()

        if word in self.dict:
            records = self.dict[word]
            for r in records:
                result.add((r['pos'], r['root'], 'dictionary'))
            return result

        for r in self.rules:
            loc = r['loc']
            add = r['add']
            delete = r['delete']
            frompos = r['frompos']
            topos = r['topos']
            original = ''
            if loc == 'PREFIX' and word[0:len(add)] == add:
                original = delete + word[len(add):]
                info = self.match(original)
                if info:
                    for i in info:
                        if i[0] == frompos:
                            result.add((topos, i[1], 'morphology'))
            if loc == 'SUFFIX' and word[-len(add):] == add:
                original = word[:-len(add)] + delete
                info = self.match(original)
                if info:
                    for i in info:
                        if i[0] == frompos:
                            result.add((topos, i[1], 'morphology'))
        return result

    def output(self, rawword):
        """
        Method that takes a word and calls the morphology rule matching method,
        then returns the result of matching in a given format
        :param word: the word to be analyzed
        :return: a string contains definition(s) in a given format, each definition in a separate line
        """
        word = rawword.lower()
        result = self.match(word)
        out = ''
        if result:
            for e in result:
                out += word + ' ' + e[0] + ' ROOT=' + e[1] + ' SOURCE=' + e[2] + '\n'
        else:
            out += word + ' ' + 'noun' + ' ROOT=' + word + ' SOURCE=' + 'default' + '\n'
        return out

    def process(self):
        for t in self.test:
            print(self.output(t))


if __name__ == "__main__":      # code to execute if called from command-line
    morphology = Morphology()
    morphology.read_dict()
    morphology.read_rules()
    morphology.read_test()
    morphology.process()