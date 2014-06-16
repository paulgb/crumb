
import tempfile
from contextlib import contextmanager
import shutil

@contextmanager
def repo_clone(repo, config):
    dirname = tempfile.mkdtemp()
    repo.clone_to(dirname)
    try:
        yield dirname
    finally:
        shutil.rmtree(dirname)

