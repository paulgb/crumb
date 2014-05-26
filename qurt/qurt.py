
import logging
import subprocess
from sys import argv, exit
import os, os.path as path
from time import time
import csv
from datetime import datetime

import pygit2 as git
import xattr

from tempdir import TemporaryDirectory
from orderedset import OrderedSet
from annotations import parse_output_annotations

ANNOTATIONS_REF = 'refs/notes/commits'
OUTPUT_DESTINATION = 'output'

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
        # todo: warn if files need to be checked in
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

            # annotations
            annotations = dict()

            # run process
            start_time = time()
            self.log.info('Running command in {}'.format(working_directory))
            process = subprocess.Popen(command.split(), cwd=working_directory, stdout=subprocess.PIPE)

            for line in process.stdout:
                print line.rstrip()
                try:
                    key, value = parse_output_annotations(line)
                    annotations[key] = value
                except ValueError:
                    pass

            result = process.wait()
            elapsed_time = time() - start_time

            annotations['command'] = command
            annotations['working_directory'] = relpath
            annotations['elapsed_time'] = elapsed_time

            self.log.info('Finished in {} seconds'.format(elapsed_time))
            print annotations

            # check process status
            self.log.info('Process exited with status {}'.format(result))

            self.repo.create_note(annotations,
                    self.repo.default_signature,
                    self.repo.default_signature,
                    self.commit,
                    ANNOTATIONS_REF,
                    True) # overwrite

            #self.move_output_files(clone_dir, start_time, self.commit)


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
        fields = OrderedSet(['commit_time', 'commit', 'commit_message', 'working_directory', 'command', 'elapsed_time'])
        annotations_list = list()
        for note in self.repo.notes():
            commit = self.repo.revparse_single(note.annotated_id)
            commit_time = datetime.fromtimestamp(commit.commit_time)
            annotations = dict(
                commit = note.annotated_id,
                commit_time = str(commit_time),
                commit_message = commit.message.strip()
            )
            for line in note.message.split('\n'):
                try:
                    k, v = line.split('\t', 1)
                except:
                    continue
                annotations[k] = v
            fields.update(annotations)
            annotations_list.append(annotations)
        annotations_list.sort(key = lambda x: x['commit_time'], reverse=True)

        # export to csv file
        with open(out_file, 'w') as output:
            writer = csv.DictWriter(output, fields)
            writer.writeheader()
            for annotation in annotations_list:
                writer.writerow(annotation)

