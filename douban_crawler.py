import requests
from bs4 import BeautifulSoup
import xlsxwriter


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/73.0.3683.103 Safari/537.36'
}


def get_page_obj(tag, pagination, order_by='T'):
    t_url = 'https://book.douban.com/tag/%s' % tag
    start = (pagination-1)*20
    params = {
        'start': start,
        'type': order_by
    }
    page = requests.get(t_url, params=params, headers=headers).text
    page_obj = BeautifulSoup(page, 'lxml')
    return page_obj


def get_book_data(page_obj):
    book_list = page_obj.find('ul', class_='subject-list').find_all('div', class_='info')
    for book in book_list:
        title = book.h2.a.get_text(strip=True)
        # link = book.h2.a['href']
        pub_info = book.div.get_text(strip=True).split(' / ')
        try:
            author = '、'.join(pub_info[0:-3])
        except:
            # print('[-] Error: ' + title)
            author = ''
        try:
            publish_info = ' / '.join(pub_info[-3:])
        except:
            publish_info = ''
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
        except:
            # print('[-] Error: ' + title)
            rating = ''
        # rating_num = get_rating_num(star.find_all('span')[-1].get_text(strip=True))
        try:
            description = book.p.get_text()
        except AttributeError:
            description = ''
        # yield [title, link, author, publish_info, rating, rating_num, description]
        yield [title, author, publish_info, rating, description]
        print('[+] Successfully crawled: 《%s》.' % title)


def get_rating_num(data):
    if data == u'(少于10人评价)':
        rating_num = 0
    else:
        rating_num = data[1:-4]
    return rating_num


def get_max_pagination(tag):
    page_1 = get_page_obj(tag, pagination=1)
    max_pagination = int(page_1.find('div', class_='paginator').contents[-4].get_text())
    return max_pagination


def main(tag, filename):
    try:
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()
        header = (u'书名', u'作者/译者', u'出版信息', u'评分', u'简介')
        worksheet.write_row(0, 0, header)
        row = 1
        max_pagination = get_max_pagination(tag)
        for pagination in range(1, max_pagination+1):
            page_obj = get_page_obj(tag, pagination)
            for book in get_book_data(page_obj):
                worksheet.write_row(row, 0, book)
                row += 1
    finally:
        workbook.close()


if __name__ == '__main__':
    main('python', 'python_book.xlsx')
