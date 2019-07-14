# -*- coding: utf-8 -*-

"""
    DouBan Crawler - OOP Version
    ~~~~~~~~~~~~~~

    A DouBan Book web crawler.

    :Author: JustALee(https://github.com/JustALee).
"""


import requests
from bs4 import BeautifulSoup
from xlsxwriter import Workbook


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/73.0.3683.103 Safari/537.36'
}


class Page(BeautifulSoup):
    """
    A Page Object, which is a subclass of BeautifulSoup.
    """

    def __init__(self, tag, pagination, order_by='T', **kwargs):
        """
        :param tag: The name of the tag that you wish to search.
        :param pagination: The pagination of the search result.
        :param order_by: The order of the search result, use T by default.
        :param kwargs: Will be pass to it's super class.
        """
        t_url = 'https://book.douban.com/tag/%s' % tag
        start = (pagination - 1) * 20
        params = {
            'start': start,
            'type': order_by
        }
        markup = requests.get(
            t_url, params=params, headers=headers).text
        super().__init__(markup, 'lxml', **kwargs)

    def get_books(self):
        """
        :return: A Generator which includes information of a book.
        """
        book_list = self.find('ul', class_='subject-list').find_all('div', class_='info')
        for book in book_list:
            title = book.h2.a.get_text(strip=True)
            pub_info = book.div.get_text(strip=True).split(' / ')
            author = '、'.join(pub_info[0:-3])
            publish_info = ' / '.join(pub_info[-3:])
            star = book.find_all('div')[1]
            try:
                rating = star.find_all('span')[1].get_text(strip=True)
            except IndexError:
                print('[-] Error: Rating for 《%s》 is not available.' % title)
                rating = ''
            rating_num = self.get_rating_num(
                star.find_all('span')[-1].get_text(strip=True)
            )
            try:
                description = book.p.get_text()
            except AttributeError:
                print('[-] Error: Description of the 《%s》 is not available.' % title)
                description = ''
            yield [title, author, publish_info, rating, rating_num, description]
            print('[+] Successfully crawled: 《%s》.' % title)

    @staticmethod
    def get_rating_num(data):
        """
        :param data: Raw string with the rating number.
        :return: Rating number in the raw string. Return 0 if it's less than 10.
        """
        if data == u'(少于10人评价)' \
                or data == u'(目前无人评价)':
            rating_num = 0
        else:
            rating_num = data[1:-4]
        return rating_num


class Crawler(object):
    """
    Main func of this module.
    """

    def __init__(self, tag):
        """
        :param tag: The name of the tag that you wish to search.
        """
        self.tag = tag
        self.max_pagination = self.get_max_pagination()

    def to_file(self, filename):
        """
        :param filename: The filename of the workbook that you want to write data in.
        """
        with Workbook(filename) as workbook:
            worksheet = workbook.add_worksheet()
            header = (u'书名', u'作者/译者', u'出版信息', u'评分', u'评价人数', u'简介')
            worksheet.write_row(0, 0, header)
            row = 1
            for pagination in range(1, self.max_pagination + 1):
                page = Page(self.tag, pagination)
                for book in page.get_books():
                    worksheet.write_row(row, 0, book)
                    row += 1

    def get_max_pagination(self):
        """
        :return: The maximum pagination of the search result.
        """
        page_1 = Page(self.tag, pagination=1)
        # BeautifulSoup解析的数据会包含换行符，所以最大页的索引是-4
        max_pagination = int(
            page_1.find('div', class_='paginator').contents[-4].get_text()
        )
        return max_pagination


if __name__ == '__main__':
    crawler = Crawler('python')
    crawler.to_file('python_book.xlsx')
