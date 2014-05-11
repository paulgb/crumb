
import tempfile
import subprocess
from sys import argv, exit
import os
import shutil
import logging

import pygit2 as git
import xattr

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def main():
    if len(argv) <= 1:
        print 'Usage: git qurt command [args...]'
        exit(1)

    command = argv[1:]
    log.info('Command: {}'.format(' '.join(command)))

    # check if files need to be checked in

    repo_dir = git.discover_repository('.')
    repo = git.Repository(repo_dir)

    log.info('Found git repo in {}'.format(repo.workdir))

    commit = repo.head.target.hex

    log.info('Last commit: {} ({})'.format(commit, repo.head.log().next().message))

    # create a temp directory

    target_directory = tempfile.mkdtemp()
    log.info('Working in temp directory: {}'.format(target_directory))

    # check out project in temp directory

    log.info('Cloning repository')
    git.clone_repository(repo.workdir, target_directory)
    log.info('Done.')

    # run process (from command-line args)

    log.info('Running command')
    process = subprocess.Popen(command, cwd=target_directory)
    result = process.wait()
    log.info('Done.')

    # check process status

    # move output files?

    repo = git.Repository(target_directory)
    for fname in repo.status():
        dirpath = os.path.dirname(fname)
        try:
            os.makedirs(dirpath)
        except (OSError, IOError):
            pass
        log.info('Moving output file: {}'.format(fname))
        shutil.move(os.path.join(target_directory, fname), fname)

        attrs = xattr.xattr(fname)
        attrs['created.commit'] = commit

    log.info('Deleting temp directory')
    shutil.rmtree(target_directory)

    # annotate commit?
    



if __name__ == '__main__':
    main()

