from __future__ import print_function, unicode_literals
import json
from libraries.door43_tools.messaging_service import MessagingService


class LinterMessaging(MessagingService):
    def __init__(self, queue_name="linter_complete", region="us-west-2"):
        super(LinterMessaging, self).__init__(queue_name, region)
        self.last_wait_list = None

    def clear_lint_jobs(self, source_urls, timeout=2):
        """
        for safety's sake make sure there aren't leftover messages from a previous conversion
        :param source_urls: list of lint jobs referenced by the source
        :param timeout: maximum seconds to wait
        """
        self.wait_for_lint_jobs(source_urls, timeout)

    def wait_for_lint_jobs(self, source_urls, timeout=120, visibility_timeout=5):
        """
        waits for up to timeout seconds for all lint jobs to complete.  When finished call get_finished_jobs() to get
            the received messages in dict
        :param source_urls: list of lint jobs referenced by the source
        :param timeout: maximum seconds to wait
        :return: success if all messages found
        """
        self.last_wait_list = source_urls
        return self.wait_for_messages(source_urls, timeout=timeout, visibility_timeout=visibility_timeout)

    def get_job_data(self, key):
        if self.recvd_payloads:
            lint_data = self.recvd_payloads[key]
            return lint_data
        return None

    def notify_lint_job_complete(self, source_url, success, payload=None):
        return self.send_message(source_url, success, payload)

    def get_finished_jobs(self):
        return self.recvd_payloads

    def get_unfinished_jobs(self):
        if self.last_wait_list and self.recvd_payloads:
            unfinished = list(self.last_wait_list)
            for key in self.recvd_payloads:
                unfinished.remove(key)
            return unfinished
        return None
