
import tempfile
import subprocess
from sys import argv, exit
import os
from os import path
import shutil
import logging
from time import time
import argparse
from contextlib import contextmanager
import csv

import pygit2 as git
import xattr

ANNOTATIONS_FILE = '.annotate'
ANNOTATIONS_REF = 'refs/notes/commits'
OUTPUT_DESTINATION = 'output'


@contextmanager
def TemporaryDirectory():
    name = tempfile.mkdtemp()
    try:
        yield name
    finally:
        shutil.rmtree(name)

class OrderedSet(set):
    def __init__(self, initial):
        super(OrderedSet, self).__init__(self)
        self.elements = list()
        self.update(initial)

    def update(self, elements):
        for element in elements:
            self.add(element)

    def add(self, element):
        if element in self:
            return
        super(OrderedSet, self).add(element)
        self.elements.append(element)

    def __iter__(self):
        return iter(self.elements)


class NotInRepoError(Exception):
    def __str__(self):
        return 'Not a git repo'


class Qurt(object):
    _repo = None
    _commit = None

    def __init__(self):
        self.log = logging.getLogger(__name__)


    @property
    def repo(self):
        if not self._repo:
            try:
                repo_dir = git.discover_repository('.')
            except KeyError:
                raise NotInRepoError()
            self._repo = git.Repository(repo_dir)
        return self._repo


    @property
    def commit(self):
        if not self._commit:
            self._commit = self.repo.head.target.hex
        return self._commit


    def run(self, command):
        # todo: check if files need to be checked in
        with TemporaryDirectory() as clone_dir:
            self.log.info('Found git repo in {}'.format(self.repo.workdir))
            self.log.info('Last commit: {} ({})'.format(self.commit, self.repo.head.log().next().message))
            # clone repo
            self.log.info('Cloning repository to: {}'.format(clone_dir))
            git.clone_repository(self.repo.workdir, clone_dir)
            self.log.info('Done.')

            # check out project in temp directory
            relpath = path.relpath('.', self.repo.workdir)
            working_directory = path.join(clone_dir, relpath)

            # run process
            start_time = time()
            self.log.info('Running command in {}'.format(working_directory))
            process = subprocess.Popen(command.split(), cwd=working_directory)
            result = process.wait()
            elapsed_time = time() - start_time
            self.log.info('Finished in {} seconds'.format(elapsed_time))

            # check process status
            self.log.info('Process exited with status {}'.format(result))

            self.annotate(command, relpath, elapsed_time, working_directory, self.commit)
            self.move_output_files(clone_dir, start_time, self.commit)


    def annotate(self, command, relpath, elapsed_time, working_directory, commit):
        annotations = 'command\t{}\n'.format(command)
        annotations += 'working_directory\t{}\n'.format(relpath)
        annotations += 'elapsed_time\t{}\n'.format(elapsed_time)

        try:
            fname = path.join(working_directory, ANNOTATIONS_FILE)
            print fname
            with open(fname) as ff:
                annotations += ff.read()
        except IOError:
            self.log.warn('Could not read annotations file (may not exist?)')

        for line in annotations.split('\n'):
            self.log.info(line)

        self.repo.create_note(annotations,
                self.repo.default_signature,
                self.repo.default_signature,
                commit,
                ANNOTATIONS_REF,
                True) # overwrite


    def move_output_files(self, clone_dir, start_time, commit):
        output_repo = git.Repository(clone_dir)
        output_tag = '{:.0f}-{}'.format(start_time, commit)
        for fname in output_repo.status():
            source_path = path.join(clone_dir, fname)
            fpath = path.join(OUTPUT_DESTINATION, output_tag, fname)
            try:
                os.makedirs(path.dirname(fpath))
            except (OSError, IOError):
                pass
            self.log.info('Moving output file: {}'.format(fname))
            shutil.move(source_path, fpath)

            attrs = xattr.xattr(fpath)
            attrs['created.commit'] = commit


    def export(self, out_file):
        # compile annotations data
        fields = OrderedSet(['commit', 'working_directory', 'command', 'elapsed_time'])
        annotations_list = list()
        for note in self.repo.notes():
            annotations = dict(
                commit = note.annotated_id
            )
            for line in note.message.split('\n'):
                try:
                    k, v = line.split('\t', 1)
                except:
                    continue
                annotations[k] = v
            fields.update(annotations)
            annotations_list.append(annotations)

        # export to csv file
        with open(out_file, 'w') as output:
            writer = csv.DictWriter(output, fields)
            writer.writeheader()
            for annotation in annotations_list:
                writer.writerow(annotation)
                

def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('--init', '-i', action='store_true')
    parser.add_argument('--export', '-e')
    parser.add_argument('--run', '-r')
    args = parser.parse_args()

    controller = Qurt()
    
    try:
        if args.init:
            # placeholder; nothing to initialize yet
        elif args.export:
            controller.export(args.export)
        elif args.run:
            controller.run(args.run)
        else:
            parser.print_help()

    except NotInRepoError:
        controller.log.error('Error: must be run inside a git repository')


if __name__ == '__main__':
    main()

