#! /usr/bin/env python
import argparse
import sys
import votes_calculator


def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--voters-file', required=True, help='filename of voters list')
    parser.add_argument(
        'bulletins_hash', help='hash of bulletins list in IPFS')
    return parser.parse_args()


def main():
    args = parse_arguments(sys.argv[1:])
    calc = votes_calculator.VotingResultCalculator(args.voters_file)
    calc.load_bulletins(args.bulletins_hash)
    results = calc.calculate()
    for item in results:
        print('%s: %s' % (item['vote'], item['percent']))


if __name__ == '__main__':
    main()
