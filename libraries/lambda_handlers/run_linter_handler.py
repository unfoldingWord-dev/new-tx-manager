from __future__ import unicode_literals, print_function
from libraries.lambda_handlers.handler import Handler
from libraries.linters.linter_handler import LinterHandler
from libraries.app.app import App


class RunLinterHandler(Handler):

    def _handle(self, event, context):
        """
        :param dict event:
        :param context:
        :return dict:
        """
        # Get all params, both POST and GET and JSON from the request event
        data = {}
        if 'data' in event and isinstance(event['data'], dict):
            data = event['data']
        if 'body-json' in event and event['body-json'] and isinstance(event['body-json'], dict):
            data.update(event['body-json'])
        # Set required env_vars
        args = {
            'source_zip_url': self.retrieve(data, 'source_url', 'payload'),
            'upload_key': self.retrieve(data, 'upload_key', 'payload'),
            'commit_data': self.retrieve(data, 'commit_data', 'payload', required=False),
            'resource_id': self.retrieve(data, 'resource_id', 'payload', required=False),
            'single_file': self.retrieve(data, 'single_file', 'payload', required=False, default=None),
        }
        linter_class = LinterHandler(**args).get_linter_class()
        return linter_class(**args).run()
