import argparse
from gitbook2pdf import Gitbook2PDF

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", '--url', type=str, help='the gitbook url')
    args = parser.parse_args()
    Gitbook2PDF(args.url).run()
