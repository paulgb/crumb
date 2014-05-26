
import re

'''
Annotation formats:

Output from process:

% key   value

Stored in Git:

1400724950: ./command.sh arguments
    elapsed_time    40
    cv_score        4.2997
    train_score     3.6518

'''

ANNOTATIONS_REGEX = re.compile(r'%\s*(.+?)\s+(.*)')

def parse_output_annotations(text):
    match = ANNOTATIONS_REGEX.match(text)
    if match:
        return match.groups()
    raise ValueError()


