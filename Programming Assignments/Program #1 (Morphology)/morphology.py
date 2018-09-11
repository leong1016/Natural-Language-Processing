import sys

class Morphology:

    def __init__(self):
        self.args = sys.argv
        self.dict = {}
        self.rules = []
        self.test = []

    def read_dict(self, filepath=None):
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
        if filepath is None:
            filepath = self.args[2]
        with open(filepath, 'r') as f:
            for i, line in enumerate(f):
                record = line.split()
                record.pop(4)
                record.pop(-1)
                dictionary = {'loc': record[0],
                              'add': record[1],
                              'delete': '' if (record[2]=='-') else record[2],
                              'frompos': record[3],
                              'topos': record[4]}
                self.rules.append(dictionary)

    def read_test(self, filepath=None):
        if filepath is None:
            filepath = self.args[3]
        with open(filepath, 'r') as f:
            for i, line in enumerate(f):
                record = line.split()
                self.test.append(record[0])

    def match(self, word):

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

    def output(self, word):
        result = self.match(word.lower())
        out = ''
        if result:
            for e in result:
                out += word + ' ' + e[0] + ' ROOT=' + e[1] + ' SOURCE=' + e[2] + '\n'
        else:
            out += word + ' ' + 'noun' + ' ROOT=' + word + ' SOURCE=' + 'default' + '\n'
        return out

if __name__ == "__main__":
    morphology = Morphology()
    morphology.read_dict()
    morphology.read_rules()
    morphology.read_test()

    for t in morphology.test:
        print(morphology.output(t))
