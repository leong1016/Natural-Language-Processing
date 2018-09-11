import sys


class Morphology:

    def __init__(self):
        args = sys.argv
        if len(args) != 4:
            raise ValueError('File arguments not equal to 3.')

        self.dict = {}
        self.rules = []
        self.test = []

        self.read_dict(args[1])
        self.read_rules(args[2])
        self.read_test(args[3])

    def read_dict(self, filepath):
        with open(filepath, 'r') as f:
            for i, line in enumerate(f):
                record = line.split()
                dictionary = {'pos': record[1],
                              'root': record[3] if (len(record) > 2 and record[2] == 'ROOT') else record[0]}
                if record[0] in self.dict:
                    self.dict[record[0]].append(dictionary)
                else:
                    self.dict[record[0]] = [dictionary]

    def read_rules(self, filepath):
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

    def read_test(self, filepath):
        with open(filepath, 'r') as f:
            for i, line in enumerate(f):
                record = line.split()
                self.test.append(record[0])

    # def find(self, word):
    #     result = word
    #     if word in self.dict:
    #         info = self.dict[word]
    #         result += ' ' + info['pos'] + ' ROOT=' + info['root'] + ' SOURCE=dictionary'
    #     else:
    #         info = self.match(word)
    #         if info is None:
    #             result += ' noun ROOT=' + word + ' SOURCE=default'
    #         else:
    #             result += ' ' + info['pos'] + ' ROOT=' + info['root'] + ' SOURCE=morphology'
    #     print(result)
    #     return result

    def match(self, word):

        result = []

        if word in self.dict:
            records = self.dict[word]
            for r in records:
                result.append([r['pos'], r['root'], 'default'])
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
            elif loc == 'SUFFIX' and word[-len(add):] == add:
                original = word[:-len(add)] + delete
            else:
                continue
            info = self.match(original)
            if info:
                for i in info:
                    if i[0] == frompos:
                        result.append((topos, i[1], 'morphology'))
        return result

if __name__ == "__main__":
    morphology = Morphology()

    # print(morphology.dict)
    # print(morphology.test)
    # print(morphology.suffix)
    # print(morphology.prefix)

    for t in morphology.test:
        print(morphology.match(t))