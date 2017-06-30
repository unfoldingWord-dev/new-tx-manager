from __future__ import absolute_import, unicode_literals, print_function
import unittest
import os
import tempfile
from moto import mock_s3
from bs4 import BeautifulSoup
from libraries.door43_tools.project_printer import ProjectPrinter
from libraries.general_tools.file_utils import unzip
from shutil import rmtree


@mock_s3
class ProjectPrinterTests(unittest.TestCase):
    MOCK_CDN_BUCKET = "test_cdn"

    resources_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources')

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_project_printer")
        self.printer = ProjectPrinter(self.MOCK_CDN_BUCKET)
        self.printer.cdn_handler.create_bucket()
        self.mock_s3_obs_project()

    def tearDown(self):
        rmtree(self.temp_dir, ignore_errors=True)

    def test_print_obs(self):
        self.printer.print_project(self.project_key)
        self.assertTrue(self.printer.cdn_handler.key_exists('u/{0}/print_all.html'.format(self.project_key)))
        html = self.printer.cdn_handler.get_file_contents('u/{0}/print_all.html'.format(self.project_key))
        soup = BeautifulSoup(html, 'html.parser')
        self.assertEqual(len(soup.div), 69)
        self.assertEqual(soup.html['lang'], 'en')
        self.assertEqual(soup.html['dir'], 'ltr')
        # Run again, shouldn't have to generate
        self.printer.print_project(self.project_key)
        self.assertTrue(self.printer.cdn_handler.key_exists('u/{0}/print_all.html'.format(self.project_key)))

    def test_random_tests(self):
        self.assertRaises(Exception, self.printer.print_project, 'bad_key')
        self.assertRaises(Exception, self.printer.print_project, 'bad_owner/bad_repo/bad_commit')

    def mock_s3_obs_project(self):
        zip_file = os.path.join(self.resources_dir, 'converted_projects', 'en-obs-complete.zip')
        out_dir = os.path.join(self.temp_dir, 'en-obs-complete')
        unzip(zip_file, out_dir)
        project_dir = os.path.join(out_dir, 'door43', 'en-obs', '12345678')
        self.project_files = [f for f in os.listdir(project_dir) if os.path.isfile(os.path.join(project_dir, f))]
        self.project_key = 'door43/en-obs/12345678'
        for filename in self.project_files:
            self.printer.cdn_handler.upload_file(os.path.join(project_dir, filename), 'u/{0}/{1}'.format(self.project_key, filename))
        self.printer.cdn_handler.upload_file(os.path.join(out_dir, 'door43', 'en-obs', 'project.json'), 'u/door43/en-obs/project.json')
