import pandas as pd
import sage
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from glob import glob
import csv
import argparse
import sys
import importlib
import time

importlib.reload(sage)


def main():
    parser = argparse.ArgumentParser(description='run SAGE on a set of files [to print info] or one file [to write '
                                                 '.csv file for notebook]')
    parser.add_argument('files', type=str,
                        help="This should be a glob of text files, each representing a subset of your corpus.")
    parser.add_argument('--generate', type=bool, default=False,
                        help="If provided, a .csv file will be generated for Notebook. If True you only need to pass "
                             "ONE file")
    parser.add_argument('--filename', type=str, default="input",
                        help="This is the name of .csv file, if not specified is 'input'.")
    parser.add_argument('--max_vocab_size', type=int, default=0,
                        help="Total number of words in the vocabulary, sorted by frequency. Larger numbers make it "
                             "slower. If not specified all words will be considered.")
    parser.add_argument('--base_rate_smoothing', type=float, default=1.,
                        help="Larger values cause SAGE to emphasize more high frequency terms.")
    parser.add_argument('--num_keywords', type=int, default=25,
                        help="Number of words shown on screen, not required with --generate True")
    args = parser.parse_args()

    etas, vect, x, X_base = runSage(args.files, args.max_vocab_size, args.base_rate_smoothing)
    if args.generate is False:
        printEtaCSV(etas, vect, x, X_base, num_keywords=args.num_keywords)
    else:
        filenames = sorted(glob(args.files))
        vocab_filenames = [name for name in filenames]
        if len(vocab_filenames) > 1:
            print("Using --generate you only need to pass ONE file")
        else:
            write_file(etas, vect, x, X_base, 0, args.filename)


def getData(filenames):
    for filename in filenames:
        with open(filename, encoding="utf-8") as fin:
            for line in fin:
                yield line


def runSage(filenames, max_vocab_size=10000, smoothing=1.):
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


def write_file(etas, vect, x, X_base, num_keywords, outfile_name):
    lst_word = []
    lst_f_count = []
    lst_f_rate = []
    lst_base_count = []
    lst_base_rate = []
    lst_sage = []
    vocab = {i: j for j, i in vect.vocabulary_.items()}

    for filename, eta in etas.items():
        for word in sage.topK(eta, vocab, num_keywords):
            idx = vect.vocabulary_[word]
            lst_word.append(word)
            lst_sage.append(eta[idx])
            lst_f_count.append(x[filename][idx])
            lst_f_rate.append(x[filename][idx] / float(x[filename].sum()))
            lst_base_count.append(X_base[idx])
            lst_base_rate.append(X_base[idx] / float(X_base.sum()))

    print("Writing file ...")
    df = pd.DataFrame(list(zip(lst_word, lst_sage, lst_f_count,
                               lst_f_rate, lst_base_count, lst_base_rate)),
                      columns=["word", "sage", "file_count", "file_rate", "base_count", "base_rate"])
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


if __name__ == '__main__':
    main()
