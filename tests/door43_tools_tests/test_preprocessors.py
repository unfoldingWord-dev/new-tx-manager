import os
import tempfile
import unittest

import shutil

from door43_tools.manifest_handler import MetaData, Manifest
from door43_tools.preprocessors import TsObsMarkdownPreprocessor
from general_tools.file_utils import add_file_to_zip, add_contents_to_zip, unzip


class TestPreprocessor(unittest.TestCase):

    resources_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources')

    def setUp(self):
        """
        Runs before each test
        """
        self.out_dir = ''
        self.temp_dir = ""

    def tearDown(self):
        """
        Runs after each test
        """
        # delete temp files
        if os.path.isdir(self.out_dir):
            shutil.rmtree(self.out_dir, ignore_errors=True)
        if os.path.isdir(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_TsObsMarkdownPreprocessorComplete(self):

        #given
        file_name = 'aab_obs_text_obs.zip'
        repo_name = 'aab_obs_text_obs'
        manifest, repo_dir = self.extractObsFiles(file_name, repo_name)

        # when
        folder = self.runTsObsMarkdownPreprocessor(manifest, repo_dir)

        #then
        self.verifyTransform(folder)

    def test_TsObsMarkdownPreprocessorMissingChapter(self):

        #given
        file_name = 'aab_obs_text_obs-missing_chapter_01.zip'
        repo_name = 'aab_obs_text_obs'
        missing_chapters = [1]
        manifest, repo_dir = self.extractObsFiles(file_name, repo_name)

        # when
        folder = self.runTsObsMarkdownPreprocessor(manifest, repo_dir)

        #then
        self.verifyTransform(folder, missing_chapters)

    def runTsObsMarkdownPreprocessor(self, manifest, repo_dir):
        self.out_dir = tempfile.mkdtemp(prefix='output_')
        compiler = TsObsMarkdownPreprocessor(manifest, repo_dir, self.out_dir)
        compiler.run()
        return self.out_dir

    def extractObsFiles(self, file_name, repo_name):
        file_path = os.path.join(self.resources_dir, file_name)

        # 1) unzip the repo files
        self.temp_dir = tempfile.mkdtemp(prefix='repo_')
        unzip(file_path, self.temp_dir)
        repo_dir = os.path.join(self.temp_dir, repo_name)
        if not os.path.isdir(repo_dir):
            repo_dir = file_path

        # 2) Get the manifest file or make one if it doesn't exist based on meta.json, repo_name and file extensions
        manifest_path = os.path.join(repo_dir, 'manifest.json')
        if not os.path.isfile(manifest_path):
            manifest_path = os.path.join(repo_dir, 'project.json')
            if not os.path.isfile(manifest_path):
                manifest_path = None
        meta_path = os.path.join(repo_dir, 'meta.json')
        meta = None
        if os.path.isfile(meta_path):
            meta = MetaData(meta_path)
        manifest = Manifest(file_name=manifest_path, repo_name=repo_name, files_path=repo_dir, meta=meta)
        return manifest, repo_dir

    def verifyTransform(self, folder, missing_chapters = []):
        files_to_verify = []
        files_missing = []
        for i in range(1, 51):
            file_name = str(i).zfill(2) + '.md'
            if not i in missing_chapters:
                files_to_verify.append(file_name)
            else:
                files_missing.append(file_name)
        files_to_verify.append('front.md')

        for file_to_verify in files_to_verify:
            file_name = os.path.join(folder, file_to_verify)
            self.assertTrue(os.path.isfile(file_name), 'OBS md file not found: {0}'.format(file_to_verify))

        for file_to_verify in files_missing:
            file_name = os.path.join(folder, file_to_verify)
            self.assertFalse(os.path.isfile(file_name), 'OBS md file present, but should not be: {0}'.format(file_to_verify))




