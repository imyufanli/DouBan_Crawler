import requests


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/73.0.3683.103 Safari/537.36'
}


def get_page(tag):
    t_url = 'https://book.douban.com/tag/%s' % tag
    r = requests.get(t_url, headers=headers)
    print(r.text)


if __name__ == '__main__':
    get_page('python')
