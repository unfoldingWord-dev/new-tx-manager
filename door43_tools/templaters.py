from __future__ import unicode_literals, print_function
import os
import json
import codecs
from glob import glob
from bs4 import BeautifulSoup
from general_tools.file_utils import write_file
from door43_tools.manifest_handler import Manifest


class Templater(object):
    def __init__(self, source_dir, output_dir, template_file, quiet=False):
        self.source_dir = source_dir  # Local directory
        self.output_dir = output_dir  # Local directory
        self.template_file = template_file  # Local file of template
        self.quiet = quiet

        self.files = sorted(glob(os.path.join(self.source_dir, '*.html')))
        self.manifest = None
        self.build_log = {}
        self.template_html = ''

    def run(self):
        repo_name = ""

        print(glob(os.path.join(self.source_dir, '*')))

        # get build_log
        build_log_filename = os.path.join(self.source_dir, 'build_log.json')
        if os.path.isfile(build_log_filename):
            with open(build_log_filename) as build_log_file:
                self.build_log = json.load(build_log_file)
                repo_name = self.build_log['repo_name']

        # get manifest
        manifest_filename = os.path.join(self.source_dir, 'manifest.json')
        self.manifest = Manifest(file_name=manifest_filename, repo_name=repo_name, files_path=self.source_dir)

        with open(self.template_file) as template_file:
            self.template_html = template_file.read()

        self.apply_template()

    def build_left_sidebar(self, filename=None):
        html = '<div><h1>Revisions</h1><table width="100%" id="revisions"></table></div>'
        return html

    def build_right_sidebar(self, filename=None):
        html = self.build_page_nav(filename)
        return html

    def build_page_nav(self, filename=None):
        html = """
            <nav class="affix-top hidden-print hidden-xs hidden-sm" id="right-sidebar-nav">
              <ul id="sidebar-nav" class="nav nav-stacked affix">
                <li><h1>Navigation</h1></li>
            """
        for fname in self.files:
            with codecs.open(fname, 'r', 'utf-8-sig') as f:
                soup = BeautifulSoup(f, 'html.parser')
            if soup.find('h1'):
                title = soup.h1.text
            else:
                title = os.path.splitext(os.path.basename(fname))[0].replace('_', ' ').capitalize()
            if filename != fname:
                html += '<li><a href="{0}">{1}</a></li>'.format(os.path.basename(fname),title)
            else:
                html += '<li>{0}</li>'.format(title)
        html += """
                </ul>
            </nav>
            """
        return html

    def apply_template(self):
        language_code = self.manifest.target_language['id']
        language_name = self.manifest.target_language['name']
        resource_name = self.manifest.resource['name']

        heading = '{0}: {1}'.format(language_name, resource_name)
        title = ''
        canonical = ''

        # apply the template
        template = BeautifulSoup(self.template_html, 'html.parser')

        # find the target div in the template
        content_div = template.body.find('div', {'id': 'outer-content'})
        if not content_div:
            raise Exception('No div tag with id "outer-content" was found in the template')

        left_sidebar_div = template.body.find('div', {'id': 'left-sidebar'})
        if left_sidebar_div:
            left_sidebar_html = '<span>'+self.build_left_sidebar()+'</span>'
            left_sidebar_soup = BeautifulSoup(left_sidebar_html, 'html.parser')
            left_sidebar_div.clear()
            left_sidebar_div.append(left_sidebar_soup.span.contents[0])

        # loop through the html files
        for filename in self.files:
            if not self.quiet:
                print('Applying template to {0}.'.format(filename))

            # read the downloaded file into a dom abject
            with codecs.open(filename, 'r', 'utf-8-sig') as f:
                soup = BeautifulSoup(f, 'html.parser')

            # get the language code, if we haven't yet
            if not language_code:
                if 'lang' in soup.html:
                    language_code = soup.html['lang']
                else:
                    language_code = 'en'

            # get the title, if we haven't
            if not title and soup.head and soup.head.title:
                title = soup.head.title.text
            else:
                title = os.path.basename(filename)

            # get the canonical UTL, if we haven't
            if not canonical:
                links = template.head.select('link[rel="canonical"]')
                if len(links) == 1:
                    canonical = links[0]['href']

            if soup.body:
                body = soup.body
            else:
                body = soup

            # get the content div from the temp file
            soup_content = body.find('div', {'id': 'content'})
            if not soup_content:
                soup_content = body

            # insert new HTML into the template
            content_div.clear()
            content_div.append(soup_content)
            template.html['lang'] = language_code
            template.head.title.clear()
            template.head.title.append(heading+' - '+title)
            for a_tag in template.body.select('a[rel="dct:source"]'):
                a_tag.clear()
                a_tag.append(title)

            # set the page heading
            heading_span = template.body.find('span', {'id': 'h1'})
            heading_span.clear()
            heading_span.append(heading)

            right_sidebar_div = template.body.find('div', {'id': 'right-sidebar'})
            if right_sidebar_div:
                right_sidebar_html = '<span>'+self.build_right_sidebar(filename)+'</span>'
                right_sidebar_soup = BeautifulSoup(right_sidebar_html, 'html.parser')
                right_sidebar_div.clear()
                right_sidebar_div.append(right_sidebar_soup.span)

            # render the html as a string
            html = unicode(template)
            # update the canonical URL - it is in several different locations
            html = html.replace(canonical, canonical.replace('/templates/', '/{0}/'.format(language_code)))
            # write to output directory
            out_file = os.path.join(self.output_dir, os.path.basename(filename))
            if not self.quiet:
                print('Writing {0}.'.format(out_file))
            write_file(out_file, html.encode('ascii', 'xmlcharrefreplace'))


class ObsTemplater(Templater):
    def __init__(self, *args, **kwargs):
        super(ObsTemplater, self).__init__(*args, **kwargs)


class BibleTemplater(Templater):
    def __init__(self, *args, **kwargs):
        super(BibleTemplater, self).__init__(*args, **kwargs)

    def build_page_nav(self, filename=None):

        html = """
        <nav class="affix-top hidden-print hidden-xs hidden-sm" id="right-sidebar-nav">
            <ul id="sidebar-nav" class="nav nav-stacked books panel-group">
            """
        for fname in self.files:
            base = os.path.splitext(os.path.basename(fname))[0]
            (ch_num, ch_name) = base.split('-')
            with codecs.open(fname, 'r', 'utf-8-sig') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            if soup.find('h1'):
                title = soup.find('h1').text
            else:
                title = '{0}.'.format(ch_name)
            html += """
                <div class="panel panel-default">
                    <div class="panel-heading">
                        <h4 class="panel-title">
                            <a class="accordion-toggle" data-toggle="collapse" data-parent="#sidebar-nav" href="#collapse{0}">{1}</a>
                        </h4>
                    </div>
                    <div id="collapse{0}" class="panel-collapse collapse{2}">
                        <ul class="panel-body chapters">
                    """.format(ch_name, title, ' in' if fname == filename else '')
            for chapter in soup.find_all('h2', {'c-num'}):
                print(chapter['id'])
                html += """
                       <li class="chapter"><a href="{0}#{1}">{2}</a></li>
                    """.format(os.path.basename(fname) if fname != filename else '', chapter['id'],
                               chapter['id'].split('-')[1].lstrip('0'))
            html += """
                        </ul>
                    </div>
                </div>
                    """
        html += """
            </ul>
        </nav>
            """
        print(html)
        return html
