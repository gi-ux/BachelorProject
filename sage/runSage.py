import pandas as pd
import sage
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from glob import glob
import csv
import argparse
import sys


## todos
# Code cleanup: function default arguments should come from the parser
# Make it easier to specify custom tokenizers

def main():
    parser = argparse.ArgumentParser(description='run SAGE on a set of files')
    parser.add_argument('files', type=str,
                        help="This should be a glob of text files, each representing a subset of your corpus.")
    parser.add_argument('--basefile', type=str, default=None,
                        help="If provided, the baseline probability model will be computed from this file. Otherwise, "
                             "it will be computed from the sum of counts across the corpus.")
    parser.add_argument('--max_vocab_size', type=int, default=10000,
                        help="Total number of words in the vocabulary, sorted by frequency. Larger numbers make it "
                             "slower.")
    parser.add_argument('--base_rate_smoothing', type=float, default=1.,
                        help="Larger values cause SAGE to emphasize more high frequency terms.")
    parser.add_argument('--num_keywords', type=int, default=25)
    args = parser.parse_args()

    etas, vect, x, X_base = runSage(args.files, args.basefile, args.max_vocab_size, args.base_rate_smoothing)
    printEtaCSV(etas, vect, x, X_base, num_keywords=args.num_keywords)


def getData(filenames):
    for filename in filenames:
        with open(filename, encoding="utf-8") as fin:
            for line in fin:
                yield line


def runSage(filenames, base_file=None, max_vocab_size=10000, smoothing=1.):
    # build the vocabulary
    vect = CountVectorizer(max_features=max_vocab_size)
    filenames = sorted(glob(filenames))
    vocab_filenames = [name for name in filenames]  # deep copy?
    if base_file is not None:
        vocab_filenames += [base_file]

    X = vect.fit_transform(getData(vocab_filenames))
    vocab = {i: j for j, i in vect.vocabulary_.items()}  # in Python 3 iteritems is removed, fixed

    def getNumLines(filename):
        with open(filename, encoding="utf-8") as fin:
            return len([line for line in fin])

    N = [getNumLines(filename) for filename in filenames]
    idxs = np.array([0] + N).cumsum()
    x = {filename: np.array(X[start:stop, :].sum(axis=0))[0] for filename, start, stop in
         zip(filenames, idxs[:-1], idxs[1:])}

    if base_file is not None:
        X_base = np.array(X[idxs[-1]:, :].sum(axis=0))[0]
    else:
        X_base = np.array(list(x.values())).sum(axis=0)  # in Python 3  x.values() return dict_values, fixed

    mu = np.log(X_base + smoothing) - np.log((X_base + smoothing).sum())

    etas = {filename: sage.estimate(x[filename], mu) for filename in filenames}

    return etas, vect, x, X_base


def printEtaCSV(etas, vect, x, X_base, num_keywords=25):
    lst_word = []
    lst_f_count = []
    lst_f_rate = []
    lst_base_count = []
    lst_base_rate = []
    lst_sage = []
    writer = csv.DictWriter(sys.stdout, fieldnames=['source',
                                                    'word',
                                                    'sage',
                                                    'base_count',
                                                    'base_rate',
                                                    'file_count',
                                                    'file_rate'],
                            delimiter='\t'
                            )
    writer.writeheader()
    vocab = {i: j for j, i in vect.vocabulary_.items()}
    for filename, eta in etas.items():
        # printEtaCSV(fname+'-sage.csv',eta,vect,x[i],mu,num_keywords=args.num_keywords)
        # with open(filename,'w') as fout:
        for word in sage.topK(eta, vocab, num_keywords):
            idx = vect.vocabulary_[word]
            writer.writerow({'source': filename,
                             'word': word,
                             'sage': eta[idx],
                             'file_count': x[filename][idx],
                             'file_rate': x[filename][idx] / float(x[filename].sum()),
                             'base_count': X_base[idx],
                             'base_rate': X_base[idx] / float(X_base.sum())
                             })
            lst_word.append(word)
            lst_sage.append(eta[idx])
            lst_f_count.append(x[filename][idx])
            lst_f_rate.append(x[filename][idx] / float(x[filename].sum()))
            lst_base_count.append(X_base[idx])
            lst_base_rate.append(X_base[idx] / float(X_base.sum()))

    df = pd.DataFrame(list(zip(lst_word, lst_sage, lst_f_count,
                      lst_f_rate, lst_base_count, lst_base_rate)),
                      columns=["word", "sage", "file_count", "file_rate", "base_count", "base_rate"])
    df.to_csv("data/input.csv", index=False, encoding="utf-8")
    # with open('data/output.tsv', 'wt') as out_file:
    #     tsv_writer = csv.writer(out_file, delimiter='\t')
    #     for i in range(len(lst_word)):
    #         tsv_writer.writerow([lst_word[i], lst_f_count[i]])


if __name__ == '__main__':
    main()
