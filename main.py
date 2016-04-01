# -*- coding: utf-8 -*-
from urllib import request, error
from bs4 import BeautifulSoup
import os

class URLReader():
    """
    Get HTML Page by URL
    """
    def __init__(self, url):
        self.url = url

    def get_page(self):
        data = 'Ничего не загружено'

        try:
            f = request.urlopen(self.url)
            encoding = f.headers.get_content_charset()
            data = f.read()
            data= data.decode(encoding)
        except error.HTTPError:
            print('Не удалось выполнить подключение')
        except error.URLError:
            print('Не удалось загрузить страницу - ', self.url)

        return data


class NParser():
    """
    Parsing HTML page, and make from it nice text
    """
    def __init__(self, data):
        self.data = data

    def digest(self):
        soup = BeautifulSoup(self.data)
        soup.script.replaceWith('')
        soup.head.replaceWith('')
        soup.html.replaceWith('')
        return soup.prettify()


class TXTMaker():
    """
    Write data to file
    """
    def __init__(self, data, path):
        self.data = data
        self.path = path

    def vivious_fertility(self):
        f = open(self.path, 'w')
        f.write(self.data)
        f.close()


def main():
    ureader = URLReader('http://zadolba.li/')
    np = NParser(ureader.get_page())
    txtmaker = TXTMaker(np.digest(), os.path.abspath(os.curdir))

if __name__ == '__main__':
    main()

