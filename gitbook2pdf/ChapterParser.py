import html
from urllib.parse import urljoin
from lxml import etree


class ChapterParser:
    def __init__(self, original, index_title, baselevel=0):
        self.head = ''
        self.heads = {'h1': 1, 'h2': 2, 'h3': 3, 'h4': 4, 'h5': 5, 'h6': 6}
        self.original = original
        self.baselevel = baselevel
        self.index_title = index_title

    def parser(self):
        tree = etree.HTML(self.original)
        if tree.xpath('//section[@class="normal markdown-section"]'):
            context = tree.xpath('//section[@class="normal markdown-section"]')[0]
        else:
            context = tree.xpath('//section[@class="normal"]')[0]
        if context.find('footer'):
            context.remove(context.find('footer'))
        context = self.parsehead(context)
        return html.unescape(etree.tostring(context, encoding='utf-8').decode())

    def parsehead(self, context):
        def level(num):
            return 'level' + str(num)

        for head in self.heads:
            if context.xpath(head):
                self.head = IndexParser.titleparse(context.xpath(head)[0])
                if self.head in self.index_title:
                    context.xpath(head)[0].text = self.index_title
                context.xpath(head)[0].attrib['class'] = level(self.baselevel)
                break
        return context


class IndexParser:
    def __init__(self, lis, start_url):
        self.lis = lis
        self.start_url = start_url

    @classmethod
    def titleparse(cls, li):
        children = li.getchildren()
        if len(children) != 0:
            firstchildren = children[0]
            primeval_title = ''.join(firstchildren.itertext())
            title = ' '.join(primeval_title.split())
        else:
            title = li.text
        return title

    def parse(self):
        found_urls = []
        content_urls = []
        for li in self.lis:
            element_class = li.attrib.get('class')
            if not element_class:
                continue
            if 'header' in element_class:
                title = self.titleparse(li)
                data_level = li.attrib.get('data-level')
                level = len(data_level.split('.')) if data_level else 1
                content_urls.append({
                    'url': "",
                    'level': level,
                    'title': title
                })
            elif "chapter" in element_class:
                data_level = li.attrib.get('data-level')
                level = len(data_level.split('.'))
                if 'data-path' in li.attrib:
                    data_path = li.attrib.get('data-path')
                    url = urljoin(self.start_url, data_path)
                    title = self.titleparse(li)
                    if url not in found_urls:
                        content_urls.append(
                            {
                                'url': url,
                                'level': level,
                                'title': title
                            }
                        )
                        found_urls.append(url)

                # Unclickable link
                else:
                    title = self.titleparse(li)
                    content_urls.append({
                        'url': "",
                        'level': level,
                        'title': title
                    })
        return content_urls
