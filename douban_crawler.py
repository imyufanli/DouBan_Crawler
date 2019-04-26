import requests
from bs4 import BeautifulSoup


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/73.0.3683.103 Safari/537.36'
}


def get_page(tag, page, order='T'):
    t_url = 'https://book.douban.com/tag/%s' % tag
    start = (page-1)*20
    params = {
        'start': start,
        'type': order
    }
    r = requests.get(t_url, params=params, headers=headers).text
    return r


def get_book_data(r):
    bs_obj = BeautifulSoup(r, 'lxml')
    book_list = bs_obj.find('ul', class_='subject-list').find_all('div', class_='info')
    for book in book_list:
        title = book.h2.a.get_text(strip=True)
        link = book.h2.a['href']
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
        rating_num = get_rating_num(star.find_all('span')[-1].get_text(strip=True))
        try:
            description = book.p.get_text()
        except AttributeError:
            description = ''
        book_info = [title, link, author, publish_info, rating, rating_num, description]
        print('[+] Successfully crawled: 《%s》.' % title)
        # print(book_info)


def get_rating_num(data):
    if data == u'(少于10人评价)':
        rating_num = 0
    else:
        rating_num = data[1:-4]
    return rating_num


def main(tag):
    for page in range(1, 19):
        r = get_page(tag, page)
        get_book_data(r)


if __name__ == '__main__':
    main('python')
