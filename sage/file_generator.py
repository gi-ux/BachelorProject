import sage
from glob import glob
import argparse
import importlib
import runSage

importlib.reload(sage)


def main():
    parser = argparse.ArgumentParser(description='run file_generator on ONE file to write .csv file for notebook')
    parser.add_argument('files', type=str,
                        help="This should be a glob of text files, each representing a subset of your corpus.")
    parser.add_argument('--filename', type=str, default="input",
                        help="This is the name of .csv file, if not specified is 'input'.")
    args = parser.parse_args()
    filenames = sorted(glob(args.files))
    vocab_filenames = [name for name in filenames]
    if len(vocab_filenames) > 1:
        print("You only need to pass ONE file and output filename.")
    else:
        etas, vect, x, X_base = runSage.run(args.files, 0, 1.)
        runSage.write_file(etas, vect, x, args.filename)


if __name__ == '__main__':
    main()
