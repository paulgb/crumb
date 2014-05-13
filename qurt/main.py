
import tempfile
import subprocess
from sys import argv, exit
import os
from os import path
import shutil
import logging
from time import time

import pygit2 as git
import xattr

ANNOTATIONS_FILE = '.annotate'
ANNOTATIONS_REF = 'refs/notes/commits'
OUTPUT_DESTINATION = 'output'

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

    # check out project in temp directory

    log.info('Cloning repository to: {}'.format(target_directory))
    git.clone_repository(repo.workdir, target_directory)
    log.info('Done.')

    # run process (from command-line args)

    relpath = path.relpath('.', repo.workdir)
    working_directory = path.join(target_directory, relpath)

    start_time = time()
    log.info('Running command in {}'.format(working_directory))
    process = subprocess.Popen(command, cwd=working_directory)
    result = process.wait()
    elapsed_time = time() - start_time
    log.info('Finished in {} seconds'.format(elapsed_time))

    # check process status

    log.info('Process exited with status {}'.format(result))

    # annotate commit
    
    annotations = 'command\t{}\n'.format(' '.join(command))
    annotations += 'working_directory\t{}\n'.format(relpath)
    annotations += 'elapsed_time\t{}\n'.format(elapsed_time)

    try:
        fname = path.join(working_directory, ANNOTATIONS_FILE)
        print fname
        with open(fname) as ff:
            annotations += ff.read()
    except IOError:
        pass

    repo.create_note(annotations, repo.default_signature, repo.default_signature, repo.head.target.hex, ANNOTATIONS_REF, True)

    # move output files

    output_repo = git.Repository(target_directory)
    output_tag = '{:.0f}-{}'.format(start_time, commit)
    for fname in output_repo.status():
        source_path = path.join(target_directory, fname)
        fpath = path.join(OUTPUT_DESTINATION, output_tag, fname)
        try:
            os.makedirs(path.dirname(fpath))
        except (OSError, IOError):
            pass
        log.info('Moving output file: {} to {}'.format(source_path, fpath))
        shutil.move(source_path, fpath)

        attrs = xattr.xattr(fpath)
        attrs['created.commit'] = commit

    # delete temp directory

    log.info('Deleting temp directory')
    shutil.rmtree(target_directory)


if __name__ == '__main__':
    main()

