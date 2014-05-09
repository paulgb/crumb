
import tempfile
import subprocess
from sys import argv, exit
import os
import shutil

import pygit2 as git
import xattr


def main():
    if len(argv) <= 1:
        print 'Usage: git qurt command [args...]'
        exit(1)

    command = argv[1:]

    # check if files need to be checked in

    commit = git.Repository('.').head.target.hex
    print 'Cloning revision {}'.format(commit)

    # create a temp directory

    target_directory = tempfile.mkdtemp()

    # check out project in temp directory

    git.clone_repository('./', target_directory)

    # run process (from command-line args)

    process = subprocess.Popen(command, cwd=target_directory)
    result = process.wait()

    # check process status

    print result, target_directory

    # move output files?

    repo = git.Repository(target_directory)
    for fname in repo.status():
        dirpath = os.path.dirname(fname)
        try:
            os.makedirs(dirpath)
        except (OSError, IOError):
            pass
        shutil.move(os.path.join(target_directory, fname), fname)

        attrs = xattr.xattr(fname)
        attrs['created.commit'] = commit

    shutil.rmtree(target_directory)

    # annotate commit?
    


if __name__ == '__main__':
    main()

