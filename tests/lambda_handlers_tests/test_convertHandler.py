from __future__ import absolute_import, unicode_literals, print_function
import mock
from unittest import TestCase
from lambda_handlers.convert_handler import ConvertHandler
from converters.md2html_converter import Md2HtmlConverter
from converters.usfm2html_converter import Usfm2HtmlConverter


class TestConvertHandler(TestCase):
    @mock.patch('converters.converter.Converter.run')
    def test_handle_for_obs(self, mock_convert_run):
        mock_convert_run.return_value = None
        event = {
            'data': {
                'job': {
                    'input_format': 'md',
                    'convert_module': 'md2html',
                    'message': 'Conversion started...',
                    'started_at': '2017-03-08T18:57:53Z',
                    'errors': [],
                    'job_id': '1234587890',
                    'method': 'GET',
                    'source': 'https://cdn.example.com/preconvert/705948ab00.zip',
                    'status': 'started',
                    'warnings': [],
                    'output_format': 'html',
                    'expires_at': '2017-03-09T18:57:51Z',
                    'user': 'exampleuser',
                    'cdn_file': 'tx/job/1234567890.zip',
                    'cdn_bucket': 'test_cdn_bucket',
                    'ended_at': None,
                    'success': None,
                    'created_at': '2017-03-08T18:57:51Z',
                    'callback': 'https://api.example.com/client/callback',
                    'eta': '2017-03-08T18:58:11Z',
                    'output': 'https://cdn.example.com/tx/job/a07116859e82e4596798cf81349a445e3dcecef463913f762cc5210aebe93db0.zip',
                    'identifier': 'richmahn/en-obs/705948ab00',
                    'resource_type': 'obs'
                }
            },
            'vars': {
                'cdn_url': 'https://cdn.exmaple.com',
                'api_url': 'https://api.example.com',
                'gogs_url': 'http://git.example.com',
                'cdn_bucket': 'cdn_test_bucket'
            }
        }
        self.assertIsNone(ConvertHandler(Md2HtmlConverter).handle(event, None))

    @mock.patch('converters.converter.Converter.run')
    def test_handle_for_usfm(self, mock_convert_run):
        mock_convert_run.return_value = None
        event = {
            'data': {
                'job': {
                    "input_format": "usfm",
                    "convert_module": "usfm2html",
                    'message': 'Conversion started...',
                    'started_at': '2017-03-08T18:57:53Z',
                    'errors': [],
                    'job_id': '1234587890',
                    'method': 'GET',
                    'source': 'https://cdn.example.com/preconvert/705948ab00.zip',
                    'status': 'started',
                    'warnings': [],
                    'output_format': 'html',
                    'expires_at': '2017-03-09T18:57:51Z',
                    'user': 'exampleuser',
                    'cdn_file': 'tx/job/1234567890.zip',
                    'cdn_bucket': 'test_cdn_bucket',
                    "log": ["Started job b07f65d8be71fef116841e5161f3d7f9b69b83673bf72527f1d93186d8869310 at 2017-03-15T17:50:14Z",
                            "Telling module usfm2html to convert https://s3-us-west-2.amazonaws.com/test-tx-webhook/preconvert/acf4d7eaf4.zip and put at https://test-cdn.door43.org/tx/job/b07f65d8be71fef116841e5161f3d7f9b69b83673bf72527f1d93186d8869310.zip"],
                    'ended_at': None,
                    'success': None,
                    'created_at': '2017-03-08T18:57:51Z',
                    'callback': 'https://api.example.com/client/callback',
                    'eta': '2017-03-08T18:58:11Z',
                    'output': 'https://cdn.example.com/tx/job/a07116859e82e4596798cf81349a445e3dcecef463913f762cc5210aebe93db0.zip',
                    'identifier': 'richmahn/en-obs/705948ab00',
                    'resource_type': 'obs'
                }
            },
            'vars': {
                'cdn_url': 'https://cdn.exmaple.com',
                'api_url': 'https://api.example.com',
                'gogs_url': 'http://git.example.com',
                'cdn_bucket': 'cdn_test_bucket'
            }
        }
        self.assertIsNone(ConvertHandler(Usfm2HtmlConverter).handle(event, None))
