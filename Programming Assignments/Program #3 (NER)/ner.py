#!/usr/bin/env python

"""
Collins & Singer bootstrapping algorithm for Named Entity Recognition (NER)
"""

__author__ = 'Yulong Liang'
__email__ = 'yulong.liang@utah.edu'

import sys
import re
import pandas as pd


class NER:

    def __init__(self):
        """
        Constructor - Description of the instance variables:
        self.args               ::  arguments parsed from command-line, format should be like
                                    'ner <seed rules> <training data> <test data>'
        self.seed               ::  a dictionary of seed rules
        self.training_data      ::  a python list consisting of training examples
        self.testing_data       ::  a python list consisting of testing examples
        self.dlist_spelling     ::  a dictionary storing the spelling rules
        self.dlist_context      ::  a dictionary storing the context rules
        """
        self.args = sys.argv
        self.seed = None
        self.training_data = None
        self.testing_data = None
        self.dlist_spelling = {}
        self.dlist_context = {}

    def read_seed(self, filepath=None):
        """
        Method for reading seed rule file
        :param filepath: the path of the file, if none then take the second command-line argument
        """
        self.seed = {}
        if filepath is None:
            filepath = self.args[1]
        with open(filepath, 'r') as f:
            for i, line in enumerate(f):
                item = line.split()
                type = item[0]
                contain = item[1]
                aclass = item[3]
                if type == 'SPELLING':
                    self.seed[contain[9:-1]] = {'CLASS': aclass,
                                                'PROB': -1.000,
                                                'FREQ': -1}
                else:
                    raise ValueError
        self.dlist_spelling.update(self.seed)

    def read_train(self, filepath=None):
        """
        Method for reading training example file
        :param filepath: the path of the file, if none then take the second command-line argument
        """
        self.training_data = []
        if filepath is None:
            filepath = self.args[2]
        with open(filepath, 'r') as f:
            text = f.read()
            data = re.split(r'\s*\n\s*', text)
            for i in range(0, len(data)-1, 2):
                item = {'CONTEXT': data[i][9:].split(' '),
                        'NP': data[i+1][4:].split(' '),
                        'CLASS': None}
                self.training_data.append(item)

    def read_test(self, filepath=None):
        """
        Method for reading testing example file
        :param filepath: the path of the file, if none then take the second command-line argument
        """
        self.testing_data = []
        if filepath is None:
            filepath = self.args[3]
        with open(filepath, 'r') as f:
            text = f.read()
            data = re.split(r'\s*\n\s*', text)
            for i in range(0, len(data)-1, 2):
                item = {'CONTEXT': data[i][9:].split(' '),
                        'NP': data[i+1][4:].split(' '),
                        'CLASS': None}
                self.testing_data.append(item)

    def train(self, n_iteration=3):
        """
        A wrapper method for running the algorithm on training data
        :param n_iteration: number of iterations of running Collins & Singer algorithm
        """
        seed = self.seed
        instance = self.training_data

        print('SEED DECISION LIST\n')
        self.print_dict(seed, 'SPELLING')
        for i in range(n_iteration):
            seed, instance = self.collins_singer(i, seed, instance)

        print('\nFINAL DECISION LIST\n')
        self.print_dict(self.dlist_spelling, 'SPELLING')
        self.print_dict(self.dlist_context, 'CONTEXT')

    def apply(self):
        """
        A wrapper method for applying learned rules on testing data
        """
        for i in self.testing_data:
            # spelling
            if i['CLASS'] is not None:
                continue
            np = i['NP']
            for k, v in self.dlist_spelling.items():
                if k in np:
                    i['CLASS'] = v['CLASS']
                    break
            # context
            if i['CLASS'] is not None:
                continue
            context = i['CONTEXT']
            for k, v in self.dlist_context.items():
                if k in context:
                    i['CLASS'] = v['CLASS']
                    break
        print('\nAPPLYING FINAL DECISION LIST TO TEST INSTANCES\n')
        self.print_instance(self.testing_data)

    def collins_singer(self, i, seed, instance, n_best=2, min_prob=0.8, min_freq=5):
        """
        The core method for Collins & Singer algorithm
        :param i: the number of current iteration
        :param seed: a python dictionary of seed rules
        :param instance: a python list of current examples
        :param n_best: the number of rules to generate
        :param min_prob: the threshold for probability
        :param min_freq: the threshold for frequency
        :return: learned spelling rules and examples after applying the learned rules (only for next iteration)
        """
        instance1 = self.apply_spelling(seed, instance)
        stats_context = self.induce_context(instance1)
        best_context = self.get_best(stats_context, n_best, min_prob, min_freq)
        print('\nITERATION #{}: NEW CONTEXT RULES\n'.format(i+1))
        self.print_dict(best_context, 'CONTEXT')
        self.dlist_context.update(best_context)

        instance2 = self.apply_context(best_context, instance1)
        stats_spelling = self.induce_spelling(instance2)
        best_spelling = self.get_best(stats_spelling, n_best, min_prob, min_freq)
        print('\nITERATION #{}: NEW SPELLING RULES\n'.format(i+1))
        self.print_dict(best_spelling, 'SPELLING')
        self.dlist_spelling.update(best_spelling)

        return best_spelling, instance2

    def apply_spelling(self, rules, instance):
        for i in instance:
            if i['CLASS'] is not None:
                continue
            for k, v in rules.items():
                if k in i['NP']:
                    i['CLASS'] = v['CLASS']
                    break
        return instance

    def apply_context(self, rules, instance):
        for i in instance:
            if i['CLASS'] is not None:
                continue
            for k, v in rules.items():
                if k in i['CONTEXT']:
                    i['CLASS'] = v['CLASS']
                    break
        return instance

    def induce_context(self, instance):
        stats = {}
        for i in instance:
            aclass = i['CLASS']
            context = i['CONTEXT']
            if aclass is None:
                continue
            for word in context:
                if word in self.dlist_context:
                    continue
                if word not in stats:
                    stats[word] = {'LOCATION': 0, 'ORGANIZATION': 0, 'PERSON': 0}
                stats[word][aclass] += 1
        return stats

    def induce_spelling(self, instance):
        stats = {}
        for i in instance:
            aclass = i['CLASS']
            spelling = i['NP']
            if aclass is None:
                continue
            for word in spelling:
                if word in self.dlist_spelling:
                    continue
                if word not in stats:
                    stats[word] = {'LOCATION': 0, 'ORGANIZATION': 0, 'PERSON': 0}
                stats[word][aclass] += 1
        return stats

    def get_best(self, stats, n_best, min_prob, min_freq):
        table = self.best_table(stats, n_best, min_prob, min_freq)
        result = {}
        for i, r in table.iterrows():
            result[i] = {'CLASS': r['CLASS'],
                         'PROB': r['PROB'],
                         'FREQ': r['FREQ']}
        return result

    def best_table(self, stats, n_best, min_prob, min_freq):
        table = pd.DataFrame.from_dict(stats, orient='index')
        table['SUM'] = table.sum(axis=1)
        table['LOC_PROB'] = table['LOCATION'] / table['SUM']
        table['ORG_PROB'] = table['ORGANIZATION'] / table['SUM']
        table['PER_PROB'] = table['PERSON'] / table['SUM']

        # location
        loc = table[(table['LOC_PROB'] >= min_prob) & (table['LOCATION'] >= min_freq)]
        loc = loc.sort_values(by=['LOC_PROB', 'LOCATION'], ascending=False)
        n_loc = min(n_best, loc.shape[0])
        df_loc = self.modify(loc[:n_loc].copy(), 'LOCATION')

        # organization
        org = table[(table['ORG_PROB'] >= min_prob) & (table['ORGANIZATION'] >= min_freq)]
        org = org.sort_values(by=['ORG_PROB', 'ORGANIZATION'], ascending=False)
        n_org = min(n_best, org.shape[0])
        df_org = self.modify(org[:n_org].copy(), 'ORGANIZATION')

        # person
        per = table[(table['PER_PROB'] >= min_prob) & (table['PERSON'] >= min_freq)]
        per = per.sort_values(by=['PER_PROB', 'PERSON'], ascending=False)
        n_per = min(n_best, per.shape[0])
        df_per = self.modify(per[:n_per].copy(), 'PERSON')

        result = pd.concat([df_loc, df_org, df_per])
        result = result.sort_index().sort_values(by=['PROB', 'FREQ'], ascending=False)
        return result

    @staticmethod
    def modify(df, aclass):
        df['FREQ'] = df.iloc[:,0:3].max(axis=1)
        df['PROB'] = df.iloc[:,4:7].max(axis=1)
        df['CLASS'] = aclass
        return df.iloc[:,-3:]

    @staticmethod
    def print_dict(d, type):
        for k, v in d.items():
            print('{0:s} Contains({1:s}) -> {2:s} (prob={3:.3f} ; freq={4:d})'.format(type, k, v['CLASS'], v['PROB'], v['FREQ']))

    @staticmethod
    def print_instance(d):
        for i in d:
            print('CONTEXT: {}'.format(' '.join(i['CONTEXT'])))
            print('NP: {}'.format(' '.join(i['NP'])))
            print('CLASS: {}'.format(i['CLASS'] if i['CLASS'] is not None else 'NONE'))
            print()


if __name__ == "__main__":
    ner = NER()
    ner.read_seed()
    ner.read_train()
    ner.read_test()
    ner.train()
    ner.apply()