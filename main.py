# -*- coding: utf-8 -*-
from urllib import request, error
from bs4 import BeautifulSoup
import re
import os
import codecs
import json
import sys


class ConfigReader:

    def __init__(self, path, domain):
        self.path = path
        self.domain = domain

    def open_config(self):
        f = open(self.path)
        config = json.load(f)
        f.close()
        try:
            curconf = config[self.domain]
            parent_tag = curconf['parent']['tag']
            attrs = curconf['parent']['attrs'].split(':')
            try:
                parent_attrs = {attrs[0]: attrs[1]}
            except IndexError:
                parent_attrs = {}

            title_tag = curconf['title']['tag']
            attrs = curconf['title']['attrs'].split(':')
            try:
                title_attrs = {attrs[0]: attrs[1]}
            except IndexError:
                title_attrs = {}

            text_tag = curconf['text']['tag']
            attrs = curconf['text']['attrs'].split(':')
            try:
                text_attrs = {attrs[0]: attrs[1]}
            except IndexError:
                text_attrs = {}

            spell = {
                'parent': {
                    'tag': parent_tag,
                    'attrs': parent_attrs,
                },
                'title': {
                    'tag': title_tag,
                    'attrs': title_attrs,
                },
                'text': {
                    'tag': text_tag,
                    'attrs': text_attrs,
                }}
            return spell

        except KeyError:
            spell = {
                'parent': {
                    'tag': 'body',
                    'attrs': {},
                },
                'title': {
                    'tag': 'h1',
                    'attrs': {},
                },
                'text': {
                    'tag': 'div',
                    'attrs': {},
                }}
            return spell





class URLReader:
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
            data = data.decode(encoding)
        except error.HTTPError:
            print('Не удалось выполнить подключение')
        except error.URLError:
            print('Не удалось загрузить страницу проверьте url- ', self.url)

        return data


class NParser:
    """
    Parsing HTML page, and make from it nice text
    """
    def __init__(self, data, spell):
        self.data = data
        self.parent_tag = spell['parent']['tag']
        self.parent_attrs = spell['parent']['attrs']
        self.title_tag = spell['title']['tag']
        self.title_attrs = spell['title']['attrs']
        self.text_tag = spell['text']['tag']
        self.text_attrs = spell['text']['attrs']

    def digest(self):
        soup = BeautifulSoup(self.data, "html.parser")
        output_string = ''
        if self.parent_attrs != {}:
            source = soup.find_all(name=self.parent_tag, attrs=self.parent_attrs)
        else:
            source = soup.find_all(name=self.parent_tag)
        for elem in source:
            try:
                if self.title_attrs != {}:
                    title = elem.find(name=self.title_tag, attrs=self.title_attrs)
                else:
                    title = elem.find(name=self.title_tag)
                output_string += '\t{0}\n\n'.format(title.contents[0])
            except AttributeError:
                print("Проверьте настройки для данного сайта {0}".format(get_domain(sys.argv[1])))
                break

            if self.text_attrs != {}:
                text = elem.find(name=self.text_tag, attrs=self.text_attrs)
            else:
                text = elem.find(name=self.text_tag)

            ps = text.find_all(name='p')
            for p in ps:
                links = p.find_all('a')
                for l in links:
                    l.replaceWith('{1}:[{0}] '.format(l.attrs['href'], l.string))
                words = p.get_text().split(' ')
                t = type(p)
                line_str = ''
                for word in words:
                    if len(line_str) + len(word) <= 80:
                        line_str += '{0} '.format(word)
                    else:
                        output_string += '{0}\n'.format(line_str)
                        line_str = '{0} '.format(word)
                output_string += '{0}\n\n'.format(line_str)
            output_string += '\n\n'
        output_string = output_string.replace('<a href="', '[')
        output_string = output_string.replace('">', ']')
        output_string = output_string.replace('</a>', '')
        return output_string


class TXTMaker:
    """
    Write data to file
    """
    def __init__(self, data, path):
        self.data = data
        self.path = path

    def make_path(self):
        trash = re.compile(r'https?://')
        self.path = re.sub(trash,'/', self.path)
        path_parts = self.path.split('/')
        if len(path_parts[-1]) is 0:
            self.path += 'page'
        dir_path = os.getcwd() + '/'.join(path_parts[0:-1])
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    def vicious_fertility(self):
        self.make_path()
        with codecs.open(os.getcwd() + self.path + '.txt', 'w', 'utf-8') as f:
            f.write(self.data)


def get_domain(url):
    r_e = re.compile(r'https?://(w{0,3}\.*)(\w+\.\w.)(.*)')
    data = re.match(r_e, url)
    if data.groups()[2] == '':
        print('Необходимо указать полный путь к статье, а не главную страницу сайта')
        exit()
    else:
        return data.groups()[1]


def main():
    r_e = re.compile(r'https?://(w{0,3}\.*)(\w+\.\w.)(.*)')
    if re.match(r_e, sys.argv[1]):
        url = sys.argv[1]
    else:
        print('Необходимо указать url сайта! {0} - не url'.format(sys.argv[1]))
        exit()

    ureader = URLReader(url)
    config = ConfigReader(os.path.join(os.path.abspath(os.curdir), 'config.json'), get_domain(url))
    np = NParser(ureader.get_page(), config.open_config())
    txtmaker = TXTMaker(np.digest(), url)
    txtmaker.vicious_fertility()

if __name__ == '__main__':
    main()

