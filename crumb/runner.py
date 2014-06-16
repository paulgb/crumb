
import subprocess
import shlex
from time import time
from datetime import datetime
import os.path as path

from annotations import parse_output_annotations

class Runner(object):
    def __init__(self, config):
        self.config = config
    
    def run(self, clone_dir, relpath, command):
        # annotations
        annotations = dict()

        working_dir = path.join(clone_dir, relpath)

        # run process
        start_time = time()
        start_dt = datetime.now()
        process = subprocess.Popen(shlex.split(command),
                cwd=working_dir,
                stdout=subprocess.PIPE)

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
        annotations['start_time'] = start_dt
        annotations['elapsed_time'] = elapsed_time
        annotations['exit_status'] = result

        return annotations

