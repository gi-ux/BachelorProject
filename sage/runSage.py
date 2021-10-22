import pandas as pd
import sage
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from glob import glob
import csv
import sys
import importlib

importlib.reload(sage)


def getData(filenames):
    for filename in filenames:
        with open(filename, encoding="utf-8") as fin:
            for line in fin:
                yield line


def run(filenames, max_vocab_size=10000, smoothing=1.):
    if max_vocab_size == 0:
        print("Calculation of the occurrence of each word ...")
        vect = CountVectorizer()
        print("Done !")

    else:
        print(f"Calculation of the occurrence of {max_vocab_size} words ... ")
        vect = CountVectorizer(max_features=max_vocab_size)
        print("Done !")

    filenames = sorted(glob(filenames))
    vocab_filenames = [name for name in filenames]

    X = vect.fit_transform(getData(vocab_filenames))
    vocab = {i: j for j, i in vect.vocabulary_.items()}  # in Python 3 iteritems is removed, fixed

    def getNumLines(filename):
        with open(filename, encoding="utf-8") as fin:
            return len([line for line in fin])

    N = [getNumLines(filename) for filename in filenames]
    idxs = np.array([0] + N).cumsum()
    x = {filename: np.array(X[start:stop, :].sum(axis=0))[0] for filename, start, stop in
         zip(filenames, idxs[:-1], idxs[1:])}

    X_base = np.array(list(x.values())).sum(axis=0)  # in Python 3  x.values() return dict_values, fixed
    mu = np.log(X_base + smoothing) - np.log((X_base + smoothing).sum())
    etas = {filename: sage.estimate(x[filename], mu) for filename in filenames}
    return etas, vect, x, X_base


def write_file(etas, vect, x, outfile_name):
    lst_word = []
    lst_f_count = []
    vocab = {i: j for j, i in vect.vocabulary_.items()}

    for filename, eta in etas.items():
        for word in sage.topK(eta, vocab, 0):
            idx = vect.vocabulary_[word]
            lst_word.append(word)
            lst_f_count.append(x[filename][idx])

    print("Writing file ...")
    df = pd.DataFrame(list(zip(lst_word, lst_f_count,)),
                      columns=["word", "word_count"])
    df.to_csv(f"data/{outfile_name}.csv", index=False, encoding="utf-8")
    print("Done !")


def printEtaCSV(etas, vect, x, X_base, num_keywords=25):
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
