from __future__ import unicode_literals, print_function
from manager.manager import TxManager
from lambda_handlers.handler import Handler


class DashboardHandler(Handler):

    def _handle(self, event, context):
        """
        :param dict event:
        :param context:
        :return dict:
        """
        data = {}
        if 'data' in event and isinstance(event['data'], dict):
            data = event['data']
        if 'body-json' in event and isinstance(event['body-json'], dict):
            data.update(event['body-json'])
        # Set required env_vars
        env_vars = {
            'api_url': self.retrieve(event['vars'], 'api_url', 'Environment Vars')
        }
        return TxManager(**env_vars).generate_dashboard()
