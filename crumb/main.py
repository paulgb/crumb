
import logging
import argparse
import sys

from crumb import Crumb, NotInRepoError


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('--init', '-i', action='store_true')
    parser.add_argument('--export', '-e', nargs='?', default=False)
    parser.add_argument('--run', '-r')
    args = parser.parse_args()

    crumb = Crumb()
    
    try:
        if args.init:
            # placeholder; nothing to initialize yet
            pass
        elif args.export is not False:
            if args.export is None:
                crumb.export(sys.stdout)
            else:
                with open(args.export, 'w') as output:
                    crumb.export(output)
        elif args.run:
            crumb.run(args.run)
        else:
            parser.print_help()

    except NotInRepoError:
        crumb.log.error('Error: must be run inside a git repository')


if __name__ == '__main__':
    main()

