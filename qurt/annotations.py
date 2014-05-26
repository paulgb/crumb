
import re
from StringIO import StringIO

'''
Annotation formats:

Output from process:

% key   value

Stored in Git:

1400724950: [wd] ./command.sh arguments
    elapsed_time    40
    cv_score        4.2997
    train_score     3.6518

'''

ANNOTATIONS_REGEX = re.compile(r'%\s*(.+?)\s+(.*)')
DATE_FORMAT = '%Y%m%d.%H%M'

def parse_output_annotations(text):
    match = ANNOTATIONS_REGEX.match(text)
    if match:
        return match.groups()
    raise ValueError()

def annotations_to_string(annotations, dt, command, relpath):
    result_buffer = StringIO()
    dd = dt.strftime(DATE_FORMAT)
    if relpath:
        result_buffer.write('{}: [{}] {}\n'.format(dd, relpath, command))
    else:
        result_buffer.write('{}: {}\n'.format(dd, command))

    for key, value in annotations.items():
        result_buffer.write('\t{}\t{}\n'.format(key, value))
    return result_buffer.getvalue()

