from __future__ import absolute_import, unicode_literals, print_function
import os
import tempfile
import unittest
import mock
from resource_container.ResourceContainer import RC, manifest_from_repo_name
from general_tools.file_utils import remove_tree, unzip, load_yaml_object, load_json_object
from datetime import datetime


class TestResourceContainer(unittest.TestCase):

    resources_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources')

    def setUp(self):
        """Runs before each test."""
        self.out_dir = ''

    def tearDown(self):
        """Runs after each test."""
        # delete temp files
        remove_tree(self.out_dir)

    @classmethod
    def setUpClass(cls):
        """Called before tests in this class are run."""
        pass

    @classmethod
    def tearDownClass(cls):
        """Called after tests in this class are run."""
        pass

    def test_close(self):
        """This tests that the temp directories are deleted when the class is closed."""
        pass

    def test_en_obs_manifest_yaml(self):
        """ Populates the ResourceContainer object and verifies the output."""
        # test with the English OBS
        zip_file = os.path.join(self.resources_dir, 'en-obs-manifest-yaml.zip')
        self.out_dir = tempfile.mkdtemp(prefix='repo_')
        unzip(zip_file, self.out_dir)
        repo_dir = os.path.join(self.out_dir, 'en_obs')
        rc = RC(repo_dir, 'en_obs')
        rc_dic = rc.as_dict()
        yaml = load_yaml_object(os.path.join(repo_dir, 'manifest.yaml'))
        self.assertDictEqual(yaml, rc_dic)
        chapters = rc.chapters()
        self.assertEqual(len(chapters), 2)
        chunks = rc.chunks(rc.project().identifier, 'front')
        self.assertEqual(chunks, ['intro.md', 'title.md'])

    def test_en_obs_package_json(self):
        """ Populates the ResourceContainer object and verifies the output."""
        # test with the English OBS
        zip_file = os.path.join(self.resources_dir, 'en-obs-package-json.zip')
        self.out_dir = tempfile.mkdtemp(prefix='repo_')
        unzip(zip_file, self.out_dir)
        repo_dir = os.path.join(self.out_dir, 'en-obs')
        rc = RC(repo_dir)
        rc.as_dict()
        json = load_json_object(os.path.join(repo_dir, 'package.json'))
        self.assertEqual(rc.resource.identifier, json['resource']['slug'])
        self.assertEqual(rc.resource.type, 'book')
        self.assertEqual(rc.resource.format, json['content_mime_type'])
        self.assertEqual(rc.resource.file_ext, 'md')
        self.assertEqual(rc.resource.conformsto, 'pre-rc')
        self.assertEqual(rc.resource.issued, json['resource']['status']['pub_date'])
        chapters = rc.chapters()
        self.assertEqual(len(chapters), 2)
        chunks = rc.chunks(rc.project().identifier, '_back')
        self.assertEqual(chunks, ['back-matter.md'])

    def test_bible_no_manifest(self):
        """ Populates the ResourceContainer object and verifies the output."""
        # test with the English OBS
        zip_file = os.path.join(self.resources_dir, 'bible-no-manifest.zip')
        self.out_dir = tempfile.mkdtemp(prefix='repo_')
        unzip(zip_file, self.out_dir)
        repo_dir = os.path.join(self.out_dir, 'en_ulb')
        rc = RC(repo_dir)
        rc.as_dict()
        self.assertEqual(rc.resource.identifier, 'ulb')
        self.assertEqual(rc.resource.type, 'bundle')
        self.assertEqual(rc.resource.format, 'text/usfm')
        self.assertEqual(rc.resource.file_ext, 'usfm')
        self.assertEqual(rc.resource.conformsto, 'pre-rc')
        self.assertEqual(rc.resource.modified, datetime.utcnow().strftime("%Y-%m-%d"))
        chapters = rc.chapters()
        self.assertEqual(len(chapters), 0)

    def test_bible_no_manifest(self):
        """ Populates the ResourceContainer object and verifies the output."""
        # test with the English OBS
        zip_file = os.path.join(self.resources_dir, 'bible-no-manifest.zip')
        self.out_dir = tempfile.mkdtemp(prefix='repo_')
        unzip(zip_file, self.out_dir)
        repo_dir = os.path.join(self.out_dir, 'en_ulb')
        rc = RC(repo_dir)
        rc.as_dict()
        self.assertEqual(rc.resource.identifier, 'ulb')
        self.assertEqual(rc.resource.type, 'bundle')
        self.assertEqual(rc.resource.format, 'text/usfm')
        self.assertEqual(rc.resource.file_ext, 'usfm')
        self.assertEqual(rc.resource.conformsto, 'pre-rc')
        self.assertEqual(rc.resource.modified, datetime.utcnow().strftime("%Y-%m-%d"))
        chapters = rc.chapters()
        self.assertEqual(len(chapters), 0)
        self.assertIsNone(rc.config())
        self.assertIsNone(rc.toc())

    def test_multiple_projects(self):
        """ Populates the ResourceContainer object and verifies the output."""
        # test with the English OBS
        zip_file = os.path.join(self.resources_dir, 'en-ta-multiple-projects.zip')
        self.out_dir = tempfile.mkdtemp(prefix='repo_')
        unzip(zip_file, self.out_dir)
        repo_dir = os.path.join(self.out_dir, 'en_ta')
        rc = RC(repo_dir)
        rc.as_dict()
        yaml = load_yaml_object(os.path.join(repo_dir, 'manifest.yaml'))
        self.assertEqual(rc.resource.identifier, yaml['dublin_core']['identifier'])
        self.assertEqual(rc.resource.type, yaml['dublin_core']['type'])
        self.assertEqual(rc.resource.format, yaml['dublin_core']['format'])
        self.assertEqual(rc.resource.file_ext, 'md')
        self.assertEqual(rc.resource.conformsto, yaml['dublin_core']['conformsto'])
        self.assertEqual(rc.resource.modified, yaml['dublin_core']['modified'])
        self.assertEqual(len(rc.project_ids), 4)
        self.assertEqual(rc.project_count, 4)
        chapters = rc.chapters('checking')
        self.assertEqual(len(chapters), 44)
        chunks = rc.chunks('checking', 'level1')
        self.assertEqual(chunks, ['01.md', 'sub-title.md', 'title.md'])
        self.assertTrue('acceptable' in rc.config('checking'))
        self.assertTrue('title' in rc.toc('checking'))
        self.assertTrue(rc.toc('checking')['title'], 'Table of Contents')

    def test_bible_from_tx_pre_rc(self):
        """ Populates the ResourceContainer object and verifies the output."""
        # test with the English OBS
        zip_file = os.path.join(self.resources_dir, 'id_mat_text_ulb-ts.zip')
        self.out_dir = tempfile.mkdtemp(prefix='repo_')
        unzip(zip_file, self.out_dir)
        repo_dir = os.path.join(self.out_dir, 'id_mat_text_ulb-ts')
        rc = RC(repo_dir)
        rc.as_dict()
        json = load_json_object(os.path.join(repo_dir, 'manifest.json'))
        self.assertEqual(rc.resource.identifier, json['resource']['id'])
        self.assertEqual(rc.resource.type, 'book')
        self.assertEqual(rc.resource.format, 'text/{0}'.format(json['format']))
        self.assertEqual(rc.resource.file_ext, json['format'])
        self.assertEqual(rc.resource.conformsto, 'pre-rc')
        self.assertEqual(rc.resource.modified, datetime.utcnow().strftime("%Y-%m-%d"))
        chapters = rc.chapters()
        self.assertEqual(len(chapters), 29)
        chunks = rc.chunks('01')
        self.assertEqual(len(chunks), 11)

    @mock.patch('general_tools.url_utils.get_url')
    def test_random_tests(self, mock_get_url):
        mock_get_url.return_value = '[{"ld": "ltr", "gw": false, "lc": "aa", "ln": "Afaraf", "cc": ["DJ", "ER", "ET", "US", "CA"], "pk": 6, "alt": ["Afaraf", "Danakil", "Denkel", "Adal", "Afar Af", "Qafar", "Baadu (Ba\'adu)"], "lr": "Africa", "ang": "Afar"}, {"ld": "ltr", "gw": false, "lc": "aaa", "ln": "Ghotuo", "cc": ["NG"], "pk": 7, "alt": [], "lr": "Africa", "ang": "Ghotuo"}]'
        # Test getting language from tD
        manifest = manifest_from_repo_name('aa_mat-ts')
        self.assertEqual(manifest['dublin_core']['language']['identifier'], 'aa')
        self.assertEqual(manifest['dublin_core']['language']['title'], 'Afaraf')
        self.assertEqual(manifest['dublin_core']['identifier'], 'bible')
        self.assertEqual(manifest['projects'][0]['identifier'], 'mat')
        self.assertRaises(Exception, RC, {})
        self.assertRaises(Exception, RC, '/tmp/dummy_dir')

if __name__ == '__main__':
    unittest.main()
