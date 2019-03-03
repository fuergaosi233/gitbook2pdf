import html
import requests
from lxml import etree
from weasyprint import HTML, CSS
from urllib.parse import urljoin
import asyncio
import aiohttp
 
# brew install python3 cairo pango gdk-pixbuf libffi
proxies = {
    'http': 'socks5://127.0.0.1:1080',
    'https': 'socks5://127.0.0.1:1080'
}
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
}
BASE_URL = 'https://feisky.gitbooks.io/kubernetes/content/'

CONTENT_LIST = []


async def request(url, headers, timeout=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, timeout=timeout) as resp:
            return await resp.text()


async def get_request(url, headers, timeout=None):
    return requests.get(url, headers=headers, timeout=timeout).text


async def gettext(index, path):
    '''
    return path's html 
    '''

    global CONTENT_LIST

    url = urljoin(BASE_URL, path)
    print("crawling : ", url)
    try:
        metatext = await request(url, headers, timeout=10)
    except Exception as e:
        print("retrying : ", url)
        metatext = await request(url, headers)
    tree = etree.HTML(metatext)
    context = tree.xpath('//section[@class="normal markdown-section"]')[0]
    context.remove(context.find('footer'))
    text = etree.tostring(context).decode()
    CONTENT_LIST[index] = html.unescape(text)
    print("done : ", url)


def write_pdf(name, html_text, css_text):
    tmphtml = HTML(string=html_text)
    tmpcss = CSS(string=css_text)
    name += '.pdf'
    tmphtml.write_pdf(name, stylesheets=[tmpcss])


def get_all_css():
    '''
    return all css 
    '''
    # all_css = [
    #     BASE_URL+'gitbook/style.css',
    #     BASE_URL+'gitbook/gitbook-plugin-page-toc/page-toc.css',
    #     BASE_URL+'gitbook/gitbook-plugin-search-plus/search.css',
    #     BASE_URL+'gitbook/gitbook-plugin-tbfed-pagefooter/footer.css',
    #     BASE_URL+'gitbook/gitbook-plugin-comment/plugin.css',
    #     BASE_URL+'gitbook/gitbook-plugin-fontsettings/website.css',
    #     BASE_URL+'gitbook/gitbook-plugin-highlight/website.css',
    # ]
    # css_text=''
    # for _ in all_css:
    #     css_text+=requests.get(_,headers=header, proxies=proxies).text
    # return css_text
    with open('gitbook.css', 'r') as f:
        return f.read()


def collect_toc():
    text = requests.get(BASE_URL, headers=headers).text
    tree = etree.HTML(text)
    uls = tree.xpath('//ul[@class="summary"]/li')
    text_tree = {}
    tmp_title = 'header'

    content_urls = []

    for li in uls:
        element_class = li.attrib.get('class')
        if not element_class:
            continue
        if "header" in element_class:
            title = li.text
            text_tree[title] = {}
            tmp_title = title

        elif "chapter" in element_class:

            # 一级标题
            if len(li) == 1:
                level = li.attrib.get('data-level')
                data_path = li.attrib.get('data-path')
                # all_html += gettext(data_path)
                content_urls.append(data_path)
                text_tree[tmp_title][level] = data_path

            elif len(li) == 2:
                level = li.attrib.get('data-level')
                data_path = li.attrib.get('data-path')
                tmp_s = {'header': data_path}
                _lis = li.find('ul')

                if len(level.split(".")) == 2:
                    for _li in _lis:
                        lilevel = _li.attrib.get('data-level')
                        lidata_path = _li.attrib.get('data-path')
                        # all_html += gettext(lidata_path)
                        content_urls.append(lidata_path)
                        tmp_s[lilevel] = lidata_path
                text_tree[tmp_title][level] = tmp_s
    return text_tree, content_urls


async def main():
    global CONTENT_LIST
    text_tree, content_urls = collect_toc()
    CONTENT_LIST = [None for _ in range(len(content_urls))]

    tasks = []
    for index, url in enumerate(content_urls):
        tasks.append(
            gettext(index, url)
        )
    await asyncio.gather(*tasks)
    print("crawl : all done!")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()

    all_html = "".join(CONTENT_LIST)
    with open('demo.html', 'w', encoding='utf-8')as f:
        f.write(all_html)
    csstext = get_all_css()
    write_pdf("demo", all_html, csstext)
