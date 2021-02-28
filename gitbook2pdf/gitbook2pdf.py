import asyncio
import datetime
import logging
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from .ChapterParser import *
from .HtmlGenerator import *
from .util import *

logging.basicConfig(level=logging.INFO)


class Gitbook2PDF:
    def __init__(self, base_url, fname=None):
        self.fname = fname
        self.base_url = base_url
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
        }
        self.content_list = []
        self.meta_list = []
        self.meta_list.append(('generator', 'gitbook2pdf'))
        weasyprint.HTML._ua_stylesheets = local_ua_stylesheets

    def run(self):
        content_urls = self.collect_urls_and_metadata(self.base_url)
        self.content_list = ["" for _ in range(len(content_urls))]

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.crawl_main_content(content_urls))
        loop.close()

        # main body
        body = "".join(self.content_list)
        # 使用HtmlGenerator类来生成HTML
        html_g = HtmlGenerator(self.base_url)
        html_g.add_body(body)
        for key, value in self.meta_list:
            html_g.add_meta_data(key, value)
        html_text = html_g.output()
        css_text = load_gitbook_css()

        write_pdf(self.fname, html_text, css_text)

    async def crawl_main_content(self, content_urls):
        tasks = []
        for index, urlobj in enumerate(content_urls):
            if urlobj['url']:
                tasks.append(self.gettext(index, urlobj['url'], urlobj['level'], urlobj['title']))
            else:
                tasks.append(self.getext_fake(index, urlobj['title'], urlobj['level']))
        await asyncio.gather(*tasks)
        logging.info("crawl : all done!")

    async def getext_fake(self, index, title, level):
        await asyncio.sleep(0.01)
        class_ = get_level_class(level)
        string = f"<h1 class='{class_}'>{title}</h1>"
        self.content_list[index] = string

    async def gettext(self, index, url, level, title):
        """
        return path's html
        """
        logging.info("crawling : " + url)

        try:
            metatext = await request(url, self.headers, timeout=10)
        except TimeoutError:
            logging.warning("retrying : " + url)
            metatext = await request(url, self.headers)
        try:
            text = ChapterParser(metatext, title, level, ).parser()
            logging.info("done : " + url)
            self.content_list[index] = text
        except IndexError:
            logging.error('faild at : ' + url + ' maybe content is empty?')

    def collect_urls_and_metadata(self, start_url):
        response = requests.get(start_url, headers=self.headers)
        self.base_url = response.url
        start_url = response.url
        text = response.text
        soup = BeautifulSoup(text, 'html.parser')

        # If the output file name is not provided, grab the html title as the file name.
        if not self.fname:
            title_ele = soup.find('title')
            if title_ele:
                title = title_ele.text
                if '·' in title:
                    title = title.split('·')[1]
                if '|' in title:
                    title = title.split('|')[1]
                title = title.replace(' ', '').replace('/', '-')
                self.fname = title + '.pdf'
        self.meta_list.append(('title', self.fname.replace('.pdf', '')))

        # get description meta data
        comments_section = soup.find_all(class_='comments-section')
        if comments_section:
            description = comments_section[0].text.replace('\n', '').replace('\t', '')
            self.meta_list.append(('description', description))
        else:
            pass

        # get author meta
        author_meta = soup.find('meta', {'name': 'author'})
        if author_meta:
            author = author_meta.attrs['content']
        else:
            author = urlparse(self.base_url).netloc
        self.meta_list.append(
            ('author', author)
        )

        # creation date and modification date : default now
        # see : https://www.w3.org/TR/NOTE-datetime
        now = datetime.datetime.utcnow().replace(microsecond=0).isoformat()
        self.meta_list.append(('dcterms.created', now))
        self.meta_list.append(('dcterms.modified', now))
        lis = etree.HTML(text).xpath("//ul[@class='summary']//li")
        return IndexParser(lis, start_url).parse()
