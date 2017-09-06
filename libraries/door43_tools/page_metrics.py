from __future__ import print_function, unicode_literals
import logging
import re
import urlparse
from decimal import Decimal
from datetime import datetime
from operator import itemgetter
from libraries.aws_tools.dynamodb_handler import DynamoDBHandler
from libraries.models.language_stats import LanguageStats
from libraries.models.manifest import TxManifest
from libraries.app.app import App


class PageMetrics(object):
    LANGUAGE_STATS_TABLE_NAME = 'language-stats'
    INVALID_URL_ERROR = 'repo not found for: '
    INVALID_LANG_URL_ERROR = 'language not found for: '
    DB_ACCESS_ERROR = 'could not access view counts for: '

    def __init__(self, language_stats_table_name=None):
        """
        :param string language_stats_table_name:
        """
        self.language_stats_table_name = language_stats_table_name
        self.language_stats_db_handler = None
        self.logger = logging.getLogger()
        self.languages = None

    def get_view_count(self, path, increment=0):
        """
        get normal user page view count with optional increment
        :param path:
        :param increment:
        :return:
        """
        self.logger.debug("Start: get_view_count")

        response = {  # default to error
            'ErrorMessage': PageMetrics.INVALID_URL_ERROR + path
        }

        parsed = urlparse.urlparse(path)
        try:
            empty, u, repo_owner, repo_name = parsed.path.split('/')[0:4]
        except:
            self.logger.warning("Invalid repo url: " + path)
            return response

        if (empty != '') or (u != 'u'):
            self.logger.warning("Invalid repo url: " + path)
            return response

        del response['ErrorMessage']

        self.logger.debug("Valid repo url: " + path)
        # First see record already exists in DB
        tx_manifest = App.db.query(TxManifest).filter_by(repo_name=repo_name, user_name=repo_owner).first()
        if tx_manifest:
            if increment:
                tx_manifest.views += 1
                self.logger.debug('Incrementing view count to {0}'.format(tx_manifest.views))
                App.db.commit()
            else:
                self.logger.debug('Returning stored view count of {0}'.format(tx_manifest.views))
            view_count = tx_manifest.views
        else:  # record is not present
            self.logger.debug('No entries for page in manifest table')
            view_count = 0

        response['view_count'] = view_count

        return response

    def get_language_view_count(self, path, increment=0):
        """
        get language page view count with optional increment
        :param path:
        :param increment:
        :return:
        """
        self.logger.debug("Start: get_language_count")

        response = {  # default to error
            'ErrorMessage': PageMetrics.INVALID_LANG_URL_ERROR + path
        }

        parsed = urlparse.urlparse(path)
        try:
            parts = parsed.path.split('/')
            if len(parts) == 2:
                empty, language_code = parts
            else:
                empty, language_code, page = parts
        except:
            self.logger.warning("Invalid language page url: " + path)
            return response

        language_code = self.validate_language_code(language_code)
        if not language_code:
            self.logger.warning("Invalid language page url: " + path)
            return response

        del response['ErrorMessage']
        language_code = language_code.lower()
        if not self.language_stats_db_handler:
            self.init_language_stats_table(parsed)

        self.logger.debug("Valid '" + language_code + "' url: " + path)
        try:
            # First see record already exists in DB
            lang_stats = LanguageStats({'lang_code': language_code},
                                       db_handler=self.language_stats_db_handler)
            if lang_stats.lang_code:  # see if data in table
                if increment:
                    lang_stats.views += 1
                    self.logger.debug('Incrementing view count to {0}'.format(lang_stats.views))
                    self.updateLangStats(lang_stats)
                else:
                    self.logger.debug('Returning stored view count of {0}'.format(lang_stats.views))

            else:  # record is not present
                lang_stats.views = 0
                if increment:
                    lang_stats.lang_code = language_code
                    lang_stats.views += 1
                    self.logger.debug('No entries for {0} in {1} table, creating'.format(language_code,
                                                                                    self.language_stats_table_name))
                    self.updateLangStats(lang_stats)
                else:
                    self.logger.debug('No entries for {0} in {1} table'.format(language_code,
                                                                                     self.language_stats_table_name))

            view_count = lang_stats.views
            if type(view_count) is Decimal:
                view_count = int(view_count.to_integral_value())
            response['view_count'] = view_count

        except Exception as e:
            self.logger.exception('Error accessing {0} table'.format(self.language_stats_table_name), exc_info=e)
            response['ErrorMessage'] = PageMetrics.DB_ACCESS_ERROR + path
            return response

        return response

    def validate_language_code(self, language_code):
        """
        verifies that language_code is valid format and returns the language code if it's valid, else returns None
        :param language_code:
        :return:
        """
        language_code = language_code.lower()
        lang_code_pattern = re.compile("^[a-z]{2,3}(-[a-z0-9]{2,4})?$")  # e.g. ab, abc, pt-br, es-419, sr-latn
        valid_lang_code = lang_code_pattern.match(language_code)
        if not valid_lang_code:
            extended_lang_code_pattern = re.compile("^[a-z]{2,3}(-x-[\w\d]+)?$", re.UNICODE)  # e.g. abc-x-abcdefg
            valid_lang_code = extended_lang_code_pattern.match(language_code)
            if not valid_lang_code:
                extended_lang_code_pattern2 = re.compile("^(-x-[\w\d]+){1}$", re.UNICODE)  # e.g. -x-abcdefg
                valid_lang_code = extended_lang_code_pattern2.match(language_code)
                if not valid_lang_code:
                    language_code = None
        return language_code

    def updateLangStats(self, lang_stats):
        """
        update the entry in the database
        :param lang_stats:
        :return:
        """
        utcnow = datetime.utcnow()
        lang_stats.last_updated = utcnow.strftime("%Y-%m-%dT%H:%M:%SZ")
        lang_stats.update()

    def init_language_stats_table(self, parsed):
        if not self.language_stats_table_name:
            site = ''
            netloc_parts = parsed.netloc.split('-')
            if len(netloc_parts) > 1:
                site = netloc_parts[0]
            self.language_stats_table_name = site + '-' + PageMetrics.LANGUAGE_STATS_TABLE_NAME
        self.language_stats_db_handler = DynamoDBHandler(self.language_stats_table_name)

    def list_language_views(self):
        """
        get list of all the language view records
        :return:
        """
        if not self.language_stats_db_handler:
            return None

        # First see record already exists in DB
        language_items = LanguageStats(db_handler=self.language_stats_db_handler).query({"monitor":
                                                                                   {"condition": "eq", "value": True}})
        self.languages = []
        if language_items and len(language_items):
            for language in language_items:
                self.languages.append(language.get_db_data())
        return self.languages

    def get_language_views_sorted_by_count(self, reverse_sort=True):
        """
        Get list of language views records sorted by views.
        :param reverse_sort:
        :return:
        """
        newlist = None
        if self.languages is None:
            try:
                self.list_language_views()
            except:
                pass

        if self.languages is not None:
            newlist = sorted(self.languages, key=itemgetter('views'), reverse=reverse_sort)

        return newlist

    def get_language_views_sorted_by_date(self, reverse_sort=True):
        """
        Get list of language views records sorted by time last viewed.
        :param reverse_sort:
        :return:
        """
        newlist = None
        if self.languages is None:
            try:
                self.list_language_views()
            except:
                pass

        if self.languages is not None:
            newlist = sorted(self.languages, key=itemgetter('last_updated'), reverse=reverse_sort)

        return newlist
