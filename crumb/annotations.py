
import re
from StringIO import StringIO
from datetime import datetime

'''
Annotation formats:

Output from process:

% key   value

Stored in Git:

20140525.2215: [working/directory] ./command.sh arguments
    elapsed_time    40
    cv_score        4.2997
    train_score     3.6518

'''

ANNOTATIONS_REGEX = re.compile(r'%\s*(.+?)\s+(.*)')
DATE_FORMAT = '%Y%m%d.%H%M'
ANNOTATIONS_HEADER = re.compile(r'(\d+\.\d+):(?: \[([^\]]+)\])? (.+)')
ANNOTATIONS_KV = re.compile('\t(.+)\t(.+)')


def parse_output_annotations(text):
    match = ANNOTATIONS_REGEX.match(text)
    if match:
        return match.groups()
    raise ValueError()


def annotations_to_string(annotations):
    result_buffer = StringIO()
    annotations = dict(annotations)
    relpath = annotations.pop('working_directory')
    dt = annotations.pop('start_time')
    command = annotations.pop('command')

    dd = dt.strftime(DATE_FORMAT)
    if relpath:
        result_buffer.write('{}: [{}] {}\n'.format(dd, relpath, command))
    else:
        result_buffer.write('{}: {}\n'.format(dd, command))

    for key, value in annotations.items():
        result_buffer.write('\t{}\t{}\n'.format(key, value))
    return result_buffer.getvalue()


def string_to_annotations(string_annotations):
    annotations = None

    for line in string_annotations.split('\n'):
        match = ANNOTATIONS_HEADER.match(line)
        if match is not None:
            if annotations is not None:
                yield annotations
            annotations = dict()

            timestamp, wd, command = match.groups()
            if wd is None:
                wd = ''
            timestamp = datetime.strptime(timestamp, DATE_FORMAT)
            annotations['start_time'] = timestamp
            annotations['working_directory'] = wd
            annotations['command'] = command
            continue

        match = ANNOTATIONS_KV.match(line)
        if match is not None:
            if annotations is None:
                continue
            k, v = match.groups()
            annotations[k] = v

    if annotations:
        yield annotations

