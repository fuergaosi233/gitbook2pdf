import sys
from gitbook2pdf import Gitbook2PDF
if __name__ == '__main__':
    url = sys.argv[1]
    Gitbook2PDF(url).run()
