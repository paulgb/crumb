
import csv
from orderedset import OrderedSet

class Exporter(object):
    def __init__(self, repo, config):
        self.repo = repo
        self.config = config

    def prepare_annotations(self):
        # compile annotations data
        fields = OrderedSet([
            'start_time',
            'commit_time',
            'commit',
            'commit_message',
            'working_directory',
            'command',
            'elapsed_time'])

        annotations_list = list()
        for annotation in self.repo.get_annotations():
            fields.update(annotation)
            annotations_list.append(annotation)

        annotations_list.sort(key = lambda x: x['start_time'], reverse=True)
        return fields, annotations_list


class CSVExporter(Exporter):
    def export(self, out_file):
        # export to csv file
        fields, annotations = self.prepare_annotations()
        writer = csv.DictWriter(out_file, fields)
        writer.writeheader()
        for annotation in annotations:
            writer.writerow(annotation)

