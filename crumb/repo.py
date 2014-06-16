
import pygit2 as git
from annotations import annotations_to_string, string_to_annotations
from datetime import datetime

ANNOTATIONS_REF = 'refs/notes/commits'

class NotInRepoError(Exception):
    def __str__(self):
        return 'Not a git repo'


class GitRepo(object):
    def __init__(self):
        try:
            self.repo_dir = git.discover_repository('.')
        except KeyError:
            raise NotInRepoError()

        self.repo = git.Repository(self.repo_dir)
        self.commit = self.repo.head.target.hex
        self.basedir = self.repo.workdir

    def clone_to(self, dirname):
        git.clone_repository(self.repo_dir, dirname)

    def annotate(self, annotations):
        annotations_txt = annotations_to_string(annotations)

        try:
            previous_value = self.repo.lookup_note(self.commit).message
            annotations_txt = '\n'.join((previous_value, annotations_txt))
        except KeyError:
            pass

        self.repo.create_note(annotations_txt,
                self.repo.default_signature,
                self.repo.default_signature,
                self.commit,
                ANNOTATIONS_REF,
                True) # overwrite

    def get_annotations(self):
        for note in self.repo.notes():
            commit = self.repo.revparse_single(note.annotated_id)
            commit_time = datetime.fromtimestamp(commit.commit_time)

            for annotation in string_to_annotations(note.message):
                annotation['commit'] = note.annotated_id
                annotation['commit_time'] = str(commit_time)
                annotation['commit_message'] = commit.message.strip()

                yield annotation

