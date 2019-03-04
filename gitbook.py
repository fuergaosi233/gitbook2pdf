import html
import requests
import asyncio
import aiohttp
import weasyprint
import datetime
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from lxml import etree


async def request(url, headers, timeout=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, timeout=timeout) as resp:
            return await resp.text()


def local_ua_stylesheets(self):
    return [weasyprint.CSS('./html5_ua.css')]


def load_gitbook_css():
    with open('gitbook.css', 'r') as f:
        return f.read()


class HtmlGenerator():
    def __init__(self):
        self.html_start = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">      
"""

        self.title_ele = ""
        self.meta_list = []
        self.body = ""
        self.html_end = """
</body>
</html>
"""

    def add_meta_data(self, key, value):
        meta_string = "<meta name={key} content={value}>".format_map({
            'key': key,
            'value': value
        })
        self.meta_list.append(meta_string)

    def add_body(self, body):
        self.body = body

    def output(self):
        full_html = self.html_start + self.title_ele + "".join(self.meta_list) \
                    + "<body>" + self.body + self.html_end
        return full_html


class Gitbook2PDF():
    def __init__(self, base_url, fname=None):
        self.fname = fname
        self.base_url = base_url
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
        }
        self.content_list = []
        self.meta_list = []

        self.meta_list.append(
            ('generator', 'gitbook2pdf')
        )
        weasyprint.HTML._ua_stylesheets = local_ua_stylesheets

    def run(self):
        content_urls = self.collect_urls_and_metadata(self.base_url)
        content_urls = list(dict.fromkeys(content_urls))  # 去重
        self.content_list = ["" for _ in range(len(content_urls))]
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.crawl_main_content(content_urls))
        loop.close()

        # main body
        body = "".join(self.content_list)
        # 使用HtmlGenerator类来生成HTML
        html_g = HtmlGenerator()
        html_g.add_body(body)
        for key, value in self.meta_list:
            html_g.add_meta_data(key, value)
        html_text = html_g.output()
        css_text = load_gitbook_css()

        self.write_pdf(self.fname, html_text, css_text)

    async def crawl_main_content(self, content_urls):
        tasks = []
        for index, url in enumerate(content_urls):
            tasks.append(
                self.gettext(index, url)
            )
        await asyncio.gather(*tasks)
        print("crawl : all done!")

    async def gettext(self, index, url):
        '''
        return path's html
        '''

        print("crawling : ", url)
        try:
            metatext = await request(url, self.headers, timeout=10)
        except Exception as e:
            print("retrying : ", url)
            metatext = await request(url, self.headers)

        tree = etree.HTML(metatext)

        try:
            context = tree.xpath('//section[@class="normal markdown-section"]')[0]

            if context.find('footer'):
                context.remove(context.find('footer'))
            text = etree.tostring(context).decode()
            text = html.unescape(text)
            print("done : ", url)

            self.content_list[index] = text
        except IndexError:
            print('faild at : ', url, ' maybe content is empty?')

    def write_pdf(self, fname, html_text, css_text):
        tmphtml = weasyprint.HTML(string=html_text)
        tmpcss = weasyprint.CSS(string=css_text)
        fname = os.path.join(os.path.dirname(__file__), 'output', fname)
        tmphtml.write_pdf(fname, stylesheets=[tmpcss])

    def collect_urls_and_metadata(self, start_url):
        text = requests.get(start_url, headers=self.headers).text
        soup = BeautifulSoup(text, 'html.parser')

        # 如果不提供输出文件名的话，抓取html标题为文件名
        if not self.fname:
            title_ele = soup.find('title')
            if title_ele:
                title = title_ele.text
                if '·' in title:
                    title = title.split('·')[1]
                title = title.replace(' ', '')
                self.fname = title + '.pdf'
        self.meta_list.append(
            ('title', self.fname.replace('.pdf', ''))
        )

        # get description meta data
        comments_section = soup.find_all(class_='comments-section')
        if comments_section:
            description = comments_section[0].text.replace('\n', '').replace('\t', '')
            self.meta_list.append(
                ('description', description)
            )

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

        lis = soup.find('ul', class_='summary').find_all('li')
        content_urls = []
        for li in lis:
            element_class = li.attrs.get('class')
            if not element_class:
                continue
            if "chapter" in element_class:
                data_path = li.attrs.get('data-path')
                content_urls.append(
                    urljoin(start_url, data_path)
                )
        return content_urls


if __name__ == '__main__':
    Gitbook2PDF("https://eastlakeside.gitbooks.io/interpy-zh/content/").run()
