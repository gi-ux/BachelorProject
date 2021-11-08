import sage
import argparse
import importlib
import runSage

importlib.reload(sage)


def main():
    parser = argparse.ArgumentParser(description='run print_info on a set of files to execute SAGE algorithm.')
    parser.add_argument('files', type=str,
                        help="This should be a glob of text files, each representing a subset of your corpus.")
    parser.add_argument('--max_vocab_size', type=int, default=0,
                        help="Total number of words in the vocabulary, sorted by frequency. Larger numbers make it "
                             "slower. If not specified all words will be considered.")
    parser.add_argument('--base_rate_smoothing', type=float, default=1.,
                        help="Larger values cause SAGE to emphasize more high frequency terms.")
    parser.add_argument('--num_keywords', type=int, default=25,
                        help="Number of words shown on screen, not required with --generate True")
    args = parser.parse_args()
    etas, vect, x, X_base = runSage.run(args.files, args.max_vocab_size, args.base_rate_smoothing)
    runSage.printEtaCSV(etas, vect, x, X_base, num_keywords=args.num_keywords)


if __name__ == '__main__':
    main()
