from __future__ import absolute_import, unicode_literals, print_function
import mock
from unittest import TestCase
from lambda_handlers.start_job_handler import StartJobHandler


class TestStartJobHandler(TestCase):

    @mock.patch('manager.manager.TxManager.setup_resources')
    @mock.patch('manager.manager.TxManager.start_job')
    def test_handle(self, mock_start_job, mock_setup_resources):
        mock_start_job.return_value = None
        event = {
            'Records': [
                {
                    'eventName': 'INSERT',
                    'eventSourceARN': 'arn:aws:dynamodb:us-west-2:111111111111:table/tx-job/stream/2020-10-10T08:18:22.385',
                    'dynamodb': {
                        'Keys': {'job_id':{'S': '1234'}}
                    }
                }
            ]
        }
        handler = StartJobHandler()
        self.assertIsNone(handler.handle(event, None))
