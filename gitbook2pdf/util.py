import os

import aiohttp
import weasyprint

BASE_DIR = os.path.dirname(__file__)


async def request(url, headers, timeout=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, timeout=timeout) as resp:
            return await resp.text()


def local_ua_stylesheets(self):
    return [weasyprint.CSS(os.path.join(BASE_DIR, './libs/html5_ua.css'))]


# weasyprint's monkey patch for level
def load_gitbook_css():
    with open(os.path.join(BASE_DIR, './libs/gitbook.css'), 'r') as f:
        return f.read()


def get_level_class(num):
    """
    return 'level'+num
    """
    return 'level' + str(num)


def write_pdf(fname, html_text, css_text):
    tmphtml = weasyprint.HTML(string=html_text)
    tmpcss = weasyprint.CSS(string=css_text)
    fname = "./output/" + fname
    htmlname = fname.replace('.pdf', '.html')
    with open(htmlname, 'w', encoding='utf-8') as f:
        f.write(html_text)
    print('Generating pdf,please wait patiently')
    tmphtml.write_pdf(fname, stylesheets=[tmpcss])
    print('Generated')
