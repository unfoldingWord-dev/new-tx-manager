from __future__ import print_function, unicode_literals

import os

from bs4 import BeautifulSoup

from general_tools.file_utils import load_json_object
from obs_data import obs_data


class OBSStatus(object):
    def __init__(self, content_dir=None):
        """
        Class constructor. Takes a path to a directory
        :param object content_dir: Path to the directory of OBS manifest file
        """
        self.content_dir = content_dir

        self. manifest_file = os.path.join(self.content_dir, 'manifest.json')
        if os.path.isfile(self. manifest_file):
            self.__dict__ = load_json_object(self.manifest_file)
        else:
            raise IOError('The file {0} was not found.'.format(self.manifest_file))

    def __contains__(self, item):
        return item in self.__dict__


class OBSInspection(object):
    def __init__(self, filename, chapter=None):
        """
        Class constructor. Takes a path to an OBS chapter and the chapter of the given file
        :param string filename: Path to the OBS chapter file
        :param string chapter: Chapter being processed
        """
        self.filename = filename
        self.chapter = None # initialize so we don't throw an exception testing for attribute
        if not chapter:
            try:
                self.chapter = int(os.path.splitext(os.path.basename(filename))[0])
            except:
                pass
        else:
            self.chapter = chapter

        self.manifest = {}
        self.warnings = []
        self.errors = []

    def run(self):
        if not self.chapter: # skip over files that are not chapters
            return

        if not os.path.isfile(self.filename):
            self.errors.append('Chapter {0} does not exist!'.format(self.chapter))
            return

        with open(self.filename) as chapter_file:
            chapter_html = chapter_file.read()

        soup = BeautifulSoup(chapter_html, 'html.parser')

        if not soup.find('body'):
            self.warnings.append('Chapter {0} has no body!'.format(self.chapter))
            return

        content = soup.body.find(id='content')

        if not content:
            self.warnings.append('Chapter {0} has no content!'.format(self.chapter))
            return

        if not content.find('h1'):
            self.warnings.append('Chapter {0} does not have a title!'.format(self.chapter))

        frame_count = len(content.find_all('img'))
        expected_frame_count = obs_data['chapters'][str(self.chapter).zfill(2)]['frames']
        if frame_count != expected_frame_count:
            self.warnings.append(
                'Chapter {0} has only {1} frame(s).There should be {2}!'.format(self.chapter, frame_count,
                                                                                expected_frame_count))

        paragraph_count = len(content.find_all('p'))
        expected_paragraph_count = (frame_count * 2 + 1)
        if paragraph_count != expected_paragraph_count:
            self.warnings.append('Bible reference not found at end of chapter {0}!'.format(self.chapter))
