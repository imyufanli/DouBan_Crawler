# -*- coding: utf-8 -*-

"""
    DouBan Crawler
    ~~~~~~~~~~~~~~

    A DouBan Book web crawler.

    :Author: JustALee(https://github.com/JustALee).
"""


import requests
from bs4 import BeautifulSoup
import xlsxwriter


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/73.0.3683.103 Safari/537.36'
}


def get_page_obj(tag, pagination, order_by='T'):
    """
    :param tag: The name of the tag that you wish to search.
    :param pagination: The pagination of the search result.
    :param order_by: The order of the search result, use T by default.
    :return: A BeautifulSoup object of the specific tag and page.
    """
    t_url = 'https://book.douban.com/tag/%s' % tag
    start = (pagination-1)*20
    params = {
        'start': start,
        'type': order_by
    }
    markup = requests.get(t_url, params=params, headers=headers).text
    page_obj = BeautifulSoup(markup, 'lxml')
    return page_obj


def get_book_data(page_obj):
    """
    :param page_obj: The BeautifulSoup object of the page that you want to extract data from.
    :return: A generator with the crawled data.
    """
    book_list = page_obj.find('ul', class_='subject-list').find_all('div', class_='info')
    for book in book_list:
        title = book.h2.a.get_text(strip=True)
        # link = book.h2.a['href']
        pub_info = book.div.get_text(strip=True).split(' / ')
        # 事实上豆瓣上很多书籍的信息会有缺失，所以像这样按照位置确定数据类型的方式并不精准，
        # 要做到精确的方式就是进入每个图书的详情页面抓取数据，但这样的话工作量无疑也会大大增加
        author = '、'.join(pub_info[0:-3])
        publish_info = ' / '.join(pub_info[-3:])
        '''        try:
            publisher = pub_info[-3]
        except:
            # print('[-] Error: ' + title)
            publisher = ''
        try:
            publication_date = pub_info[-2]
        except:
            publication_date = ''
        try:
            price = pub_info[-1]
        except:
            price = ''
        '''
        star = book.find_all('div')[1]
        try:
            rating = star.find_all('span')[1].get_text(strip=True)
        except IndexError:
            print('[-] Error: Rating for 《%s》 is not available.' % title)
            rating = ''
        rating_num = get_rating_num(star.find_all('span')[-1].get_text(strip=True))
        try:
            description = book.p.get_text()
        except AttributeError:
            print('[-] Error: Description of the 《%s》 is not available.' % title)
            description = ''
        # yield [title, link, author, publish_info, rating, rating_num, description]
        yield [title, author, publish_info, rating, rating_num, description]
        print('[+] Successfully crawled: 《%s》.' % title)


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


def get_max_pagination(tag):
    """
    :param tag: The name of the tag that you wish to search.
    :return: The maximum pagination of the search result.
    """
    page_1 = get_page_obj(tag, pagination=1)
    # BeautifulSoup解析的数据会包含换行符，所以最大页的索引是-4
    max_pagination = int(page_1.find('div', class_='paginator').contents[-4].get_text())
    return max_pagination


def main(tag, filename):
    """
    :param tag: The name of the tag that you wish to search.
    :param filename: The filename of the workbook that you want to write data in.
    """
    with xlsxwriter.Workbook(filename) as workbook:
        worksheet = workbook.add_worksheet()
        header = (u'书名', u'作者/译者', u'出版信息', u'评分', u'评价人数', u'简介')
        worksheet.write_row(0, 0, header)
        row = 1
        max_pagination = get_max_pagination(tag)
        for pagination in range(1, max_pagination+1):
            page_obj = get_page_obj(tag, pagination)
            for book in get_book_data(page_obj):
                worksheet.write_row(row, 0, book)
                row += 1


if __name__ == '__main__':
    main('python', 'python_book.xlsx')
