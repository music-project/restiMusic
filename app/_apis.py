# -*- coding=UTF-8 -*-

from flask import Flask
from flask import request
import json
from spider.qqmusic import search


app = Flask(__name__)


@app.route('/test/test11/', methods=['GET'])
def test():
    return "just test"


@app.route('/api/search/', methods=['POST'])
def searchsong():
    """
    :function:  search songs
    :args:      none
    :rv         qqmusic spider function return value

    根据搜索词查询相关歌曲
    """

    if request.method == 'POST':
        page = request.form.get('page')
        word = request.form.get('word')

        info = eval(search(page, word))

        val = {}
        val['song'] = info['data']['song']
        keyword = ['albumname_hilight', 'alertid', 'belongCD', 'cdIdx', 'chinesesinger', 'docid', 'grp',
                   'interval', 'isonly', 'lyric', 'lyric_hilight', 'media_mid', 'msgid', 'newStatus', 'nt',
                   'pay', 'preview', 'pubtime', 'pure', 'size128', 'size320', 'sizeape', 'sizeflac', 'sizeogg',
                   'songname_hilight', 'strMediaMid', 'stream', 'switch', 't', 'tag', 'type', 'ver', 'vid']
        for song in val['song']['list']:
            for word in keyword:
                song.pop(word)
        return str(val)

@app.route('/api/play/', methods=['POST'])
def getm4a():
    """
    :function:  getm4a
    :args:      none
    :rv         the link to song`s m4a

    根据歌曲ID返回m4a播放链接
    """
    id = request.args.get('id')
    print id
    return 'http://ws.stream.qqmusic.qq.com/C100' + id + '.m4a?fromtag=38'


if __name__ == '__main__':
    app.run(debug=True)
    getm4a('just test')