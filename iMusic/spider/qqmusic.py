# -*- coding=UTF-8 -*-

import requests


def _search(page, word):
    url = 'https://c.y.qq.com/soso/fcgi-bin/client_search_cp?cr=1&p=' + page + '&n=20&w=' + word
    r = requests.get(url)
    text = r.content[9:-1]
    return text


def _songdetail(songid):
    url = 'https://c.y.qq.com/v8/fcg-bin/fcg_play_single_song.fcg?songmid=' + songid + '&tpl=' \
          'yqq_song_detail&format=jsonp&callback=getOneSongInfoCallback'
    r = requests.get(url)
    text = r.content[23:-1]
    return text

def _albumdetail(albumid):
    url = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_album_info_cp.fcg?albummid=' + albumid
    r = requests.get(url)
    # print(r.json())
    return r.json()


# if __name__ == '__main__':
#     play('000Md1wq0vnwzE')
#     search('1', '一生有你')