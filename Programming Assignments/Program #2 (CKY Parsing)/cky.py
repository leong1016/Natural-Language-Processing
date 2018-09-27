#!/usr/bin/env python

"""
A syntactic parser that accept two input files: (1) a PCFG file, and (2) a sentences file and then run
either non-probabilistic CYK or probabilistic CKY algorithm. For each sentence in the input file,
it will print three things:
1. PARSING SENTENCE: <sentence>
2. NUMBER OF PARSES FOUND: <number>
3. TABLE: followed by the contents of each cell in the table on a separate line.
"""

__author__ = 'Yulong Liang'
__email__ = 'yulong.liang@utah.edu'

import sys


class CKY:
    def __init__(self):
        """
        Constructor - Description of the instance variables:
        self.args       ::  arguments parsed from command-line, format should be like
                            'cky <pcfg file> <sentences file>' or 'cky.py <pcfg file> <sentences file> -prob'
        self.prob       ::  a boolean variable indicating whether to use probabilistic CKY algorithm
        self.rules      ::  a python list consisting of probabilistic context-free grammar rules in CNF form,
                            one per line. Each rule will have 3 parts:
                            1. left-hand side constituent
                            2. right-hand side constituent(s)
                            3. the probability of the rule
        self.sentences  ::  a python list containing sentences to be parsed, one per line
        """
        self.args = sys.argv
        self.prob = len(self.args) == 4 and self.args[3] == '-prob'
        self.rules = []
        self.sentences = []

    def read_pcfg(self, filepath=None):
        """
        Method for reading pcfg file
        :param filepath: the path of the file, if none then take the second command-line argument
        """
        if filepath is None:
            filepath = self.args[1]

        with open(filepath, 'r') as f:
            for i, line in enumerate(f):
                record = line.split()
                left = record[0]
                right = record[2:-1]
                prob = float(record[-1])
                self.rules.append({'left': left,
                                   'right': right,
                                   'prob': prob})

    def read_sentences(self, filepath=None):
        """
        Method for reading sentences file
        :param filepath: the path of the file, if none then take the third command-line argument
        """
        if filepath is None:
            filepath = self.args[2]

        with open(filepath, 'r') as f:
            for i, line in enumerate(f):
                record = line.split()
                self.sentences.append(record)

    def cky(self, sentence):
        """
        Method for getting the parsing table of a sentence using non-probabilistic CKY parsing
        :param sentence: the sentence to be parsed
        :return: a table containing the parsing result
        """
        length = len(sentence)
        table = [[[] for j in range(length)] for i in range(length)]
        for col in range(0, length):
            word = sentence[col]
            for rule in self.rules:
                if len(rule['right']) == 1 and rule['right'][0] == word:
                    table[col][col].append(rule['left'])
            for row in range(col-1, -1, -1):
                for k in range(0, col):
                    right0 = table[row][k]
                    right1 = table[k+1][col]
                    for rule in self.rules:
                        left = rule['left']
                        right = rule['right']
                        if len(right) != 2:
                            continue
                        for r0 in right0:
                            if right[0] != r0:
                                continue
                            for r1 in right1:
                                if right[1] != r1:
                                    continue
                                table[row][col].append(left)
        return table

    def cky_prob(self, sentence):
        """
        Method for getting the parsing table of a sentence using probabilistic CKY parsing
        :param sentence: the sentence to be parsed
        :return: a table containing the parsing result
        """
        length = len(sentence)
        table = [[[] for j in range(length)] for i in range(length)]
        for col in range(0, length):
            word = sentence[col]
            for rule in self.rules:
                if len(rule['right']) == 1 and rule['right'][0] == word:
                    table[col][col].append({'constituent': rule['left'],
                                            'probability': rule['prob']})
            for row in range(col-1, -1, -1):
                bestProb = 0
                bestLeft = ''
                for k in range(0, col):
                    right0 = table[row][k]
                    right1 = table[k+1][col]
                    for rule in self.rules:
                        if len(rule['right']) != 2:
                            continue
                        for e in right0:
                            if rule['right'][0] != e['constituent']:
                                continue
                            for f in right1:
                                if rule['right'][1] != f['constituent']:
                                    continue
                                prob = e['probability'] * f['probability'] * rule['prob']
                                if prob > bestProb:
                                    bestProb = prob
                                    bestLeft = rule['left']
                if bestLeft == '' and bestProb == 0:
                    continue
                table[row][col].append({'constituent': bestLeft,
                                        'probability': bestProb})
        return table

    def parsing(self, sentence):
        """
        Method for getting the parsing result based on the 'prob' flag
        :param sentence: the sentence to be parsed
        :return: a table containing the parsing result
        """
        if self.prob:
            return self.cky_prob(sentence)
        else:
            return self.cky(sentence)

    def output(self):
        """
        Method for printing the result of parsing
        """
        for s in self.sentences:
            length = len(s)
            table = self.parsing(s)
            print('PARSING SENTENCE: {}'.format(' '.join(s)))
            print('NUMBER OF PARSES FOUND: {}'.format(len(table[0][length-1])))
            print('TABLE:')
            for row in range(0, length):
                for col in range(row, length):
                    if self.prob:
                        constituent = [t['constituent'] for t in table[row][col]]
                        probability = [t['probability'] for t in table[row][col]]
                        idx = [i[0] for i in sorted(enumerate(constituent), key=lambda x: x[1])]
                        result = []
                        for i in idx:
                            result.append(constituent[i]+'('+format(probability[i], '.4f')+')')
                        cell = ' '.join(result)
                    else:
                        cell = ' '.join(sorted(table[row][col]))
                    if cell == '':
                        cell = '-'
                    print('cell[{},{}]: {}'.format(row+1, col+1, cell))
            print('')


if __name__ == '__main__':
    cky = CKY()
    cky.read_pcfg()
    cky.read_sentences()
    cky.output()