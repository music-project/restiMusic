# -*- coding=UTF-8 -*-

import requests


def search(page, word):
    url = 'https://c.y.qq.com/soso/fcgi-bin/client_search_cp?cr=1&p=' + page + '&n=20&w=' + word
    r = requests.get(url)
    text = r.content[9:-1]
    return text

#
# if __name__ == '__main__':
#     search('1', '一生有你')