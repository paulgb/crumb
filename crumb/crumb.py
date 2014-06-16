
#import logging
#from sys import argv, exit
#import os, os.path as path
#from time import time
import os.path as path

#import xattr

from cloner import repo_clone
from annotations import parse_output_annotations, annotations_to_string, string_to_annotations
from repo import GitRepo, NotInRepoError
from config import Configuration
from runner import Runner
from export import CSVExporter


class Crumb(object):
    def __init__(self):
        #self.log = logging.getLogger(__name__)

        self.repo = GitRepo()
        self.config = Configuration(self.repo)


    def run(self, command):
        runner = Runner(self.config)

        relpath = path.relpath('.', self.repo.basedir)

        with repo_clone(self.repo, self.config) as clone_dir:
            annotations = runner.run(clone_dir, relpath, command)
            self.repo.annotate(annotations)


    def export(self, out_file):
        exporter = CSVExporter(self.repo, self.config)
        exporter.export(out_file)

